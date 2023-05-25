
import time
from typing import Dict, Tuple
import subprocess

import pytest
from click.testing import CliRunner
import pycouchdb as couch

from app.constants import testconfig
from app.config import Config
from app.app import main
from app.ui import create_app
from app.tasks import start_pipeline
from app.db import DB

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
