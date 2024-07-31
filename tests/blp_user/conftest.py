"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class")
def user_id(request):
    """Return User id from request param."""
    return request.param if hasattr(request, "param") else None
