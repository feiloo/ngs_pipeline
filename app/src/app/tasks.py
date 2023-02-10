from celery import Celery, chain
import pycouchdb as couch
from pathlib import Path
from datetime import datetime
import subprocess
import json
import tempfile
import logging
import time
import json

logger = logging.getLogger(__name__)

from app.parsers import parse_fastq_name, parse_miseq_run_name
from app.model import SequencerRun, PipelineRun

from app.constants import testconfig
from app.filemaker_api import Filemaker


def get_celery_config(config):
    celery_config = { 
      'backend_url': f'couchdb://{config["couchdb_user"]}:{config["couchdb_psw"]}@localhost:8001/pipeline_results',
      'broker_url': f'pyamqp://{config["rabbitmq_user"]}:{config["rabbitmq_psw"]}@localhost//'
    }
    return celery_config

celery_config = get_celery_config(testconfig)

mq = Celery('ngs_pipeline', 
        **celery_config
        )


with open('/etc/ngs_pipeline_config.json', 'r') as f:
    config = json.loads(f.read())

assert 'filemaker_server' in config
assert 'filemaker_user' in config
assert 'filemaker_psw' in config

filemaker = Filemaker(
        config['filemaker_server'], 
        config['filemaker_user'], 
        config['filemaker_psw'])

def get_db(url):
    server = couch.Server(url)
    app_db = server.database('ngs_app')
    return app_db

@mq.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sig = start_pipeline.signature(args=(config,))
    sender.add_periodic_task(300.0, sig, name='start pipeline every 300s')

    #sender.add_periodic_task(300.0, sig, name='sync filemaker to couchdb')
    # Executes every day at midnight
    '''
    sender.add_periodic_task(
        crontab(hour=0, minute=0, day_of_week='*'),
        test.s('Happy Mondays!'),
    )
    '''


@mq.task
def sync_couchdb_to_filemaker(config):
    app_db = get_db(get_db_url(config))

    for i in range(2):
        # backoff for a few seconds
        time.sleep(5)
        resp = filemaker.get_all_records(offset=i*1000+1)
        print(resp)
        recs = resp['data']
        print('s couch', len(recs))
        for i,r in enumerate(recs):
            d = r['fieldData']
            d['document_type']='filemaker_record'
            app_db.save(d)
            print(f"saved {i}")
    

@mq.task
def poll_sequencer_output(app_db, config):
    # first, sync db with miseq output data
    sequencer_runs = list(app_db.query('sequencer_runs/all'))
    sequencer_paths = [str(r['key']['original_path']) for r in sequencer_runs]

    miseq_output_path = Path(config['miseq_output_folder'])
    miseq_output_runs = [miseq_output_path / x for x in miseq_output_path.iterdir()]

    for run_name in miseq_output_runs:
        try:
            parsed = parse_miseq_run_name(run_name.name)
            dirty=False
        except RuntimeError as e:
            parsed = {}
            dirty=True

        #panel_type = infer_panel_type(samplesheet)

        # run folder name doesnt adhere to illumina naming convention
        # because it has been renamed or manually copied
        # we save the parsed information too, so we can efficiently query the runs

        if str(run_name) in sequencer_paths:
            continue

        run_document = {
                'document_type':'sequencer_run',
                'original_path':Path(run_name), 
                'name_dirty':str(dirty), 
                'parsed':parsed, 
                'state': 'successful',
                'panel_type': 'unset', 
                'indexed_time':datetime.now()
                }

        sequencer_run = SequencerRun(**run_document)
        #runs.append(run_document)
        app_db.save(json.loads(sequencer_run.json()))


def get_db_url(config):
    user = config['couchdb_user']
    psw = config['couchdb_psw']
    host = 'localhost'
    port = 5984
    url = f"http://{user}:{psw}@{host}:{port}"
    return url

def get_mp_number_from_path(p):
    d = parse_fastq_name(Path(p).name)
    return d['sample_name']


