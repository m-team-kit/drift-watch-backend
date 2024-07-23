"""Testing module for endpoint methods /experiment/<id>."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class")
def path(request, experiment_id):
    """Return the path for the request."""
    if hasattr(request, "param") and request.param:
        return request.param
    return f"/experiment/{experiment_id}"


@fixture(scope="module")
def collection(database):
    """Return a collection connection to the database."""
    return database["app.experiments"]


@fixture(scope="class")
def experiment_id(request):
    """Return Experiment id from request param."""
    return request.param
