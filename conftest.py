import pytest

from api import create_app
from api.models import db


@pytest.fixture
def application():
    app = create_app(config_mode='test')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(application):
    return application.test_client()
