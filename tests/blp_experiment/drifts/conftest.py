"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class")
def path(request, experiment_id):
    """Return the path for the request."""
    if hasattr(request, "param") and request.param:
        return request.param
    return f"/experiment/{experiment_id}/drift"


@fixture(scope="module")
def collection(database, experiment_id):
    """Return a collection connection to the database."""
    return database[f"app.{experiment_id}"]
