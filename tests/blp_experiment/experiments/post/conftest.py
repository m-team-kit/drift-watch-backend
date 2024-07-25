"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class", name="response")
def request(client, path, request_kwds):
    """Create a request object."""
    yield client.post(path, **request_kwds)


@fixture(scope="class")
def body(request, name, permissions):
    """Inject and return a request body."""
    kwds = request.param if hasattr(request, "param") else {}
    if not isinstance(kwds, dict):
        return kwds  # Return the body as is
    for key, value in [
        ("name", name),
        ("permissions", permissions),
    ]:
        kwds.update({key: value} if value else {})
    return kwds if kwds else None


@fixture(scope="class")
def name(request):
    """Inject and return a name filter."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def permissions(request):
    """Inject and return a permissions filter."""
    return request.param if hasattr(request, "param") else None
