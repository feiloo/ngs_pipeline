import pytest

from app.parsers import parse_fastq_name
from app.constants import testconfig
import app
from app.tasks import handle_sequencer_run

#def test_start_panel_workflow(testconfig)uI#, workflow_inputs, panel_type, sequencer_run_path):
def test_start_panel_workflow(config):
    config=testconfig
    panel_type=None
    #start_panel_workflow(config, workflow_inputs, panel_type, sequencer_run_path)

@pytest.fixture()
def sequencer_run():
    run = {
      "_id": "6d3df7f2-8d2d-485a-8873-ec0b7769bddb",
      "_rev": "1-057c351ea7a4195b43d047c23f1441aa",
      "data_model_version": "0.0.1",
      "document_type": "sequencer_run",
      "original_path": "/data/private_testdata/miseq_output_testdata/220831_M03135_0376_000000000-KHR5V",
      "name_dirty": False,
      "parsed": {
	"date": "220831",
	"device": "M03135",
	"run_number": "0376",
	"flowcell_barcode": "000000000-KHR5V"
      },
      "indexed_time": "2023-03-09T16:49:56.974636",
      "state": "successful"
    }
	
    return run

exam = {
      "_id": "00026972-6af1-4f70-a5a7-6c37b15288b9",
      "_rev": "1-45547578e624fa80c5b0171db53b5c57",
      "data_model_version": "0.0.1",
      "document_type": "examination",
      "examinationtype": "NRAS",
      "started_date": "2013-12-17T00:00:00",
      "sequencer_runs": [],
      "pipeline_runs": [],
      "filemaker_record": {}
    }
	

class MockDB:
    def save(self, *args, **kwargs):
        pass

    def get(self, *args, **kwargs):
        pass

    def query(self, url, *args, **kwargs):
        if 'examinations/mp_number?key=' in url:
            return [{'value':exam}]
        pass


@pytest.fixture()
def db():
    return MockDB()


def test_handle_sequencer_run(monkeypatch, config, sequencer_run, db):
    config=testconfig

    def start_panel_workflow_mock(*args, **kwargs):
        '''
            start_panel_workflow(
                    config, 
                    workflow_inputs, 
                    panel_type, 
                    new_run['key']['original_path'])
        '''
        pass

    def get_db_mock(*args,**kwargs):
        return MockDB()

    monkeypatch.setattr(app.tasks, 'start_panel_workflow', start_panel_workflow_mock)
    
    workflow_inputs=[]
    panel_type=''
    sequencer_run_path=''
    #app.tasks.start_panel_workflow(config, workflow_inputs, panel_type, sequencer_run_path)
    app.tasks.handle_sequencer_run(config, new_run={'key':sequencer_run}, app_db=db)
