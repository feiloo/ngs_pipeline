import pycouchdb as couch


def clean_init_filemaker_mirror():
    server = couch.Server(url)
    try:
        server.delete('filemaker_mirror')
    except:
        pass

    server.create('filemaker_mirror')
    db = server.database('filemaker_mirror')

    filemaker_mirror_patient_grouping_map_fn = '''
    function (doc) {
        emit([doc.Name, doc.Vorname, doc.GBD, doc.Zeitstempel], doc);
    }
    '''

    response = db.save(
        {
            "_id": '_design/filemaker', 
            'views':
            {
            'all':{"map":filemaker_map_fn},
            }
        }
        )

    return db

def setup_views(app_db):
    sequencer_map_fn = '''
    function (doc) {
      if(doc.document_type == 'sequencer_run')
        emit(doc, 1);
        }
    '''
    sample_map_fn = '''
    function (doc) {
      if(doc.document_type == 'sample')
        emit(doc, 1);
        }
    '''
    pipeline_map_fn = '''
    function (doc) {
      if(doc.document_type == 'pipeline_run')
        emit(doc, 1);
        }
    '''

    filemaker_map_fn = '''
    function (doc) {
      if(doc.document_type == 'filemaker_record')
        emit(doc, 1);
        }
    '''

    examinations_new_cases = '''
    function (doc) {
      if(document_type == 'examination') {
	if(doc.sequencer_runs.length != 0 && doc.pipeline_runs == 0){
	  emit(doc, null);
	}
      }
    }
    '''

    examinations_mp_number = '''
    function (doc) {
      if (doc.document_type == 'filemaker_record'){
          emit([doc.Jahr, doc.Mol_NR], doc.Untersuchung);
            }
    }
    '''


    response = app_db.save(
        {
            "_id": '_design/sequencer_runs', 
            'views':
            {
            'all':{"map":sequencer_map_fn},
            }
        }
        )

    response = app_db.save(
        {
            "_id":'_design/samples', 
            'views':
                {
                'all':{"map":sample_map_fn}
                }
        })

    response = app_db.save(
        {
            "_id":'_design/pipeline_runs', 
            'views':
                {
                'all':{"map":pipeline_map_fn}
                }
        })

    response = app_db.save(
        {
            "_id": '_design/filemaker', 
            'views':
            {
            'all':{"map":filemaker_map_fn},
            }
        })

    response = app_db.save(
        {
            "_id": '_design/examinations', 
            'views':
            {
            'new_examinations':{"map":filemaker_map_fn},
            'mp_number':{"map":filemaker_map_fn},
            }
        })
