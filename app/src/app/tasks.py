from celery import Celery, chain, group
from celery.utils.log import get_task_logger
from celery.contrib.abortable import AbortableTask

from app.tasks_impl import (run_app_schedule_impl, start_workflow_impl, processor,
    retrieve_new_filemaker_data_incremental, create_examinations, aggregate_patients, poll_sequencer_output)
from app.config import Config

from app.db import DB
from app.filemaker_api import Filemaker
import app.app

logger = get_task_logger(__name__)

config = Config().dict()

mq = Celery('ngs_pipeline', 
        **Config().celery_config()
        )


@mq.task
def run_schedule(config):
    db = DB.from_config(config)
    run_app_schedule_impl(db, config)


@mq.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    #sig = start_pipeline.signature(args=(config,))
    sig = run_schedule.signature(args=(config,))
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
def sync_couchdb_to_filemaker(config):
    db = DB.from_config(config)
    filemaker = Filemaker.from_config(config)

    retrieve_new_filemaker_data_incremental(db, filemaker, processor, backoff_time=5)
    create_examinations(db, config)
    aggregate_patients(db, config)


@mq.task
def sync_sequencer_output(config):
    db = DB.from_config(config)
    poll_sequencer_output(db, config)


@mq.task(bind=True, base=AbortableTask)
# self because its an abortable task
# aborting doesnt work yet
def start_workflow(self, config, workflow_inputs, panel_type):
    db = DB.from_config(config)

    start_workflow_impl(self.is_aborted, db, config, workflow_inputs, panel_type)


@mq.task
def start_pipeline(config):
    '''
    this loads the sequencer output files into the database
    compares if every sequencer run has an according pipeline run by the folder path

    if not, it runs the pipeline for the missing ones
    sync_couchdb_to_filemaker
    new_examinations = collect_work()



    db = DB.from_config(config)
    start_workflow_tasks = app_start_pipeline(db, config)
    return

    tasks = []
    for task_args in start_workflow_tasks:
        signature = start_panel_workflow.s(*task_args)
        tasks.append(signature)

    lazy_group = group(tasks)
    promise = lazy_group.apply_async()

    return promise
    '''


