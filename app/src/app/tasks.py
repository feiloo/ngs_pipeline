from celery import Celery, chain, group
from celery.utils.log import get_task_logger
from celery.contrib.abortable import AbortableTask

from app.tasks_impl import app_schedule, app_start_pipeline, start_panel_workflow_impl
from app.config import Config

# for sigint
import signal

logger = get_task_logger(__name__)

config = Config().dict()

mq = Celery('ngs_pipeline', 
        **Config().celery_config()
        )

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


def transform_data(config):
    #create_examinations(config)
    aggregate_patients(config)


@mq.task
def sync_couchdb_to_filemaker(config):
    #retrieve_new_filemaker_data_incremental(config)
    transform_data(config)



@mq.task
def start_pipeline(config):
    '''
    this loads the sequencer output files into the database
    compares if every sequencer run has an according pipeline run by the folder path

    if not, it runs the pipeline for the missing ones
    '''
    start_workflow_tasks = app_start_pipeline(config)

    tasks = []
    for start_workflow_task in start_panel_workflow_tasks:
        signature = start_panel_workflow.s(*task_args)

    lazy_group = group(tasks)
    promise = lazy_group.apply_async()

    return promise



@mq.task
def run_schedule(config):
    app_schedule(config)

@mq.task(bind=True, base=AbortableTask)
# self because its an abortable task
# aborting doesnt work yet
def start_panel_workflow(self, config, workflow_inputs, panel_type, sequencer_run_path):
    start_panel_workflow_impl(self, config, workflow_inputs, panel_type, sequencer_run_path)
