"""Pytest configuration for testing the backend."""

# pylint: disable=redefined-outer-name
import json
import uuid

import mongomock
from flaat.user_infos import UserInfos
from pytest import fixture
from werkzeug.datastructures import Authorization

from app import create_app
from app.tools import authentication

MOCK_DATABASE_FILE = "tests/fixtures/database.json"


@fixture(scope="session")
def app():
    """Create and configure a new app instance for each test."""
    # See: https://flask.palletsprojects.com/en/3.0.x/testing/
    app = create_app(TESTING=True)
    app.config["db_client"] = mongomock.MongoClient()
    # other setup tasks can go here
    yield app
    # clean up after the test run


@fixture(scope="module", autouse=True)
def database(app):
    """Return the database from the application."""
    database_patch = f"test-{uuid.uuid4()}"
    app.config["db"] = app.config["db_client"][database_patch]
    return app.config["db"]


@fixture(scope="module")
def with_database(database):
    """Loads the database with data from data file."""
    with open(MOCK_DATABASE_FILE, "r", encoding="utf-8") as file:
        for section in json.load(file):
            database[section["collection"]].insert_many(section["items"])


@fixture(scope="module")
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@fixture(scope="module")
def with_context(app):
    """Return a context for the app."""
    with app.app_context() as context:
        yield context


@fixture(scope="class")
def request_kwds(request, auth, query, body):
    """Create a request kwds dict to complete."""
    kwds = {"query_string": query, "json": body, "auth": auth}
    kwds.update(request.param if hasattr(request, "param") else {})
    return kwds


@fixture(scope="class")
def auth(request):
    """Inject and return a request auth."""
    if request.param is None:
        return None
    return Authorization("bearer", token=request.param)


@fixture(scope="class")
def query(request):
    """Inject and return a request query."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def body(request):
    """Inject and return a request body."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def issuer(request):
    """Inject and return a request issuer in the token info."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class", params=["ai4eosc-null"])
def user_info(request):
    """User information send by the OP endpoint."""
    if not hasattr(request, "param"):
        return None
    config_path = f"tests/fixtures/user_infos/{request.param}.json"
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


@fixture(scope="class")
def accept_authorization(class_mocker, user_info, issuer):
    """Patches flaat to edit provided user_infos."""
    user_infos = UserInfos(
        access_token_info={"issuer": issuer} if issuer else None,
        user_info=user_info if user_info else {},
        introspection_info=None,
    )
    class_mocker.patch.object(
        authentication.flaat,
        "get_user_infos_from_access_token",
        return_value=user_infos,
    )


@fixture(scope="class")
def db_user(response, database, user_info):
    """Returns user from database after response."""
    db_filter = {"subject": user_info["sub"], "issuer": user_info["iss"]}
    user = database["app.users"].find_one(db_filter)
    if user is not None:
        user["id"] = user.pop("_id")
    return user
