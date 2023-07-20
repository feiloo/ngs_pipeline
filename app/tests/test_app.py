import time
import subprocess
import signal

import pycouchdb as couch
import pytest

from app.tasks import start_pipeline
from app.app import main
from app.db import DB
from app.ui import create_app

from click.testing import CliRunner
from app.config import CONFIG, Config


@pytest.fixture()
def cli_runner():
    return CliRunner()

@pytest.mark.skip()
def test_start_pipeline():
    start_pipeline.apply_async(args=(dict(current_app.config['data']),))

@pytest.mark.skip()
@pytest.mark.celery()
def test_create_task(celery_app, celery_worker):
    pass


def test_pipeline_status(db, config):
    app_db = db 
    app = create_app(config)
    with app.test_client() as test_client:
        res = test_client.get('/pipeline_status')
        #assert res.status_code == 200


@pytest.mark.incremental
class TestAppCli:
    def test_init_db_dev(self, config, couchdb_server):
        # apparently the click tests runner is not thread safe, switching to subprocess
        #result = cli_runner.invoke(main, ['--dev','init'])
        proc = subprocess.run(['ngs_pipeline', '--dev', 'init'])
        exit_code = proc.returncode
        assert exit_code == 0
        assert 'ngs_app' in couchdb_server
        couchdb_server.delete('ngs_app')

    def test_worker(self, config, db):
        proc = subprocess.Popen(['ngs_pipeline', '--dev', 'worker'])
        time.sleep(5)
        proc.send_signal(signal.SIGINT)
        proc.wait()
        exit_code = proc.returncode
        assert exit_code == 0

    def test_run(self, config, db):
        proc = subprocess.Popen(['ngs_pipeline', '--dev', 'run'])
        time.sleep(5)
        proc.send_signal(signal.SIGINT)
        proc.wait()
        exit_code = proc.returncode
        assert exit_code == 0

    def test_beat(self, config, db):
        proc = subprocess.Popen(['ngs_pipeline', '--dev', 'beat'])
        time.sleep(5)
        proc.send_signal(signal.SIGINT)
        proc.wait()
        exit_code = proc.returncode
        assert exit_code == 0