def start_run(config, workflow_inputs, panel_type, sequencer_run_path):
    app_db = get_db(get_db_url(config))

    workflows = {
        'NGS DNA Lungenpanel': '/data/ngs_pipeline/workflow/wdl/test.wdl',
        'NGS oncoHS' : '/data/ngs_pipeline/workflow/wdl/test.wdl',
        'NGS BRCAness': '/data/ngs_pipeline/workflow/wdl/test.wdl',
        'NGS RNA Sarkom': '/data/ngs_pipeline/workflow/wdl/test.wdl',
        'NGS RNA Fusion Lunge': '/data/ngs_pipeline/workflow/wdl/test.wdl',
        'NGS PanCancer': '/data/ngs_pipeline/workflow/wdl/test.wdl',
        }

    #workflow = '/data/ngs_pipeline/workflow/wdl/test.wdl'
    #workflow = '/data/ngs_pipeline/workflow/wdl/clc_test.wdl'
    #workflow = '/data/ngs_pipeline/workflow/wdl/ngs_pipeline.wdl'

    if panel_type == 'unset':
        print('info, panel type not set, skipping')
        return

    workflow = workflows[panel_type]

    pipeline_document = {
            'document_type':'pipeline_run',
            'created_time':str(datetime.now()),
            'input_samples': [str(x) for x in workflow_inputs],
            'sequencer_run': Path(sequencer_run_path),
            'workflow': workflow,
            'status': 'running',
            'logs': {
                'stderr': '',
                'stdout': '',
                }
            }

    pipeline_run = PipelineRun(
            created_time=datetime.now(),
            input_samples=[str(x) for x in workflow_inputs],
            sequencer_run=Path(sequencer_run_path),
            workflow=workflow,
            status='running',
            logs={
                'stderr': '',
                'stdout': '',
                }
            )

    def db_save(pipeline_run):
        pr = app_db.save(pipeline_run.to_dict())
        return pipeline_run.from_dict(pr)
        

    pipeline_run = db_save(pipeline_run)

    try:
        output_dir = '/data/fhoelsch/wdl_out'

        # we write to tempfile, even though there is an output log file in the wdl output directory, 
        # because elsewhere we dont know the run name
        # this will be fixed in future, for example by naming the runs

        with tempfile.TemporaryFile() as stde:
            with tempfile.TemporaryFile() as stdo:
                clc_host = config['clc_host']
                clc_user = config['clc_user']
                clc_psw = config['clc_psw']

                cmd = ['miniwdl', 'run', 
                        '--env', f'CLC_HOST={clc_host}', 
                        '--env', f"CLC_USER={clc_user}", 
                        '--env', f'CLC_PSW={clc_psw}', 
                        '--dir', output_dir, 
                        workflow
                        ] + [f'files={i}' for i in workflow_inputs]

                pipeline_proc = subprocess.Popen(
                        cmd,
                        stdout=stde, #subprocess.PIPE, 
                        stderr=stdo, #subprocess.PIPE
                        #capture_output=True
                        )

                # update db entry every second when the process runs
                while pipeline_proc.poll() is None:
                    stde.seek(0)
                    stdo.seek(0)
                    pipeline_run.logs.stderr = stde.read().decode('utf-8')
                    pipeline_run.logs.stdout = stdo.read().decode('utf-8')

                    pipeline_run = db_save(pipeline_run)
                    time.sleep(1)

                # update db entry at the end
                stde.seek(0)
                stdo.seek(0)
                pipeline_run.logs.stderr = stde.read().decode('utf-8')
                pipeline_run.logs.stdout = stdo.read().decode('utf-8')

                retcode = pipeline_proc.returncode
                if retcode == 0:
                    pipeline_run.status = 'successful'
                else:
                    pipeline_run.status = 'error'

                pipeline_run = db_save(pipeline_run)

    except Exception as e:
        print(e)
        pipeline_document['status'] = 'error'
        pipeline_document = db_save(pipeline_document)


@mq.task
def start_pipeline(config):
    app_db = get_db(get_db_url(config))

    poll_sequencer_output(app_db, config)

    miseq_output_folder = config['miseq_output_folder']

    sequencer_runs = list(app_db.query('sequencer_runs/all'))
    pipeline_runs = list(app_db.query('pipeline_runs/all'))

    sequencer_run_ids = set([str(Path(r['key']['original_path']).name) for r in sequencer_runs])
    pipeline_run_refs = set([str(Path(r['key']['sequencer_run']).name) for r in pipeline_runs])

    new_run_ids = sequencer_run_ids - pipeline_run_refs

    new_runs = list(filter(
        lambda x: str(Path(x['key']['original_path']).name) in new_run_ids, 
        sequencer_runs)
        )

    if len(new_runs) == 0:
        print('no new runs')
        return

    for new_run in new_runs:
        if new_run['key']['state'] != 'successful':
            continue

        workflow_inputs = []
        mp_numbers = []

        for sample_path in (Path(miseq_output_folder) / Path(new_run['key']['original_path']).name).rglob('*.fastq.gz'):
            try:
                #mp_numbers.append(get_mp_number_from_path(str(sample_path)))
                workflow_inputs.append(sample_path)
            except Exception as e:
                print(f'error: {e}')
        
        start_run(config, workflow_inputs, new_run['key']['panel_type'], new_run['key']['original_path'])
