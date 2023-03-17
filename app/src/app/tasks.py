from celery import Celery, chain
from celery.utils.log import get_task_logger

import pycouchdb as couch
from pathlib import Path
from datetime import datetime
import subprocess
import json
import tempfile
import logging
import time
import json

from app.parsers import parse_fastq_name, parse_miseq_run_name
from app.model import SequencerRun, PipelineRun, Examination, Patient, filemaker_examination_types

from app.constants import testconfig, filemaker_examination_types_workflow_mapping, workflow_paths
from app.filemaker_api import Filemaker
from app.db_utils import clean_init_filemaker_mirror
from app.parsers import parse_date
from uuid import UUID, uuid4


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

logger = get_task_logger(__name__)

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


def get_db_url(config):
    user = config['couchdb_user']
    psw = config['couchdb_psw']
    host = 'localhost'
    port = 5984
    url = f"http://{user}:{psw}@{host}:{port}"
    return url

@mq.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sig = start_pipeline.signature(args=(config,))
    sender.add_periodic_task(300.0, sig, name='start pipeline every 300s')

    # sender.add_periodic_task(300.0, sig, name='sync filemaker to couchdb')
    # Executes every day at midnight
    '''
    sender.add_periodic_task(
        crontab(hour=0, minute=0, day_of_week='*'),
        #test.s('Happy Mondays!'),

    )
    '''

#@mq.task
def retrieve_new_filemaker_data(config):
    db = get_db(get_db_url(config))

    st = time.time()
    timeout = 2*60*60 # 2h in seconds
    off = 0
    while 1:
        try:
            # backoff for a few seconds
            time.sleep(5)
            resp = filemaker.get_all_records(offset=off*1000+1)
            recs = resp['data']
            for i,r in enumerate(recs):
                d = r['fieldData']
                d['document_type']='filemaker_record'
                db.save(d)
                logger.debug(f"saved {i}")

            if time.time() > (st + timeout):
                raise RuntimeError('database sync timed out')
        except Exception as e:
            logger.warning(f'cant export with offset {i} or database timed out with error: {e}')
            break

        off += 1

    return db



#@mq.task
def transform_data(config):
    app_db = get_db(get_db_url(config))

    deleted_docs = []
    for p in app_db.query('patients/patients'):
        #app_db.delete(p['value']['_id'])
        deleted_docs.append(p['value'])

    logger.info(len(deleted_docs))

    for p in app_db.query('examinations/examinations'):
        #app_db.delete(p['value']['_id'])
        deleted_docs.append(p['value'])

    logger.info(len(deleted_docs))

    todelete = []
    for d in deleted_docs:
        doc = {'_id':d['_id'], '_rev':d['_rev'], 'deleted':True}
        todelete.append(doc)

    app_db.save_bulk(todelete)

    k = None
    exams = []

    docs_to_save = []

    for doc in app_db.query('patients/patient_aggregation'):
        if k is None:
            k = doc['key']

        d = doc['value']

        if doc['key'] == k:
            uid = str(uuid4())

            exam = Examination(
                    id=uid,
                    examinationtype=d['Untersuchung'], 
                    started_date=parse_date(d['Zeitstempel']),
                    sequencer_runs=[],
                    pipeline_runs=[],
                    filemaker_record=d
                    )
            exams.append(exam)

        else:
            try:
                birthdate = datetime.strptime(d['GBD'], '%m/%d/%Y'),

                patient = Patient(
                    id=str(uuid4()),
                    names=[f'{d["Vorname"], d["Name"]}'],
                    birthdate=birthdate,
                    gender=d['Geschlecht'],
                    examinations=[e.id for e in exams],
                    )
            except Exception as e:
                logger.warning(e)

                patient = Patient(
                    id=str(uuid4()),
                    names=[f'{d["Vorname"], d["Name"]}'],
                    gender=d['Geschlecht'],
                    examinations=[e.id for e in exams],
                    )

            #app_db.save(patient.to_dict())
            docs_to_save.append(patient.to_dict())

            for e in exams:
                #app_db.save(e.to_dict())
                docs_to_save.append(e.to_dict())

            k = doc['key']
            exams = []

    app_db.save_bulk(docs_to_save)

@mq.task
def poll_new_cases(app_db, config):
    app_db = get_db(get_db_url(config))
    #transform_data(config)

    new_cases = app_db.query('examinations/new_examinations')
    return new_cases

@mq.task
def sync_couchdb_to_filemaker(config):
    retrieve_new_filemaker_data(config)
    transform_data(config)


@mq.task
def poll_sequencer_output(config):
    app_db = get_db(get_db_url(config))

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

        # run folder name doesnt adhere to illumina naming convention
        # because it has been renamed or manually copied
        # we save the parsed information too, so we can efficiently query the runs

        if str(run_name) in sequencer_paths:
            continue

        run_document = {
                'id': str(uuid4()),
                'document_type':'sequencer_run',
                'original_path':Path(run_name), 
                'name_dirty':str(dirty), 
                'parsed':parsed, 
                'state': 'successful',
                'indexed_time':datetime.now()
                }

        # this validates the fields
        sequencer_run = SequencerRun(**run_document)
        #app_db.save(json.loads(sequencer_run.json()))
        app_db.save(sequencer_run.to_dict())


