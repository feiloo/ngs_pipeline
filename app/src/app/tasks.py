from celery import Celery, chain
import pycouchdb as couch
from pathlib import Path
from datetime import datetime
import subprocess
import json
import tempfile
import logging

logger = logging.getLogger(__name__)

import time

from app.parsers import parse_fastq_name, parse_miseq_run_name

testconfig = {'couchdb_user':'testuser',
        'couchdb_psw':'testpsw',
        'rabbitmq_user':'testuser',
        'rabbitmq_psw':'testpsw',
        'miseq_output_folder':'/data/private_testdata/miseq_output_testdata',
        "dev":'true'
        }

config = testconfig

backend_url = f'couchdb://{config["couchdb_user"]}:{config["couchdb_psw"]}@localhost:8001/pipeline_results' 
broker_url = f'pyamqp://{config["rabbitmq_user"]}:{config["rabbitmq_psw"]}@localhost//'
mq = Celery('ngs_pipeline', 
        backend=backend_url,
        broker=broker_url
        )


def get_db(url):
    server = couch.Server(url)
    app_db = server.database('ngs_app')
    return app_db


@mq.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sig = start_pipeline.signature(args=(config,))
    sender.add_periodic_task(300.0, sig, name='start pipeline every 300s')

    # Executes every day at midnight
    '''
    sender.add_periodic_task(
        crontab(hour=0, minute=0, day_of_week='*'),
        test.s('Happy Mondays!'),
    )
    '''

@mq.task
def poll_sequencer_output(app_db, config):
    # first, sync db with miseq output data
    miseq_output_path = Path(config['miseq_output_folder'])
    miseq_output_runs = [miseq_output_path / x for x in miseq_output_path.iterdir()]

    for run_name in miseq_output_runs:
        try:
            parsed = parse_miseq_run_name(run_name.name)
            dirty=False
        except RuntimeError as e:
            parsed = {}
            dirty=True

        # run folder name doesnt adhere to illumina naming convention
        # because it has been renamed or manually copied
        # we save the parsed information too, so we can efficiently query the runs
        run_document = {
                'document_type':'sequencer_run',
                'original_path':str(run_name), 
                'name_dirty':str(dirty), 
                'parsed':parsed, 
                'indexed_time':str(datetime.now())
                }
        #runs.append(run_document)
        app_db.save(run_document)

def poll_filemaker_data():
    # poll recent filemaker data
    pass

def get_db_url(config):
    user = config['couchdb_user']
    psw = config['couchdb_psw']
    host = 'localhost'
    port = 8001
    url = f"http://{user}:{psw}@{host}:{port}"
    return url

@mq.task
def start_pipeline(config):
    app_db = get_db(get_db_url(config))

    poll_sequencer_output(app_db, config)
    #poll_filemaker_data()
    miseq_output_folder = config['miseq_output_folder']
    db_runs = app_db.query('sequencer_runs/all')
    known_runs = set()#set([str(Path(r['key']['original_path']).name) for r in db_runs])
    miseq_runs = set([str(Path(r).name) for r in Path(miseq_output_folder).iterdir()])
    new_runs = miseq_runs - known_runs

    if len(new_runs) == 0:
        return

    workflow_inputs = []
    
    for new_run in new_runs:
        for sample_path in (Path(miseq_output_folder) / new_run).rglob('*.fastq.gz'):
            workflow_inputs.append(sample_path)

    workflow = '/data/ngs_pipeline/workflow/wdl/test.wdl'

    pipeline_run = {
            'document_type':'pipeline_run',
            'created_time':str(datetime.now()),
            'input_samples': [str(x) for x in workflow_inputs],
            'workflow': workflow,
            'status': 'running',
            'logs': {
                'stderr': [],
                'stdout': [],
                }
            }
    pipeline_run = app_db.save(pipeline_run)

    #workflow = '/data/ngs_pipeline/workflow/wdl/ngs_pipeline.wdl'
    output_dir = '/data/fhoelsch/wdl_out'

    # we write to tempfile, even though there is an output log file in the wdl output directory, 
    # because elsewhere we dont know the run name
    # this will be fixed in future, for example by naming the runs

    with tempfile.TemporaryFile() as stde:
        with tempfile.TemporaryFile() as stdo:
            pipeline_proc = subprocess.Popen(
                    ['miniwdl', 'run', '--dir', output_dir, workflow] + [f'files={i}' for i in workflow_inputs],
                    stdout=stde, #subprocess.PIPE, 
                    stderr=stdo, #subprocess.PIPE
                    #capture_output=True
                    )

            # update db entry every second when the process runs
            while pipeline_proc.poll() is None:
                stde.seek(0)
                stdo.seek(0)
                pipeline_run['logs']['stderr'] = stde.read().decode('utf-8')
                pipeline_run['logs']['stdout'] = stdo.read().decode('utf-8')

                pipeline_run = app_db.save(pipeline_run)
                time.sleep(1)

            # update db entry at the end
            stde.seek(0)
            stdo.seek(0)
            pipeline_run['logs']['stderr'] = stde.read().decode('utf-8')
            pipeline_run['logs']['stdout'] = stdo.read().decode('utf-8')
            retcode = proc.returncode
            if retcode == 0:
                pipeline_run['status'] = 'successful'
            else:
                pipeline_run['status'] = 'error'
            pipeline_run = app_db.save(pipeline_run)
