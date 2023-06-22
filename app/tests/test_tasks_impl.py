import pytest
from pathlib import Path
from collections.abc import Callable

import shutil

import app
from app.filemaker_api import Filemaker
from app.tasks_impl import processor, retrieve_new_filemaker_data_full, retrieve_new_filemaker_data_incremental, create_examinations, poll_sequencer_output, create_patient_aggregate

from app.model import Examination, Patient
from app.parsers import parse_date

from tests.conftest import fm_record

def drop(d, k, ignore=False):
    ''' ignore non existing key '''
    if isinstance(k, str):
        if k not in d and ignore:
            pass
        else:
            d.pop(k)
    elif isinstance(k, list):
        for kv in k:
            if kv not in d and ignore:
                pass
            else:
                d.pop(kv)
    else:
        RuntimeError("k has to be string or list")
    return d


@pytest.mark.incremental
class TestDBSync:
    # sync other db
    def test_retrieve_new_filemaker_data_full(self, fm_mock2, config, db):
        filemaker = fm_mock2
        retrieve_new_filemaker_data_full(db, filemaker, processor, backoff_time=0.1)
        alldocs = [drop(x['doc'], ['_id','_rev'], ignore=True) for x in list(db.all())]
        #assert fm_record['fieldData'] in alldocs

    def test_retrieve_new_filemaker_data_incremental(self, fm_mock2, db, config):
        filemaker = fm_mock2
        retrieve_new_filemaker_data_incremental(db, filemaker, processor, backoff_time=0.1)
        alldocs = [drop(x['doc'], ['_id','_rev'], ignore=True) for x in list(db.all())]
        #assert fm_record['fieldData'] in alldocs

    # process model data
    def test_create_examinations(self, fm_mock2, db, config):
        filemaker = fm_mock2
        retrieve_new_filemaker_data_incremental(db, filemaker, processor, backoff_time=0.1)
        create_examinations(db, config)

        alldocs = [x['doc'] for x in list(db.all())]
        docs = list(filter(lambda d: 'document_type' in d and d['document_type'] == 'examination', alldocs))
        docs = [drop(d['filemaker_record'], ['_id','_rev']) for d in docs]
        #assert fm_record['fieldData'] in docs

    def test_create_patient_aggregate(self):
        exam = Examination(
                map_id=False,
                id="examid",
                examinationtype='',
                started_date=parse_date('01/01/2001'),
                sequencer_runs=[],
                pipeline_runs=[],
                filemaker_record={
                    "Name":"N", 
                    "Vorname":"V", 
                    "GBD": "01/01/2001", 
                    "Geschlecht":"M", 
                    "Zeitstempel":"01/01/2001"
                    }
                )
        examinations = [exam]
        patient = create_patient_aggregate(examinations)
        assert patient.examinations == ["examid"]

    def aggregate_patients(config):
        pass


# ingest 
def test_poll_sequencer_output(db, config, testdir):
    miseq_output_folder = Path(testdir) / 'fake_sequencer_output_dir'

    c = config.dict()
    c['miseq_output_folder'] = str(miseq_output_folder)
    db_sequencer_runs = [x['original_path'] for x in db.view('sequencer_runs/all')]
    assert db_sequencer_runs == []
    poll_sequencer_output(db, c)
    db_sequencer_runs = [x['original_path'] for x in db.view('sequencer_runs/all')]
    fs_sequencer_runs = [ str(miseq_output_folder / '220101_M00000_0000_000000000-XXXXX')]
    assert db_sequencer_runs == fs_sequencer_runs

def start_workflow_impl(is_aborted: Callable, config, workflow_inputs, panel_type):
    pass

def handle_sequencer_run(config:dict, seq_run):#, new_run:dict):
    pass

def app_start_pipeline(config):
    pass

# periodic sync
def app_schedule(config):
    pass
