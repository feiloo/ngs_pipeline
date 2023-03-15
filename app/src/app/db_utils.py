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
        emit(doc._id, doc);
        }
    '''

    examinations = '''
    function (doc) {
      if(doc.document_type){
	if(doc.document_type == 'examination'){
	  emit(doc._id, doc);
	}
      }
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
      if (doc.document_type && (doc.document_type === 'examination')){
	      const u = [
		'DNA Lungenpanel Qiagen - kein nNGM Fall',
		'DNA Panel ONCOHS',
		'DNA PANEL ONCOHS (Mamma)',
		'DNA PANEL ONCOHS (Melanom)',
		'DNA PANEL ONCOHS (Colon)',
		'DNA PANEL ONCOHS (GIST)',
		'DNA PANEL Multimodel PanCancer DNA',
		'DNA PANEL Multimodel PanCancer RNA',
		'NNGM Lunge Qiagen',
		'RNA Fusion Lunge',
		'RNA Sarkompanel'
		];
	      if (u.includes(doc.filemaker_record.Untersuchung)){
		emit([doc.filemaker_record.Jahr, doc.filemaker_record.Mol_NR], doc);
	      }
      }
    }
    '''

    patient_map_fn = '''
    function (doc) {
      if(doc.document_type == 'patient'){
        emit(doc._id, doc);
        }
    }
    '''

    patient_aggregation_fn = '''
    function (doc) {
      if(doc.document_type == 'filemaker_record'){
        emit([doc.Name, doc.Vorname, doc.GBD], doc);
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
            'new_examinations':{"map":examinations_new_cases},
            'examinations':{"map":examinations},
            'mp_number':{"map":examinations_mp_number},
            }
        })

    response = app_db.save(
        {
            "_id": '_design/patients', 
            'views':
            {
            'patient_aggregation':{"map":patient_aggregation_fn},
            'patients':{"map":patient_map_fn},
            }
        })