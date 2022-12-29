import pycouchdb as couch
from app.app import create_app, get_db, testconfig, init
from time import sleep
import pytest

import subprocess
import time

from app.tasks import get_celery_config, start_pipeline

from click.testing import CliRunner

podman_args = [ 'podman', 'run', '-d', '--rm' ]
@pytest.fixture(scope='session')
def config():
    return testconfig

@pytest.fixture(scope='session')
def couchdb_server(config):
    args = podman_args + [
        '--name=test_couchdb', 
        '-e', 'COUCHDB_USER=testuser', 
        '-e', 'COUCHDB_PASSWORD=testpsw', 
        '-p', '8001:5984', 
        'docker.io/apache/couchdb'
        ]
    proc = subprocess.run(args)
    # sleep enough until couchdb is online
    time.sleep(3)

    user = 'testuser'
    psw = 'testpsw'
    host = 'localhost'
    port = 8001
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
def db(config, couchdb_server):
    app_db = couchdb_server.create('ngs_app')
    yield app_db
    couchdb_server.delete('ngs_app')


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
def app_db(app):
    with app.app_context():
        return get_db(app)


@pytest.fixture(scope='session')
def celery_config(config):
    return get_celery_config(config)

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

    print(db)
    db.save(init_doc)

    #_start_pipeline(app_db)
    res = db.get('sequencer_runs')
    res.pop('_rev')
    assert res == init_doc



def test_db_init(db):
    runner = CliRunner()
    result = runner.invoke(init, ['--init'])

'''
def test_poll_sequencer_output(app_db, app):
    init_doc = {"_id":"sequencer_runs", 
            "run_names": [],
            }

    res = app_db.put(init_doc)

    with app.app_context():
        _start_pipeline(app_db)
        res = app_db.get('sequencer_runs')
        assert res['run_names'] == ['220831_M03135_0376_000000000-KHR5V']
'''




'''
with open('~/fm_example_record.json', 'r') as f:
    example_record = json.loads(f.read().replace("'", '"'))
'''
