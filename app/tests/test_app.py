import couch.couch as couch
from app.app import _start_pipeline, create_app, get_db
from time import sleep
import pytest

@pytest.fixture()
def app():
    testconfig = {"couchdb_user":'testuser','couchdb_psw':'testpsw',
            'miseq_output_folder':'/data/private_testdata/miseq_output_testdata'
            }

    app = create_app(testconfig)
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield app

    # clean up / reset resources here


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


def test_request_example(client):
    response = client.get("/pipeline_status")


def test_db(app_db):
    init_doc = {"_id":"sequencer_runs", 
            "run_names": [],
            }

    res = app_db.put(init_doc)

    #_start_pipeline(app_db)
    res = app_db.get('sequencer_runs')
    init_doc.pop('_rev')
    res.pop('_rev')
    assert res == init_doc



def test_poll_sequencer_output(app_db):
    init_doc = {"_id":"sequencer_runs", 
            "run_names": [],
            }

    res = app_db.put(init_doc)

    _start_pipeline(app_db)
    res = app_db.get('sequencer_runs')
    assert res['run_names'] == ['220831_M03135_0376_000000000-KHR5V']


