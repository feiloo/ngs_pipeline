import pycouchdb as couch
import pytest

from app.db import DB, View, DesignDoc, basic_view

import subprocess
import time

def test_ddoc():
    patient_aggregation_fn = '''
    if(doc.document_type == 'examination'){
      emit([doc.filemaker_record.Name, doc.filemaker_record.Vorname, doc.filemaker_record.GBD, doc._id], doc._id);
      }
    if(doc.document_type == 'patient'){
      emit([doc.filemaker_record.Name, doc.filemaker_record.Vorname, doc.filemaker_record.GBD, doc._id], doc._id);
      }
    '''

    patient_map_fn = '''
    emit(doc._id, doc);
    '''

    patient_aggregation = basic_view('patients_aggregation', patient_aggregation_fn)
    patient = basic_view('patients', patient_map_fn, doctypes=['patient'])
    patients_ddoc = DesignDoc('patients', [patient_aggregation, patient])

    #assert patients_ddoc.to_dict() == 
    #print(patients_ddoc.to_dict())

def test_create_document(db):
    init_doc = {"_id":"sequencer_runs", 
            "run_names": [],
            }

    #app_db = db
    db.save(init_doc)

    #_start_pipeline(app_db)
    res = db.get('sequencer_runs')
    res.pop('_rev')
    assert res == init_doc
