from celery import Celery, chain, group
from celery.utils.log import get_task_logger
from celery.contrib.abortable import AbortableTask

from pathlib import Path
from datetime import datetime
import subprocess
import tempfile
import logging
import time
from itertools import count, groupby
from more_itertools import chunked

from app.parsers import parse_fastq_name, parse_miseq_run_name
from app.model import SequencerRun, PipelineRun, Examination, Patient, filemaker_examination_types

from app.constants import filemaker_examination_types_workflow_mapping, workflow_paths
from app.config import Config
from app.filemaker_api import Filemaker
from app.db import DB
from app.parsers import parse_date
from uuid import UUID, uuid4

# for sigint
import signal

logger = get_task_logger(__name__)

config = Config().dict()

mq = Celery('ngs_pipeline', 
        **Config().celery_config()
        )

class Timeout:
    def __init__(self, seconds):
        self.starttime = time.time()
        self.length = seconds

    def reached(self):
        return time.time() > (self.starttime + self.length)

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

def retrieve_new_filemaker_data_full(config, backoff_time=5):
    db = DB.from_config(config)

    timeout = Timeout(2*60*60) # 2h in seconds
    filemaker = Filemaker.from_config(config)

    for batches_done in count():
        try:
            # backoff for a few seconds
            time.sleep(backoff_time)
            response = filemaker.get_all_records(offset=batches_done*1000+1, limit=1000)
            records = response['data']
            for i,r in enumerate(records):
                d = r['fieldData']
                d['document_type']='filemaker_record'
                db.save(d)
                logger.debug(f"saved {i}")

            if timeout.reached():
                raise RuntimeError('database sync timed out took too long in total')
        except Exception as e:
            logger.warning(f'cant export batch {batches_done} or database timed out with error: {e}')
            break

    return db


def retrieve_new_filemaker_data_incremental(config, backoff_time=5):
    db = DB.from_config(config)

    timeout = Timeout(2*60*60) # 2h in seconds

    app_state = db.get('app_state')
    last_synced_row = int(app_state['last_synced_filemaker_row'])
    filemaker = Filemaker.from_config(config)

    def make_fm_doc(r):
        d = r['fieldData']
        d['document_type']='filemaker_record'
        return d

    for batches_done in count():
        try:
            # backoff for a few seconds
            time.sleep(backoff_time)
            response = filemaker.get_all_records(offset=batches_done*1000+last_synced_row+1, limit=1000)
            records = list(response['data'])
            logger.debug(f"retrieved {len(records)} filemaker_rows")
            logger.debug(f"last_synced_row_was {last_synced_row} and record id was {records[0]['recordId']}")

            if last_synced_row >= int(records[0]['recordId']):
                raise RuntimeError('record id doesnt match last_synced_row')

            rowids = list(map(lambda x: int(x['recordId']), records))
            app_state['last_synced_filemaker_row'] = max(rowids)
            newdocs = list(map(make_fm_doc, records)) + [app_state]
            db.save_bulk(newdocs)
            logger.debug(f"rowids: {rowids}")

            if timeout.reached():
                raise RuntimeError('database sync timed out took too long in total')

        except Exception as e:
            logger.warning(f'cant export batch {batches_done} or database timed out with error: {e}')
            break

    return batches_done


def create_examinations(config):
    db = DB.from_config(config)

    logger.info('creating examinations')

    new_records = []
    duplicate_examinations = []
    for p in db.query('filemaker/all?group_level=1&'):
        if p['value'] < 1:
            new_records.append(p['key'][0])
        elif p['value'] > 1:
            duplicate_examinations.append(p['key'][0])

    logger.info('finished grouping filemaker records, starting creating examinations')

    for i, p in enumerate(new_records):
        filemaker_record = db.get(p)
        d = filemaker_record

        exam = Examination(
                map_id=False,
                id=str(uuid4()),
                examinationtype=d['Untersuchung'], 
                started_date=parse_date(d['Zeitstempel']),
                sequencer_runs=[],
                pipeline_runs=[],
                filemaker_record=d
                )
        db.save(exam.to_dict())

        if i % 1000==0:
            logger.info('created {i} examinations and continuing')


