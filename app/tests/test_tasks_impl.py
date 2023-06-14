import pytest

import app
from app.filemaker_api import Filemaker
from app.tasks_impl import processor, retrieve_new_filemaker_data_full, retrieve_new_filemaker_data_incremental, create_examinations

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
    def test_retrieve_new_filemaker_data_full(self, monkeypatch, fm_mock, config, db):
        filemaker = fm_mock
        retrieve_new_filemaker_data_full(db, filemaker, processor, backoff_time=5)
        alldocs = [drop(x['doc'], ['_id','_rev'], ignore=True) for x in list(db.all())]
        assert fm_record['fieldData'] in alldocs

    def test_retrieve_new_filemaker_data_incremental(self, fm_mock, db, config):
        filemaker = fm_mock
        retrieve_new_filemaker_data_incremental(db, filemaker, processor, backoff_time=5)
        alldocs = [drop(x['doc'], ['_id','_rev'], ignore=True) for x in list(db.all())]
        assert fm_record['fieldData'] in alldocs

    # process model data
    def test_create_examinations(self, fm_mock, db, config):
        filemaker = fm_mock
        retrieve_new_filemaker_data_incremental(db, filemaker, processor, backoff_time=5)
        create_examinations(db, config)

        alldocs = [x['doc'] for x in list(db.all())]
        docs = list(filter(lambda d: 'document_type' in d and d['document_type'] == 'examination', alldocs))
        docs = [drop(d['filemaker_record'], ['_id','_rev']) for d in docs]
        assert fm_record['fieldData'] in docs

    def aggregate_patients(config):
        pass

# ingest 
def poll_sequencer_output(self, config):
    pass

# run pipeline
def workflow_backend_execute(config, pipeline_run, is_aborted):
    pass
def start_panel_workflow_impl(self, config, workflow_inputs, panel_type, sequencer_run_path):
    pass
def handle_sequencer_run(config:dict, seq_run):#, new_run:dict):
    pass
def app_start_pipeline(config):
    pass

# periodic sync
def app_schedule(config):
    pass
