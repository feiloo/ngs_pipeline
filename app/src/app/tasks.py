from celery import Celery, chain, group
from celery.utils.log import get_task_logger
from celery.contrib.abortable import AbortableTask

from app.model import filemaker_examination_types
from app.tasks_impl import (run_app_schedule_impl, start_workflow_impl, processor,
    retrieve_new_filemaker_data_incremental, create_examinations, aggregate_patients, 
    poll_sequencer_output, collect_work, get_samples_of_examination)

from app.db import DB
from app.config import CONFIG
from app.filemaker_api import Filemaker
#import app.app
from functools import wraps

logger = get_task_logger(__name__)

# importantly, the config needs to be updated through the cli in app.py
mq = Celery('ngs_pipeline')
db = DB

@mq.task
def run_schedule():
    run_app_schedule_impl()


@mq.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    #sig = start_pipeline.signature(args=(config,))
    sig = run_schedule.signature(args=[])
    sender.add_periodic_task(10.0, sig, name='check for dynamically scheduled tasks')

    # sender.add_periodic_task(300.0, sig, name='sync filemaker to couchdb')
    # Executes every day at midnight
    '''
    sender.add_periodic_task(
        crontab(hour=0, minute=0, day_of_week='*'),
        #test.s('Happy Mondays!'),

    )
    '''


@mq.task
def sync_couchdb_to_filemaker():
    filemaker = Filemaker.from_config(CONFIG)
    retrieve_new_filemaker_data_incremental(filemaker, processor, backoff_time=5)
    create_examinations()
    aggregate_patients()


@mq.task
def sync_sequencer_output():
    poll_sequencer_output()


@mq.task(bind=True, base=AbortableTask)
# self because its an abortable task
# aborting doesnt work yet
def start_workflow(self, workflow_inputs, panel_type):
    start_workflow_impl(self.is_aborted, workflow_inputs, panel_type)


@mq.task
def start_pipeline(*args):
    '''
    this loads the sequencer output files into the database
    compares if every sequencer run has an according pipeline run by the folder path

    if not, it runs the pipeline for the missing ones
    '''

    panel_types = set()

    for e in db.query('examinations/types').to_wrapped().values():
        panel_types.add(e.examinationtype)

    #logger.info(f'examinationtypes: {panel_types}')
    #logger.info(f'examinationtypes count: {len(panel_types)}')
    #return

    #sync_couchdb_to_filemaker()
    sync_sequencer_output()
    groups = collect_work()

    #logger.info(groups[-2:])

    work = {}

    for panel in panel_types: #filemaker_examination_types:
        if panel not in groups:
            continue

        examinations = groups[panel]
        work[panel] = []
        logger.info(f"number of new examinations: {len(examinations)}")

        for e in examinations:
            try:
                ex_samples = get_samples_of_examination(e)
                logger.info(f'samples of examination are {ex_samples}')
                if len(ex_samples) > 1:
                    for exs in ex_samples:
                        work[panel] = work[panel] + [(e.id, str(exs))]
                    logger.error(f'more than one sample found for new_examination: {e}')
                elif len(ex_samples) == 0:
                    logger.info(f'no sample found yet for new_examination: {e}')
                else:
                    work[panel] = work[panel] + [(e.id, str(ex_samples[0]))]
            except Exception as exc:
                logger.error(f'cant obtain sample of examination: {exc} cause of {e}')

    logger.info(f'collected the work: {work}')
    logger.info(f'work: {work}')

    tasks = []
    for panel in work.keys():
        workflow_inputs = work[panel]
        if len(workflow_inputs) == 0:
            continue
        signature = start_workflow.s(workflow_inputs, panel)
        tasks.append(signature)

    lazy_group = group(tasks)
    promise = lazy_group.apply_async()

    return promise


    #plan_pipeline_runs()
    #run_pipeline_runs()
