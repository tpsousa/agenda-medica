import pytest

from app import create_app
from app.extensions import db
from app.models import User


class TestConfig:
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_BASE_URL = "http://mock-api-test:5001"
    API_TIMEOUT = 1
    TESTING = True


@pytest.fixture
def app():
    application = create_app(TestConfig)
    with application.app_context():
        db.create_all()
        user = User(username="admin", email="admin@timesaver.com.br")
        user.set_password("admin123")
        db.session.add(user)
        db.session.commit()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, username="admin", password="admin123"):
    return client.post(
        "/auth/login",
        data={"identifier": username, "password": password},
        follow_redirects=True,
    )
