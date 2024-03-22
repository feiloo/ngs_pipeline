from celery import Celery, chain, group
rom celery.utils.log import get_task_logger
from celery.contrib.abortable import AbortableTask

from app.tasks_utils import Schedule
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
    sig = run_schedule.signature(args=[])
    sender.add_periodic_task(10.0, sig, name='check for dynamically scheduled tasks')


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
def start_workflow_single(self, args):
    return_code = start_single_workflow(self.is_aborted, args)
    return return_code


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

    sync_couchdb_to_filemaker()
    sync_sequencer_output()
    groups = collect_work()
    work = {}

    for panel in panel_types:
        if panel not in groups:
            continue

        examinations = groups[panel]
        work[panel] = []
        logger.info(f"number of new examinations: {len(examinations)}")

        for e in examinations:
            try:
                ex_samples = list(sorted(get_samples_of_examination(e)))
                logger.info(f'samples of examination are {ex_samples}')
                c = len(ex_samples)
                if c == 2:
                    work[panel] = work[panel] + [(e.id, (str(ex_samples[0]), str(ex_samples[1])))]
                else:
                    raise RuntimeError('invalid number of samples {c}')
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


def run_app_schedule_impl():
    schedule = Schedule(db)
    schedule.acquire_lock()

    try:
        if schedule.is_enabled() and schedule.has_work_now():
            s1 = sync_couchdb_to_filemaker.s()
            s2 = start_pipeline.s()
            res = chain(s1, s2)
            res.apply_async()
    finally:
        schedule.release_lock()
