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
    app_secret_key: bytes
    workflow_output_dir: str


class Config:
    def __init__(self, dev: bool=False, path:Path=None):
        if dev == True:
            cfg = testconfig

        if path is None:
            p = Path('/etc/ngs_pipeline_config.json')
        else:
            p = path

        with p.open('r') as f:
            cfg = json.loads(f.read())

        self.params = ConfigParams(**cfg)

    def dict(self):
        return self.params.dict()


