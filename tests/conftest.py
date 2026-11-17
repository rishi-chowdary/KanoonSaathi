import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.models.user import User


@pytest.fixture(scope="session")
def app():
    """Create and configure a Flask app for testing."""
    test_app = create_app(TestConfig)
    with test_app.app_context():
        db.create_all()
    yield test_app
    with test_app.app_context():
        db.drop_all()


@pytest.fixture(autouse=True)
def clean_database(app):
    """Ensure database is clean before each test."""
    with app.app_context():
        db.session.rollback()
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
    yield


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create and persist a standard test user."""
    with app.app_context():
        user = User(
            email="lawyer@example.com",
            full_name="Sarah Jenkins",
            role="USER",
        )
        user.set_password("SecurePassword123!")
        db.session.add(user)
        db.session.commit()
        return db.session.get(User, user.id)
