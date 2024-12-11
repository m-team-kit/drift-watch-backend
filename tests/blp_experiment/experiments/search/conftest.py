"""Testing module for endpoint methods /experiment/search."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="module")
def path(request):
    """Return the path for the request."""
    return request.param if hasattr(request, "param") else "/experiment/search"
