from textwrap import indent
import requests
import pycouchdb as couch
import json

from app.model import *

NotFound = couch.exceptions.NotFound

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
                'last_synced_filemaker_row':0,
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
          emit([doc.filemaker_record.id,1], 1);
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
emit(doc._id, 1);
'''

examinations_count = basic_view('examinations_count', x, reducefn='_count', doctypes=['examination'])
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
  emit(doc._id, doc);
}
'''
new_examinations = basic_view('new_examinations', x, doctypes=['examination'])
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
    examinations,
    examinations_count,
    examinations_mp_number,
    new_examinations, 
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

def map_id(doc):
    id = doc.pop('_id')
    doc['id'] = id
    if '_rev' in doc:
        rev = doc.pop('_rev')
        doc['rev'] = rev
    else:
        doc['rev'] = None

    return doc

def unmap_id(doc):
    id = doc.pop('id')
    doc['_id'] = id
    if 'rev' in doc:
        rev = doc.pop('rev')
        if rev is not None:
            doc['_rev'] = rev

    return doc



def _wrap(doc):
    d = map_id(doc)
    if 'document_type' not in d:
        return d

    doctype = d['document_type']
    if doctype not in document_class_map.keys():
        return d

    cl = document_class_map[doctype]
    return cl(**d)


class QueryResult:
    ''' class to allow easier manipulation of couchdb view results '''
    def __init__(self, rows, should_wrap=False):
        self._rows = rows
        self._should_wrap = should_wrap

    def to_wrapped(self):
        return QueryResult(self.rows, should_wrap=True)

    def _wrap(self, x):
        if self._should_wrap:
            return _wrap(x)
        else:
            return x

    def ids(self):
        return [x['id'] for x in self._rows]

    def keys(self):
        return [x['key'] for x in self._rows]

    def values(self):
        return [self._wrap(x['value']) for x in self._rows]

    def docs(self):
        return [self._wrap(x['doc']) for x in self.rows]

    @property
    def rows(self):
        return self._rows


class Db:
    '''
    class that wraps pycouchdb to extend and adapt functionality
    '''

    server = None
    couchdb = None
    name = 'ngs_app'

    def __init__(self):
        pass

    def _check_con(self):
        if not self._check_initialized():
            raise RuntimeError('trying to connect to uninitialized database')
        if self.server is None:
            raise RuntimeError('trying to connect but Db server is None, ensure db connection was called')
        if self.couchdb is None:
            raise RuntimeError('trying to connect but Db client is None, ensure db connection was called')

    def _check_initialized(self):
        return self.name in self.server

    def __contains__(self, doc_id):
        return doc_id in self.couchdb

    def get(self, *args, **kwargs):
        self._check_con()
        return _wrap(self.couchdb.get(*args,**kwargs))

    def bulk_get(self, ids, *args, **kwargs):
        return [self.get(i) for i in ids]

    def _obj_to_d(self, obj):
        # forbid directly writing _id and _rev to prevent bugs where it isnt properly mapped

        if isinstance(obj, BaseDocument):
            # use json loads and model_dump_json instead of model_dump
            # because fields like date or path will not be stringified otherwise
            return unmap_id(json.loads(obj.model_dump_json()))
        elif isinstance(obj, dict):
            if '_id' in obj.keys():
                raise RuntimeError('explicitely setting _id is not allowed, use id instead')
            if '_rev' in obj.keys():
                raise RuntimeError('explicitely setting _rev is not allowed, use rev instead')
            return unmap_id(obj)
        else:
            raise RuntimeError('unsupported object: {obj} of type {type(obj)}')

    def save(self, *args, **kwargs):
        self._check_con()
        nargs = list(args)
        nargs[0] = self._obj_to_d(args[0])
        return self.couchdb.save(*nargs,**kwargs)

    def save_bulk(self, *args, **kwargs):
        self._check_con()
        nargs = list(args)
        nargs[0] = [self._obj_to_d(o) for o in args[0]]
        return self.couchdb.save_bulk(*nargs,**kwargs)

    def delete(self, *args, **kwargs):
        self._check_con()
        return self.couchdb.delete(*args,**kwargs)

    def query(self, *args, fields=['value'], **kwargs):
        self._check_con()
        if 'as_list' not in kwargs.keys():
            kwargs['as_list'] = True

        res = self.couchdb.query(*args,**kwargs)
        return QueryResult(res)


    #@staticmethod
    def init_db(self, config):
        server = couch.Server(_get_db_url(config))
        server.create(self.name)
        self.from_config(config)
        setup_views(self.couchdb)

        self.views = ddocs
        for doc in ddocs:
            self.couchdb.save(doc)


    def view(self, viewname, value=True):
        if value==True:
            res = self.query(viewname)
            return [x['value'] for x in res]


    #@staticmethod
    def from_config(self, config):
        if not config.is_set:
            raise RuntimeError('cant create db from config if config is not set yet')

        url = _get_db_url(config)
        self.server = couch.Server(url)
        self.couchdb = self.server.database(self.name)
        return Db()


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

#DB = Db.from_config(CONFIG)
DB = Db()
