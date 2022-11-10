import couch.couch as couch
from app.app import _start_pipeline, create_app
from time import sleep
import pytest


def test_start_pipeline():
    test_config = {"couch_user":"testuser", "couch_psw":"testpsw"}
    class App():
        pass

    app = App()
    app.testing = True

    '''
    app = create_app(test_config)
    app.config.update({
        "TESTING": True,
        })
    '''
    auth = couch.BasicAuth('testuser', 'testpsw')
    server = couch.Server('localhost', port=8001, auth=auth)
    res = server.create_db('ngs_app')

    app_db = server.get_db('ngs_app')

    init_doc = {"_id":"sequencer_runs", 
            "run_names": [],
            }

    res = app_db.put(init_doc)

    _start_pipeline(app_db)
    res = app_db.get('sequencer_runs')
