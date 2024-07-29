"""Testing module for endpoint methods /group/<id>."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class")
def path(request, group_id):
    """Return the path for the request."""
    if hasattr(request, "param") and request.param:
        return request.param
    return f"/group/{group_id}"


@fixture(scope="module")
def collection(database):
    """Return a collection connection to the database."""
    return database["app.groups"]
