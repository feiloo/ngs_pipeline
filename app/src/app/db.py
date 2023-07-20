from textwrap import indent
import requests
import pycouchdb as couch

def ind(x):
    ''' hardcoded indent for convenience '''
    return indent(x, "  ")

def iffn(h, b):
    ''' javascript if function '''
    fn = "if (" + h + ") {\n" + ind(b) + "\n}"
    return fn

def fnfn(b):
    ''' javascript function function'''
    fn = "function (doc) {\n" + ind(b) + "\n}"
    return fn

def gen_map_fn_str(body, doctypes=None, deleted=False):
    """ generate a map function

    body is the script body inside the map function
    doctype can be a list of allowed document types for the view
    deleted=False filters deleted documents from mapfn

    """

    mapfn = body

    if doctypes is not None:
        hd = "||".join([f"doc.document_type === '{d}'" for d in doctypes])
        h = f"doc.document_type && ({hd})"
        mapfn = iffn(h, mapfn)

    if deleted == False:
        mapfn = iffn("!doc.deleted", mapfn)

    mapfn = fnfn(mapfn)
    return mapfn



class DesignDoc:
    def __init__(self, name, views):
        self.name = name
        self.views = views

    def to_dict(self):
        design_doc_views = {}
        for view in self.views:
            design_doc_views[view.name] = view.functions()

        design_doc_dict = {"_id":"_design/"+self.name,
            "views": design_doc_views
            }
        return design_doc_dict

    def add_view(self, view):
        self.views += view

    def __str__(self):
        return f"DesignDoc: {self.to_dict()}"



class View:
    def __init__(self, name, mapfn, reducefn=None):
        self.name = name
        self.mapfn = mapfn
        self.reducefn = reducefn

    def functions(self):
        if self.reducefn is not None:
            return {"map":self.mapfn, "reduce":self.reducefn}
        else:
            return {"map":self.mapfn}

    def __str__(self):
        return f"View: {self.name}, {self.functions()}"


def basic_view(name, map_body, reducefn=None, doctypes=None, deleted=False):
    ''' generate a view with some useful defaults '''
    map_fn_str = gen_map_fn_str(map_body, doctypes, deleted)
    return View(name, map_fn_str, reducefn)


def setup_views(app_db):
    if 'app_state' not in app_db:
        app_state = {
                '_id': 'app_state',
                'last_synced_filemaker_row':-1,
                'sync_running': False
                }

        app_db.save(app_state)

    if 'app_settings' not in app_db:
        default_app_settings = {
            '_id':'app_settings',
            'schedule': [''],
            'autorun_pipeline':True
        }

        app_db.save(default_app_settings)


    sequencer_map_fn = '''
    function (doc) {
      if(doc.document_type){
        if(doc.document_type == 'sequencer_run')
          emit(doc.parsed.date, doc);
          }
      }
    '''

    sample_map_fn = '''
    function (doc) {
      if(doc.document_type){
        if(doc.document_type == 'sample')
          emit(doc._id, doc);
          }
      }
    '''
    pipeline_map_fn = '''
    function (doc) {
      if(doc.document_type){
        if(doc.document_type == 'pipeline_run')
          emit(doc.created_time, doc);
          }
      }
    '''

    filemaker_map_fn = '''
    function (doc) {
      if(doc.document_type){
        if(doc.document_type == 'filemaker_record'){
          emit([doc._id,0], 0);
        }
        else if(doc.document_type == 'examination'){
          emit([doc.filemaker_record._id,1], 1);
        }
      }
    }
    '''
    filemaker_reduce_fn = '''
    function (keys, values, rereduce) {
      return sum(values);
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
            'all':{"map":filemaker_map_fn,
                   "reduce":filemaker_reduce_fn
                    },
            }
        })


ddocs = []

x = '''
emit(doc.started_date, doc);
'''
examinations = basic_view('examinations', x, doctypes=['examination'])
del x

x = '''
for(var i=0; i<doc.sequencer_runs.length; i++) {
  emit(doc.sequencer_runs[i]._id, doc._id);
}
'''
examinations_sequencer_runs = basic_view('sequencer_runs', x, doctypes=['examination'])
del x

x = '''
if(doc.pipeline_runs.length === 0 && doc.sequencer_runs.length > 0){
  emit(doc, null);
}
'''
unfinished_examinations = basic_view('unfinished', x, doctypes=['examination'])
del x

x = '''
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
'''
examinations_mp_number = basic_view('mp_number', x, doctypes=['examination'])
del x

examinations_ddoc = DesignDoc('examinations', [
    unfinished_examinations, 
    examinations,
    examinations_mp_number
    ]).to_dict()
ddocs.append(examinations_ddoc)


x = '''
if(doc.document_type == 'examination'){
  emit([doc.filemaker_record.Name, doc.filemaker_record.Vorname, doc.filemaker_record.GBD, doc._id], doc._id);
  }
if(doc.document_type == 'patient'){
  emit([doc.names.firstname, doc.names.lastname, doc.birthdate, doc._id], doc._id);
  }
'''
patient_aggregation = basic_view('patient_aggregation', x)
del x

x = '''
emit(doc._id, doc);
'''
patient = basic_view('patients', x, doctypes=['patient'])
del x

patients_ddoc = DesignDoc('patients', [patient_aggregation, patient]).to_dict()
ddocs.append(patients_ddoc)


def _get_db_url(config):
    user = config['couchdb_user']
    psw = config['couchdb_psw']
    host = 'localhost'
    port = 5984
    url = f"http://{user}:{psw}@{host}:{port}"
    return url


class DB(couch.client.Database):
    @staticmethod
    def init_db(config):
        server = couch.Server(_get_db_url(config))
        server.create('ngs_app')
        db = DB.from_config(config)

        setup_views(db)

        db.views = ddocs
        for doc in ddocs:
            db.save(doc)
        #res = db.save_bulk(ddocs)

        return db

    def view(self, viewname, value=True):
        if value==True:
            res = self.query(viewname, as_list=True)
            return [x['value'] for x in res]


    @staticmethod
    def from_config(config):
        url = _get_db_url(config)
        server = couch.Server(url)
        #app_db = server.database('ngs_app')
        name = 'ngs_app'

        # origin from https://github.com/histrio/py-couchdb/blob/919f2f36a2b11c3e460f2014c20c106c0db11523/pycouchdb/client.py#L157
        (r, result) = server.resource.head(name)
        if r.status_code == 404:
                raise exp.NotFound("Database '{0}' does not exists".format(name))

        db = DB(server.resource(name), name)
        return db

    def save_obj(self, obj):
        ''' save the pydantic object '''
        o = self.save(obj.to_dict())
        return obj.from_dict(o)


def get_db_url(app):
    host = app.config['data']['couchdb_host']
    user = app.config['data']['couchdb_user']
    psw = app.config['data']['couchdb_psw']
    port = 5984
    url = f"http://{user}:{psw}@{host}:{port}"
    return url

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
