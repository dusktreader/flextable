import flask
import flask_sqlalchemy
import flextable
import os
import pytest


@pytest.fixture(scope="session")
def app():
    """
    Create a Flask app context for the tests.
    """
    app = flask.Flask(__name__)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+psycopg2://postgres@localhost:5432/flextable_test",
    )
    return app


@pytest.fixture(scope="session")
def db(app):
    """
    Provide the transactional fixtures with access to the database via a
    Flask-SQLAlchemy database connection.
    """
    db = flask_sqlalchemy.SQLAlchemy(app=app)
    return db


@pytest.fixture(scope="session")
def models(db):
    class DummySet(flextable.SetTableMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.Text, unique=True, nullable=False, index=True)
        description = db.Column(db.Text)

    DummySet.bind_db(db)

    class DummyFlex(flextable.FlexTableMixin, db.Model):

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.Text, unique=True, nullable=False, index=True)
        description = db.Column(db.Text)

    DummyFlex.bind_db(db)

    return (DummySet, DummyFlex)


@pytest.fixture(scope="session", autouse=True)
def create_all(db, models):
    (Dumb, Flex) = models
    db.create_all()
    yield
    db.drop_all()


@pytest.fixture(scope="function", autouse=True)
def session(app, db):
    with app.app_context():
        db.session.begin_nested()
        yield
        db.session.rollback()