def aggregate_patients(config):
    db = DB.from_config(config)
    logger.info('aggregating patients')
    it = list(db.query('patients/patient_aggregation?include_docs=true'))
    logger.info('grouping examinations for patient aggregation')

    for i, (key, group) in enumerate(groupby(it, key=lambda d: d['key'])):
        g = list(group)

        if i == 0:
            logger.info(f'groups: {g}')

        patient_entries = list(filter(
            lambda d: d['doc']['document_type'] == 'patient',
            g
            ))
        examination_docs = list(filter(
            lambda d: d['doc']['document_type'] == 'examination',
            g
            ))
        examinations = list(map(
            lambda e: Examination(True, **e['doc']), 
            examination_docs
            ))

        if i == 0:
            logger.info(f'examinations: {examinations}')

        examinations_ids = [e.id for e in examinations]

        if len(patient_entries) > 1:
            raise RuntimeError(f'too many patient objects for examination group: {g}')
        elif len(patient_entries) == 1:
            pd = patient_entries[0]
            pd.pop('_rev')
            pd['examinations'] = examination_ids
            p = Patient.from_dict(pd)
            db.save(Patient.to_dict())
        else:
            # no patient exists for the examinations
            names = list(map(
                lambda e: f"{e.filemaker_record['Vorname']}, {e.filemaker_record['Name']}",
                examinations))

            if len({e.filemaker_record['GBD'] for e in examinations}) != 1:
                logger.error(f'examination group {examinations} has multiple birthdates')

            if len({e.filemaker_record['Geschlecht'] for e in examinations}) != 1:
                logger.warn(f'detected gender change in patient of examinations {examinations}')

            gend = list(sorted(
                    examinations,
                    key=lambda e: 
                        datetime.strptime(
                            e.filemaker_record['Zeitstempel'],
                            '%m/%d/%Y'
                            )
                ))[0].filemaker_record['Geschlecht']

            patient = Patient(
                map_id=False,
                id=str(uuid4()),
                names=names,
                birthdate=datetime.strptime(examinations[0].filemaker_record['GBD'], '%m/%d/%Y'),
                gender=gend,
                examinations=examination_ids
                )
            db.save(patient)

        if i % 10 == 9:
            break

        if i % 100 == 0:
            logger.info('aggregated {i} patients, continuing')


#@mq.task
def transform_data(config):
    db = DB.from_config(config)
    #create_examinations(config)
    aggregate_patients(config)
    return


@mq.task
def sync_couchdb_to_filemaker(config):
    #retrieve_new_filemaker_data_incremental(config)
    transform_data(config)


def poll_sequencer_output(config):
    db = DB.from_config(config)

    # first, sync db with miseq output data
    sequencer_runs = list(db.query('sequencer_runs/all'))
    sequencer_paths = [str(r['value']['original_path']) for r in sequencer_runs]

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

        sequencer_run = SequencerRun(
                map_id=False,
                id=str(uuid4()),
                original_path=Path(run_name),
                name_dirty=str(dirty),
                parsed=parsed,
                state='successful',
                indexed_time=datetime.now()
                )

        # this validates the fields
        db.save(sequencer_run.to_dict())


def get_mp_number_from_path(p):
    d = parse_fastq_name(Path(p).name)
    return d['sample_name']


def workflow_backend_execute(config, pipeline_run, is_aborted):
    logger.debug(f'workflow backend starts executing {pipeline_run.id}')
    db = DB.from_config(config)

    try:
        output_dir = config['workflow_output_dir']

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
                        ] + [f'files={i}' for i in pipeline_run.input_samples]

                pipeline_proc = subprocess.Popen(
                        cmd,
                        stdout=stde, #subprocess.PIPE, 
                        stderr=stdo, #subprocess.PIPE
                        #capture_output=True
                        )

                # update db entry every second when the process runs
                while pipeline_proc.poll() is None:
                    if is_aborted():
                        logger.warning(f'pipeline_run: {pipeline_run.id} is aborting')
                        pipeline_proc.send_signal(signal.SIGINT)
                        logger.warning(f'pipeline_run: {pipeline_run.id} was aborted')

                    stde.seek(0)
                    stdo.seek(0)
                    pipeline_run.logs.stderr = stde.read().decode('utf-8')
                    pipeline_run.logs.stdout = stdo.read().decode('utf-8')

                    pipeline_run = db.save_obj(pipeline_run)
                    time.sleep(1)

                # update db entry at the end
                stde.seek(0)
                stdo.seek(0)
                pipeline_run.logs.stderr = stde.read().decode('utf-8')
                pipeline_run.logs.stdout = stdo.read().decode('utf-8')

                retcode = pipeline_proc.returncode
                if retcode == 0:
                    pipeline_run.status = 'successful'
                elif retcode == signal.SIGINT:
                    pipeline_run.status = 'aborted'
                else:
                    pipeline_run.status = 'error'

                pipeline_run = db.save_obj(pipeline_run)

    except Exception as e:
        logger.warning(e)
        
        # check types by converting into domain model object
        pipeline_document = pipeline_run.to_dict()
        pipeline_document['status'] = 'error'
        pipeline_run = pipeline_run.from_dict(pipeline_document)
        pipeline_run = db.save_obj(pipeline_run)


