"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class", name="response")
def request(client, path, request_kwds):
    """Create a request object."""
    yield client.put(path, **request_kwds)


@fixture(scope="class")
def body(request, name, permissions):
    """Inject and return a request body."""
    kwds = {}  # Update the body with the test parameters
    for key, value in [
        ("name", name),
        ("permissions", permissions),
    ]:
        kwds.update({key: value} if value else {})
    kwds.update(request.param if hasattr(request, "param") else {})
    return kwds if kwds else None


@fixture(scope="class")
def name(request):
    """Inject and return a name filter."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def permissions(request):
    """Inject and return a permissions filter."""
    return request.param if hasattr(request, "param") else None
