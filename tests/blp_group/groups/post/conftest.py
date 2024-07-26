"""Testing module for endpoint methods /group."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class", name="response")
def request(client, path, request_kwds):
    """Create a request object."""
    yield client.post(path, **request_kwds)


@fixture(scope="class")
def body(request, name, members):
    """Inject and return a request body."""
    kwds = request.param if hasattr(request, "param") else {}
    if not isinstance(kwds, dict):
        return kwds  # Return the body as is
    for key, value in [
        ("name", name),
        ("members", members),
    ]:
        kwds.update({key: value} if value else {})
    return kwds if kwds else None


@fixture(scope="class")
def name(request):
    """Inject and return a name value."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def members(request):
    """Inject and return a members value."""
    return request.param if hasattr(request, "param") else None
