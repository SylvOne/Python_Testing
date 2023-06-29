import pytest
from Python_Testing.server import app, loadClubs, loadCompetitions


@pytest.fixture(scope='function')
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(scope='function')
def competitions():
    return loadCompetitions()


@pytest.fixture(scope='function')
def clubs():
    return loadClubs()
