from pathlib import Path
from pydantic import BaseModel

from app.constants import testconfig
import json


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
    dev: str
    app_secret_key: str
    workflow_output_dir: str


class Config:
    def __init__(self, dev: bool=False, path:Path=None):
        if dev == True:
            cfg = testconfig
        else:
            if path is None:
                p = Path('/etc/ngs_pipeline_config.json')
            else:
                p = path

            with p.open('r') as f:
                cfg = json.loads(f.read())

        self.params = ConfigParams(**cfg)

    def __getitem__(self, k):
        return self.dict()[k]

    def dict(self):
        return self.params.dict()

    def celery_config(self):
        celery_config = { 
          'backend': f'couchdb://{self["couchdb_user"]}:{self["couchdb_psw"]}@localhost:5984/pipeline_results',
          'broker': f'pyamqp://{self["rabbitmq_user"]}:{self["rabbitmq_psw"]}@localhost//',
        }
        return celery_config
