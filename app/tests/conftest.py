import time
from typing import Dict, Tuple
import subprocess

import pytest
import pycouchdb as couch

from app.constants import testconfig
from app.config import Config
from app.app import main
from app.ui import create_app
from app.tasks import start_pipeline
from app.db import DB




# marker for incremental tests, see https://docs.pytest.org/en/7.1.x/example/simple.html 


# store history of failures per test class name and per index in parametrize (if parametrize used)
_test_failed_incremental: Dict[str, Dict[Tuple[int, ...], str]] = {}


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        # incremental marker is used
        if call.excinfo is not None:
            # the test has failed
            # retrieve the class name of the test
            cls_name = str(item.cls)
            # retrieve the index of the test (if parametrize is used in combination with incremental)
            parametrize_index = (
                tuple(item.callspec.indices.values())
                if hasattr(item, "callspec")
                else ()
            )
            # retrieve the name of the test function
            test_name = item.originalname or item.name
            # store in _test_failed_incremental the original name of the failed test
            _test_failed_incremental.setdefault(cls_name, {}).setdefault(
                parametrize_index, test_name
            )


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        # retrieve the class name of the test
        cls_name = str(item.cls)
        # check if a previous test has failed for this class
        if cls_name in _test_failed_incremental:
            # retrieve the index of the test (if parametrize is used in combination with incremental)
            parametrize_index = (
                tuple(item.callspec.indices.values())
                if hasattr(item, "callspec")
                else ()
            )
            # retrieve the name of the first test function to fail for this class name and index
            test_name = _test_failed_incremental[cls_name].get(parametrize_index, None)
            # if name found, test has failed for the combination of class name & test name
            if test_name is not None:
                pytest.xfail("previous test failed ({})".format(test_name))


@pytest.fixture(scope='session')
def config():
    return Config(dev=True)



''' sythetic example record
'''
fm_record = {'fieldData': {
        'lf_Untersuchung_ID': 49999, 
        'Zeitstempel': '12/24/2020', 
        'Mol_NR': 4000, 
        'FISH_ NR': '', 
        'Kürzel': 'E ', 
        'Nummer': 18000, 
        'Jahr': 2020, 
        'Block_NR': 'XX X0.0.0X', 
        'Untersuchung': 'BRAF Ex11', 
        'Befunder': 'X', 
        'Ergebnis': '', 
        'Zeitstempel_ Ergebnis': '', 
        'ADR1::DBCKOMFORT': '', 
        'Vorname': '',
        'Name': '',
        'GBD': '12/24/2020',
        'Abrechnungsziffer': '',
        'Bemerkung': '',
        'Erledigt_Abrechnung': 'nein',
        'Barcode': 'E 00.00000',
        'global_lokal::next Mol Nr': 4021,
        'global_lokal::Untersuchung': 'XXXX',
        'global_lokal::next FISH Nr': 0,
        'DBCARZTORG': '',
        'DBCARZTKOP': '', 
        'Kürzel_JK_MT': '',
        'Kürzel_Erfassung': 'XX',
        'global_lokal::gl_Kuerzel_Erfasser': 'XX',
        'global_lokal::gl_Befunder': '',
        'global_lokal::gl_Jahr': '20',
        'Barcode_automatisch': 'E 1111111',
        'Geschlecht': 'M',
        'Leerschnitte': 3,
        'TZAnteil': 80,
        'Markierer': 'XX',
        'Diagnose': '',
        'Primarius_Metastase': '',
        'Lokalisation': '',
        'ICD10': '',
        'ICD03': ''
        },
    'portalData': {},
    'recordId': '40000',
    'modId': '9'
    }

@pytest.fixture()
def filemaker_testdata():
    return fm_record

class FilemakerMock:
    def __init__(self, *args, **kwargs):
        pass

    def get_all_records(self, offset, limit=1000):
        print(f'offset: {offset}')
        if offset > 50000:
            raise RuntimeError('offset in filemaker mock reached all documents')
        return {'data': [fm_record]}


@pytest.fixture()
def fm_mock():
    return FilemakerMock()


podman_args = [ 'podman', 'run', '-d']#, '--rm' ]

@pytest.fixture(scope='session')
def couchdb_server():
    args = [ 'podman', 'stop', '-i', 'test_couchdb' ]
    subprocess.run(args)

    args = [ 'podman', 'rm', '-v', 'test_couchdb' ]
    subprocess.run(args)

    args = podman_args + [
        '--name=test_couchdb', 
        '-e', 'COUCHDB_USER=testuser', 
        '-e', 'COUCHDB_PASSWORD=testpsw', 
        '-p', '5984:5984', 
        'docker.io/apache/couchdb'
        ]
    proc = subprocess.run(args)
    # sleep enough until couchdb is online
    time.sleep(3)

    user = 'testuser'
    psw = 'testpsw'
    host = 'localhost'
    port = 5984
    url = f"http://{user}:{psw}@{host}:{port}"

    server = couch.Server(url)
    # get info to ensure that server is ready
    server.info()
    yield server
    args = [ 'podman', 'stop', 'test_couchdb' ]
    subprocess.run(args)
    args = [ 'podman', 'rm', '-v', 'test_couchdb' ]
    subprocess.run(args)
    time.sleep(3)


@pytest.fixture()
def rabbitmq_server(config):
    args = podman_args + [
        '--name=test_rabbitmq', 
	'-p', '5672:5672',
	'--hostname', 'my-rabbit',
	'-e', 'RABBITMQ_DEFAULT_USER=testuser',
	'-e', 'RABBITMQ_DEFAULT_PASS=testpsw',
	'docker.io/rabbitmq:3-management'
        ]

    proc = subprocess.run(args)
    # sleep enough until rabbitmq is online
    time.sleep(3)
    yield proc
    args = [ 'podman', 'stop', 'test_rabbitmq' ]
    subprocess.run(args)
    time.sleep(3)


@pytest.fixture()
def db(couchdb_server, config):
    s = couchdb_server
    db = DB.init_db(config)
    yield db
    res = s.delete('ngs_app')


@pytest.fixture(scope='session')
def celery_config(config):
    return config.celery_config()

