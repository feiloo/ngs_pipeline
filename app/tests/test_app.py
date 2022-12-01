import couch.couch as couch
from app.app import _start_pipeline, create_app, get_db
from time import sleep
import pytest

@pytest.fixture()
def config():
    testconfig = {"couchdb_user":'testuser','couchdb_psw':'testpsw',
            'miseq_output_folder':'/data/private_testdata/miseq_output_testdata'
            }
    return testconfig

@pytest.fixture()
def db(config):
    auth = couch.BasicAuth(config['couchdb_user'], config['couchdb_psw'])
    server = couch.Server('localhost', port=8001, auth=auth)
    app_db = server.create_db('ngs_app')
    return app_db


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


'''
def test_request_example(client):
    response = client.get("/pipeline_status")
'''


def test_create_document(app_db):
    init_doc = {"_id":"sequencer_runs", 
            "run_names": [],
            }

    res = app_db.put(init_doc)

    #_start_pipeline(app_db)
    res = app_db.get('sequencer_runs')
    assert res == init_doc



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
