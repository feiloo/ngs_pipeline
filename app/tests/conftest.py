import pytest

from app.constants import testconfig

@pytest.fixture(scope='session')
def config():
    return testconfig


