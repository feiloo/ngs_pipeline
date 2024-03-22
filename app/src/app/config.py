from typing import Optional
from pathlib import Path
from pydantic import BaseModel

import json

testconfig = {
        'couchdb_host': 'localhost',
        "couchdb_user":'testuser',
        'couchdb_psw':'testpsw',
        'clc_host': 'localhost',
        'clc_user': 'testuser',
        'clc_psw': 'testpsw',
        'filemaker_server':'',
        'filemaker_user':'',
        'filemaker_psw':'',
        'workflow_output_dir':'',
        'rabbitmq_user':'testuser',
        'rabbitmq_psw':'testpsw',
        'miseq_output_folder':'/data/private_testdata/miseq_output_testdata',
        "dev":'true',
        "app_secret_key": '_5#y2L"F4Q8z\n\xec]/'
        }


class ConfigParams(BaseModel):
    couchdb_host: str
    couchdb_user: str
    couchdb_psw: str
    clc_host: str
    clc_user: str
    clc_psw: str
    rabbitmq_user: str
    rabbitmq_psw: str
    filemaker_server: str
    filemaker_user: str
    filemaker_psw: str
    miseq_output_folder: str
    dev: bool
    app_secret_key: str
    workflow_output_dir: str
    backend: str = 'clc'

    # local path to clc ImportExport dir
    clc_import_export_dir: Optional[str]
    # clc path to clc inputs (clc_serverfile format to inportexport dir)
    clc_input_dir: Optional[str]
    # clc path to where clc outputs should be stored (clc object format)
    clc_output_dir: Optional[str]


class Config:
    _params = None
    _is_set = False

    def __init__(self):
        pass

    def set(self, dev: bool=False, path:Path=None):
        if self._is_set:
            raise RuntimeError('config is already set and should not be overwritten')

        self._is_set = True

        if dev == True:
            cfg = testconfig
        else:
            if path is None:
                p = Path('/etc/ngs_pipeline_config.json')
            else:
                p = path

            with p.open('r') as f:
                cfg = json.loads(f.read())

        self._params = ConfigParams(**cfg)

    def __contains__(self, k):
        return k in self.dict()

    def __getitem__(self, k):
        return self.dict()[k]

    def dict(self):
        if not self._is_set:
            raise RuntimeError('config wasnt set yet')
        return self._params.dict()

    @property
    def is_set(self):
        return self._is_set

    @property
    def celery_config(self):
        if not self._is_set:
            raise RuntimeError('config wasnt set yet')

        celery_config = { 
          'backend': f'couchdb://{self["couchdb_user"]}:{self["couchdb_psw"]}@localhost:5984/pipeline_results',
          'broker_url': f'pyamqp://{self["rabbitmq_user"]}:{self["rabbitmq_psw"]}@localhost//',
        }
        return celery_config

    def __str__(self):
        return str(self._params)

CONFIG = Config()
