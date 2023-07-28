from typing import Optional, Literal, List

from time import sleep
from itertools import count, groupby
from pathlib import Path
from datetime import datetime
from uuid import uuid4
from collections.abc import Callable

from celery.utils.log import get_task_logger

from more_itertools import flatten

from app.parsers import parse_fastq_name, parse_miseq_run_name, parse_date
from app.model import SequencerRun, PipelineRun, Examination, Patient, filemaker_examination_types, document_class_map, BaseDocument
from app.constants import filemaker_examination_types_workflow_mapping, workflow_paths
from app.tasks_utils import Timeout, Schedule
from app.workflow_backends import workflow_backend_execute

from app.db import DB
from app.config import CONFIG

import pycouchdb

logger = get_task_logger(__name__)

db = DB

def build_obj(obj: dict) -> BaseDocument:
    ty = obj['document_type']
    data_obj = document_class_map[ty](map_id=True, **obj)
    return data_obj


def query(query) -> List[BaseDocument]:
    l = db.query(query)
    return [build_obj(x['value']) for x in l]


def processor(record: dict) -> dict:
    d = record['fieldData']
    d['document_type'] = 'filemaker_record'
    return d


def retrieve_new_filemaker_data_full(filemaker, processor, backoff_time=5):
    ''' 
    iterate through all filemaker records in the table
    do so in 1000 record batches until an error signals
    that we've reached the end

    sleep in between to not overload the server
    save the raw data directly into the couchdb
    '''
    timeout = Timeout(2*60*60) # 2h in seconds

    for batches_done in count():
        try:
            # backoff for a few seconds
            sleep(backoff_time)
            response = filemaker.get_all_records(offset=batches_done*1000+1, limit=1000)
            records = response['data']
            res = list(map(processor, records))
            db.save_bulk(res)
            logger.debug(f"saved {batches_done} batches")

            if timeout.reached():
                raise RuntimeError('database sync timed out took too long in total')
        except Exception as e:
            logger.warning(f'cant export batch {batches_done} or database timed out with error: {e}')
            break

    return batches_done


def retrieve_new_filemaker_data_incremental(filemaker, processor, backoff_time=5):
    '''
    iterate through the highest filemaker records according to recordid and appstate
    do so in 1000 record batches

    if there are less records in filemaker than the couchdb, raise an error
    iteratively save the new latest record id
    '''
    timeout = Timeout(2*60*60) # 2h in seconds

    app_state = DB.get('app_state')
    last_synced_row = int(app_state['last_synced_filemaker_row'])
    # annoyingly, filemaker rows start with one, so we need to set last_synced row to 0 initially
    # and after, it will match the highest rowid, but the number ow rows will be last_synced_row-1
    if last_synced_row == -1:
        logger.info("starting first incremental sync")
        last_synced_row = 0

    for batches_done in count():
        try:
            # backoff for a few seconds
            sleep(backoff_time)
            offset = batches_done*1000 + last_synced_row+1
            response = filemaker.get_all_records(offset=offset, limit=1000)
            records = list(response['data'])
            logger.debug(f"retrieved {len(records)} filemaker_rows")
            logger.debug(f"last_synced_row_was {last_synced_row} and record id was {records[0]['recordId']}")


            if last_synced_row >= int(records[0]['recordId']):
                logger.error(f"record id doesnt match last_synced_row with record {records}")
                raise RuntimeError('record id doesnt match last_synced_row')

            #rowids = list(map(lambda x: int(x['recordId']), records))
            #app_state['last_synced_filemaker_row'] = max(rowids)
            app_state['last_synced_filemaker_row'] = offset + len(records)
            newdocs = list(map(processor, records)) + [app_state]
            #docs = filter_existing(newdocs)
            DB.save_bulk(newdocs)

            app_state = DB.get('app_state')
            last_synced_row = int(app_state['last_synced_filemaker_row'])

            logger.debug(f"rowids: {rowids}")

            if timeout.reached():
                raise RuntimeError('database sync timed out, it took too long in total')

        except Exception as e:
            logger.warning(f'cant export batch {batches_done} or database timed out with error: {e}')
            break

    return batches_done



def create_examinations():
    '''
    scan through all filemaker records and create an exam document
    for all filemaker records that didnt have one

    collect errors where duplicate examination exist
    
    examination records contain the original filemaker records
    '''
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
                filemaker_record=d,
                #last_sync_time=datetime.now(),
                annotations={}
                )
        db.save(exam.to_dict())

        if i % 1000==0:
            logger.info(f'created {i} examinations and continuing')


def get_names(examination):
    filemaker_record = examination.filemaker_record
    names = {}
    names['fullname'] = f"{filemaker_record['Vorname']} {filemaker_record['Name']}"
    names['firstname'] = filemaker_record['Vorname']
    names['lastname'] = filemaker_record['Name']
    return names


