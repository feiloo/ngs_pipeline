import pycouchdb as couch
import pytest

from app.db import DB
from app.ui import create_app

import subprocess
import time

from app.tasks import start_pipeline
from app.app import main

from click.testing import CliRunner

podman_args = [ 'podman', 'run', '-d', '--rm' ]

@pytest.fixture(scope='session')
def couchdb_server():
    args = [ 'podman', 'stop', 'test_couchdb' ]
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
    yield server
    args = [ 'podman', 'stop', 'test_couchdb' ]
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


@pytest.fixture()
def app(db, config):
    app = create_app(config)
    app.config.update({
        "TESTING": True,
    })

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

@pytest.fixture()
def cli_runner():
    return CliRunner()

@pytest.fixture(scope='session')
def celery_config(config):
    return config.celery_config()

@pytest.mark.skip()
def test_start_pipeline():
    start_pipeline.apply_async(args=(dict(current_app.config['data']),))


@pytest.mark.skip()
@pytest.mark.celery()
def test_create_task(celery_app, celery_worker):
    pass

def test_create_document(db):
    init_doc = {"_id":"sequencer_runs", 
            "run_names": [],
            }

    app_db = db
    app_db.save(init_doc)

    #_start_pipeline(app_db)
    res = db.get('sequencer_runs')
    res.pop('_rev')
    assert res == init_doc

def test_pipeline_status(config, db):
    app_db = db 
    app = create_app(config)
    with app.test_client() as test_client:
        res = test_client.get('/pipeline_status')
        assert res.status_code == 200

@pytest.mark.incremental
class TestAppStart:
    def test_init_db(self, config, cli_runner):
        result = cli_runner.invoke(main, ['--dev','init'])
        assert result.exit_code == 0
