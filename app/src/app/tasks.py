from celery import Celery, chain, group
from celery.utils.log import get_task_logger
from celery.contrib.abortable import AbortableTask

from app.tasks_impl import (run_app_schedule_impl, start_workflow_impl, processor,
    retrieve_new_filemaker_data_incremental, create_examinations, aggregate_patients, poll_sequencer_output)

from app.db import DB
from app.config import CONFIG
from app.filemaker_api import Filemaker
#import app.app
from functools import wraps

logger = get_task_logger(__name__)

# importantly, the config needs to be updated through the cli in app.py
mq = Celery('ngs_pipeline')


@mq.task
def run_schedule():
    db = DB.from_config(CONFIG)
    run_app_schedule_impl(db, CONFIG)


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
    db = DB.from_config(CONFIG)
    filemaker = Filemaker.from_config(CONFIG)
    retrieve_new_filemaker_data_incremental(db, filemaker, processor, backoff_time=5)
    create_examinations(db, CONFIG)
    aggregate_patients(db, CONFIG)


@mq.task
def sync_sequencer_output():
    db = DB.from_config(CONFIG)
    poll_sequencer_output(db, CONFIG)


@mq.task(bind=True, base=AbortableTask)
# self because its an abortable task
# aborting doesnt work yet
def start_workflow(self, workflow_inputs, panel_type):
    db = DB.from_config(CONFIG)
    start_workflow_impl(self.is_aborted, db, CONFIG, workflow_inputs, panel_type)


@mq.task
def start_pipeline(*args):
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