def create_patient_aggregate(examinations: [Examination]) -> Patient :
    # use the most recent names as the patients names
    sorted_exams = sorted(examinations, key=lambda e: e.started_date)
    names = list(map(get_names, sorted_exams))[-1]

    if len({e.filemaker_record['GBD'] for e in examinations}) != 1:
        logger.error(f'examination group {examinations} has multiple birthdates')

    try:
        birthdate = datetime.strptime(examinations[0].filemaker_record['GBD'], '%m/%d/%Y')
    except Exception as e:
        logger.error(e)
        raise e

    if len({e.filemaker_record['Geschlecht'] for e in examinations}) != 1:
        logger.warn(f'detected gender change in patient of examinations {examinations}')

    gend = sorted_exams[-1].filemaker_record['Geschlecht']
    eids = [e.id for e in examinations]

    patient = Patient(
        map_id=False,
        id=str(uuid4()),
        names=names,
        birthdate=birthdate, 
        gender=gend,
        examinations=eids
        )
    return patient


def aggregate_patients():
    ''' scan through all examination documents and group
    them by [name, birthdate] (see the patients/patient_aggregation view)
    create a patient document for every group

    link the patient and exam documents by their id's
    '''
    logger.info('aggregating patients')
    it = db.query('patients/patient_aggregation?include_docs=true')
    logger.info('grouping examinations for patient aggregation')

    for i, (key, group) in enumerate(groupby(it, key=lambda d: d['key'][0:-1])):
        g = list(group)

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

        examination_ids = [e.id for e in examinations]
        patient_objs = [Patient(map_id=True, **(e['doc'])) for e in patient_entries]

        if len(patient_objs) > 1:
            raise RuntimeError(f'too many patient objects for examination group: {g}')
        elif len(patient_objs) == 1:
            # found a patient, update patient examinations if there is a mismatch
            pd = patient_objs[0]

            if pd.examinations != examination_ids:
                new_patient = pd.to_dict()
                pd['examinations'] = examination_ids
                p = Patient(True, pd)
                db.save(Patient.to_dict())
        else:
            # no patient exists for the examinations
            try:
                patient = create_patient_aggregate(examinations)
                db.save(patient.to_dict())
            except Exception as e:
                continue


        if i % 100 == 0:
            logger.info(f'aggregated {i} patients, continuing')


def get_mp_number_from_path(p):
    d = parse_fastq_name(Path(p).name)
    return d['sample_name']


def get_examination_of_sample(sample_path, missing_ok=False):
    mp_number_with_year = get_mp_number_from_path(str(sample_path))
    mp_number, mp_year = mp_number_with_year.split('-')

    try:
        examinations = db.query(f'examinations/mp_number?key=[{mp_year},{mp_number}]')
    except pycouchdb.exceptions.NotFound:
        logger.info(f'no examination of sample {sample_path} found')
        examinations = [None]

    if missing_ok == False and len(examinations) == 0:
        raise RuntimeError(f"no examination found for sample: {sample}")
    elif len(examinations) >= 2:
        raise RuntimeError(f"multiple examinations found for sample: {sample} examinations: {examinations}")
    elif missing_ok == True and len(examinations) == 0:
        return None
    else:
        examination = examinations[0]
        return examination


def get_mp_number_from_filemaker_record(rec):
    mpnr = str(int(rec['Mol_NR'])) + '-' + str(rec['Jahr'])[-2:]
    return mpnr

def get_samples_of_examination(examination):
    ex_mpnr = get_mp_number_from_filemaker_record(examination.filemaker_record)
    print(examination.sequencer_runs)
    
    sample_candidates = []
    for srid in examination.sequencer_runs:
        sample_candidates += db.get(srid)['outputs']

    examination_samples = []
    for sa in sample_candidates:
        if get_mp_number_from_path(sa) == ex_mpnr:
            examinations_samples.append(sa)

    return examination_samples


def check_years_match(sequencer_run, samples):
    run_year_str = sequencer_run.parsed['date']
    run_year = {datetime.strptime(run_year_str, '%y%m%d').year}

    sample_years = set()

    for sample_path in samples:
        mp_number_with_year = get_mp_number_from_path(str(sample_path))
        mp_number, mp_year = mp_number_with_year.split('-')
        samplename_year = datetime.strptime(mp_year, '%y').year
        sample_years.add(samplename_year)

    if run_year != sample_years:
        raise RuntimeError(f'sequencer run name has a different year than its output samples with sample year: {sample_years} and run year {run_year}')


def link_examinations_to_sequencer_run(examinations: dict, seq_run_id: str):
    new_exams = []

    for exam in examinations:
        ex = Examination(map_id=True, **exam).sequencer_runs
        if seq_run_id not in ex.sequencer_runs:
            ex.sequencer_runs = ex.sequencer_runs + [seq_run_id]
            new_exams.append(ex)
        else:
            continue

    return new_exams