@mq.task(bind=True, base=AbortableTask)
# self because its an abortable task
# aborting doesnt work yet
def start_panel_workflow(self, config, workflow_inputs, panel_type, sequencer_run_path):
    logger.info(f'starting run: {sequencer_run_path}')
    db = DB.from_config(config)

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
            False,
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


    pipeline_run = db.save_obj(pipeline_run)
    #exam = db.query('examinations/examination_fm_join')
    #p = list(db.query(f'examinations/mp_number?key=[{year},{mp_number}]'))

    # pass is_aborted function to backend for stopping
    workflow_backend_execute(config, pipeline_run, self.is_aborted)



def handle_sequencer_run(config:dict, seq_run:SequencerRun):#, new_run:dict):
    db = DB.from_config(config)

    new_run = {'value':seq_run.to_dict()}

    year_str = new_run['value']['parsed']['date']
    year = datetime.strptime(year_str, '%y%m%d').year
    samples = []

    sample_paths = (
            Path(config['miseq_output_folder']) 
            / Path(new_run['value']['original_path']).name
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
            p = list(db.query(f'examinations/mp_number?key=[{year},{mp_number}]'))
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

    tasks = []

    # run a batch workflow for each panel type
    for panel_type in filemaker_examination_types:
        if panel_type == 'invalid':
            continue 

        workflow_inputs = list(map(
            lambda s: str(Path(s['path'])),
            filter(
                lambda s: s['panel_type'] == panel_type,
                samples
                )
            )
        )

        # skip if there is no work for the pipeline
        if len(workflow_inputs) == 0:
            continue

        # create async celery tasks
        signature = start_panel_workflow.s(
                config, 
                workflow_inputs, 
                panel_type, 
                new_run['value']['original_path'],
                )
        
        tasks.append(signature)

    lazy_group = group(tasks)
    promise = lazy_group.apply_async()

    return promise


@mq.task
def start_pipeline(config):
    '''
    this loads the sequencer output files into the database
    compares if every sequencer run has an according pipeline run by the folder path

    if not, it runs the pipeline for the missing ones
    '''

    db = DB.from_config(config)
    poll_sequencer_output(config)

    sequencer_runs = list(db.query('sequencer_runs/all'))
    pipeline_runs = list(db.query('pipeline_runs/all'))

    sequencer_run_ids = set([str(Path(r['value']['original_path']).name) for r in sequencer_runs])
    pipeline_run_refs = set([str(Path(r['value']['sequencer_run_path']).name) for r in pipeline_runs])
    new_run_ids = sequencer_run_ids - pipeline_run_refs
    logger.info(f'starting pipeline with {len(new_run_ids)} new runs')

    new_runs = list(filter(
        lambda x: str(Path(x['value']['original_path']).name) in new_run_ids, 
        sequencer_runs)
        )

    if len(new_runs) == 0:
        logger.info('no new runs')
        return
    else:
        logger.info(f'found {len(new_runs)} new runs')

    results = []

    for new_run in new_runs:
        if new_run['value']['state'] != 'successful':
            continue

        logger.info(f"starting pipeline for sequencer run {new_run['value']['original_path']}")
        result = handle_sequencer_run(config, SequencerRun(True, **new_run['value']))
        results.append(result)

    return results


class Schedule:
    def __init__(self, db):
        self.db = db

    def acquire_lock(self):
        app_state = self.db.get('app_state')
        if app_state['sync_running'] == True:
            logger.debug('sync already running')
            raise RuntimeError()
        else:
            logger.debug('sync not running, acquiring sync state')
            app_state['sync_running'] = True
            self.db.save(app_state)

    def release_lock(self):
        app_state = self.db.get('app_state')
        #app_state['sync_running'] = False
        self.db.save(app_state)

    def is_enabled(self):
        default_app_settings = {
            '_id':'app_settings',
            'schedule': '',
            'autorun_pipeline':False
        }

        settings = self.db.get('app_settings')
        return settings['autorun_pipeline'] == True


    def has_work_now(self):
        settings = self.db.get('app_settings')
        return settings['schedule'] == ''


@mq.task
def run_schedule(config):
    db = DB.from_config(config)
    schedule = Schedule(db)
    schedule.acquire_lock()

    try:
        if schedule.is_enabled() and schedule.has_work_now():
            s1 = sync_couchdb_to_filemaker.s(config)
            s2 = start_pipeline.s(config)
            res = chain(s1, s2)
            res.apply_async()
    finally:
        schedule.release_lock()