def get_mp_number_from_path(p):
    d = parse_fastq_name(Path(p).name)
    return d['sample_name']

def db_save(pipeline_run):
    app_db = get_db(get_db_url(config))
    logger.debug(pipeline_run)
    pr = app_db.save(pipeline_run.to_dict())
    return pipeline_run.from_dict(pr)

def workflow_backend_execute(config, pipeline_run):
    logger.debug(f'workflow backend starts executing {pipeline_run}')

    return

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
                        pipeline_run.workflow
                        ] + [f'files={i}' for i in pipeline_run.workflow_inputs]

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
        logger.warning(e)
        
        # check types by converting into domain model object
        pipeline_document = pipeline_run.to_dict()
        pipeline_document['status'] = 'error'
        pipeline_run = pipeline_run.from_dict(pipeline_document)
        pipeline_run = db_save(pipeline_run)


def start_panel_workflow(config, workflow_inputs, panel_type, sequencer_run_path):
    logger.info(f'starting run: {sequencer_run_path}')
    app_db = get_db(get_db_url(config))

    if panel_type == 'invalid':
        logger.warning('info, panel type invalid skipping')
        return

    workflow_type = filemaker_examination_types_workflow_mapping[panel_type]
    logger.debug(f"workflow type: {workflow_type}")

    if workflow_type is None:
        logger.info('panel skipped')
        return

    workflow = workflow_paths[workflow_type]

    pipeline_run = PipelineRun(
            id=str(uuid4()),
            created_time=datetime.now(),
            input_samples=[str(x) for x in workflow_inputs],
            sequencer_run_path=Path(sequencer_run_path),
            sequencer_run_id='',
            workflow=workflow,
            status='running',
            logs={
                'stderr': '',
                'stdout': '',
                }
            )


    pipeline_run = db_save(pipeline_run)
    #exam = app_db.query('examinations/examination_fm_join')
    #p = list(app_db.query(f'examinations/mp_number?key=[{year},{mp_number}]'))

    workflow_backend_execute(config, pipeline_run)


def handle_sequencer_run(config:dict, new_run:dict):
    app_db = get_db(get_db_url(config))

    year_str = new_run['key']['parsed']['date']
    year = datetime.strptime(year_str, '%y%m%d').year
    samples = []

    sample_paths = (
            Path(config['miseq_output_folder']) 
            / Path(new_run['key']['original_path']).name
            ).rglob('*.fastq.gz')

    for sample_path in sample_paths:
        try:
            mp_number_with_year = get_mp_number_from_path(str(sample_path))
            mp_number, mp_year = mp_number_with_year.split('-')
            samplename_year = datetime.strptime(mp_year, '%y').year

            # check that database year field matches filename year
            if year != samplename_year:
                raise RuntimeError('year in the examination record mismatches with the year of the samplename')

            #get the the examination the sample belongs to
            p = list(app_db.query(f'examinations/mp_number?key=[{year},{mp_number}]'))
            logger.info(f' handeling sequencer run with sample: {sample_path} mp_number: {mp_number}')

            if len(p) != 1:
                panel_type = 'invalid'
            else:
                panel_type = p[0]['value']['examinationtype']

        
            if panel_type == 'invalid':
                raise RuntimeError('panel type invalid')
                continue

            samples.append({
                'path':sample_path, 
                'mp_number': mp_number, 
                'mp_year': mp_year,
                'panel_type': panel_type,
                'sequencer_run': new_run,
                })

        except Exception as e:
            logger.warning(f'error: {e}')
            continue

    results = []

    # run a batch workflow for each panel type
    for panel_type in filemaker_examination_types:
        if panel_type == 'invalid':
            continue 

        workflow_inputs = list(map(
            lambda s: Path(s['path']),
            filter(
                lambda s: s['panel_type'] == panel_type,
                samples
                )
            )
        )

        if len(workflow_inputs) == 0:
            continue

        result = start_panel_workflow(
                config, 
                workflow_inputs, 
                panel_type, 
                new_run['key']['original_path'],
                )

        results.append(result)

    return results

@mq.task
def start_pipeline(config):
    '''
    this loads the sequencer output files into the database
    compares if every sequencer run has an according pipeline run by the folder path

    if not, it runs the pipeline for the missing ones
    '''

    app_db = get_db(get_db_url(config))
    poll_sequencer_output(config)

    sequencer_runs = list(app_db.query('sequencer_runs/all'))
    pipeline_runs = list(app_db.query('pipeline_runs/all'))

    sequencer_run_ids = set([str(Path(r['key']['original_path']).name) for r in sequencer_runs])
    pipeline_run_refs = set([str(Path(r['key']['sequencer_run_path']).name) for r in pipeline_runs])
    new_run_ids = sequencer_run_ids - pipeline_run_refs

    new_runs = list(filter(
        lambda x: str(Path(x['key']['original_path']).name) in new_run_ids, 
        sequencer_runs)
        )

    if len(new_runs) == 0:
        logger.info('no new runs')
        return
    else:
        logger.info(f'found {len(new_runs)} new runs')

    for new_run in new_runs:
        if new_run['key']['state'] != 'successful':
            continue

        logger.info(f"starting pipeline for sequencer run {new_run['key']['original_path']}")
        handle_sequencer_run(config, new_run)
