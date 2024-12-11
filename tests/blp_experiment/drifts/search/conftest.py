"""Testing module for endpoint methods .../drift/search."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class")
def path(request, experiment_id):
    """Return the path for the request."""
    if hasattr(request, "param") and request.param:
        return request.param
    return f"/experiment/{experiment_id}/drift/search"