def poll_sequencer_output():
    ''' ingest sequencer data from filepath
    '''

    # first, sync db with miseq output data
    db_sequencer_runs = db.query('sequencer_runs/all')
    db_sequencer_paths = [str(r['value']['original_path']) for r in db_sequencer_runs]

    fs_miseq_output_path = Path(CONFIG['miseq_output_folder'])
    fs_miseq_output_runs = [fs_miseq_output_path / x for x in fs_miseq_output_path.iterdir()]

    sequencer_runs = []

    for run_name in fs_miseq_output_runs:
        try:
            parsed = parse_miseq_run_name(run_name.name)
            dirty=False
        except RuntimeError as e:
            parsed = {}
            dirty=True

        outputs = list(Path(run_name).rglob('*.fastq.gz'))

        # run folder name doesnt adhere to illumina naming convention
        # because it has been renamed or manually copied
        # we save the parsed information too, so we can efficiently query the runs

        # skip creating sequencer run if it already exists
        if str(run_name) in db_sequencer_paths:
            continue

        sequencer_run = SequencerRun(
                map_id=False,
                id=str(uuid4()),
                original_path=str(run_name),
                name_dirty=str(dirty),
                parsed=parsed,
                state='successful',
                indexed_time=datetime.now(),
                outputs=outputs
                )

        try:
            check_years_match(sequencer_run, outputs)
        except Exception as e:
            logger.error('sequencer run year could not be checked due to error: {e}')

        examinations = []
        for s in outputs:
            try:
                x = get_examination_of_sample(db, s, missing_ok=True)
                if x is not None:
                    examinations.append(x)
            except Exception as e:
                logger.error(f'examination could not be obtained for sample: {s} due to: {e}')

        new_exams = link_examinations_to_sequencer_run(examinations, sequencer_run.id)

        # this validates the fields
        db.save_bulk([sequencer_run] + new_exams)
        sequencer_runs.append(sequencer_run)

    return sequencer_runs


def start_workflow_impl(
        is_aborted: Callable, 
        workflow_inputs, 
        panel_type: str
        ):

    logger.info(f'starting new pipeline run with inputs: {workflow_inputs} and panel: {panel_type}')

    examinations, samples = list(zip(*workflow_inputs))

    if panel_type == 'invalid':
        logger.warning('info, panel type invalid skipping')
        return

    if panel_type not in filemaker_examination_types_workflow_mapping:
        logger.error(f"panel type: {panel_type} not known in filemaker examination_types")
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
            input_samples=[str(x) for x in samples],
            workflow=workflow,
            status='running',
            logs={
                'stderr': '',
                'stdout': '',
                }
            )

    # link pipeline runs to the examinations
    new_ex_docs = []
    for e in examinations:
        d = e
        d['pipeline_runs'] = e['pipeline_runs'] + [pipeline_run.id]
        new_ex_docs.append(d)

    pipeline_run = db.save_obj(pipeline_run)
    db.save_bulk(new_ex_docs)


    # pass is_aborted function to backend for stopping
    if 'backend' in CONFIG:
        backend = CONFIG['backend']
    else:
        backend = 'nextflow'
    workflow_backend_execute(pipeline_run, is_aborted, backend)


def group_samples_by_panel(samples):
    start_panel_workflow_tasks = []

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
        sequencer_run_path = new_run['value']['original_path']

        task_args = (
                workflow_inputs, 
                panel_type, 
                sequencer_run_path
                )
        
        start_panel_workflow_tasks.append(task_args)

    return start_panel_workflow_tasks


def collect_new_runs():
    logger.info(f'started collecting new runs')

    sequencer_runs = db.query('sequencer_runs/all')
    pipeline_runs = db.query('pipeline_runs/all')

    sequencer_run_ids = set([str(Path(r['value']['original_path']).name) for r in sequencer_runs])
    pipeline_run_refs = set([str(Path(r['value']['sequencer_run_path']).name) for r in pipeline_runs])
    new_run_ids = sequencer_run_ids - pipeline_run_refs

    # get the new_run docs that match the new_run_ids
    new_runs = list(filter(
        lambda x: str(Path(x['value']['original_path']).name) in new_run_ids, 
        sequencer_runs)
        )

    if len(new_runs) == 0:
        logger.info('no new runs')
        return
    else:
        logger.info(f'collected {len(new_runs)} new runs')

    return new_runs


def group_examinations_by_type(examinations):
    groups = {}
    for e in examinations:
        ty = e.filemaker_record['Untersuchung']
        if ty not in filemaker_examination_types:
            ty = 'invalid'

        if ty not in groups:
            groups[ty] = [e]
        else:
            groups[ty] = groups[ty] + [e]

    return groups


def collect_work():
    #new_runs = collect_new_runs(db,config)
    new_examinations = db.query('examinations/new_examinations')
    new_examinations = [Examination(True, **(e['value'])) for e in new_examinations]
    groups = group_examinations_by_type(new_examinations)
    return groups



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

