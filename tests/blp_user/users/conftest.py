"""Testing module for endpoint methods /user."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="module")
def path(request):
    """Return the path for the request."""
    return request.param if hasattr(request, "param") else "/user"


@fixture(scope="module")
def collection(database):
    """Return a collection connection to the database."""
    return database["app.users"]
