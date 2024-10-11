"""Testing module for endpoint methods /entitlements."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class")
def entitlements(request):
    """Return the entitlements for the request."""
    return request.param if hasattr(request, "param") else None
