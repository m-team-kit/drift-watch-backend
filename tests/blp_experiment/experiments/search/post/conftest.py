"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class", name="response")
def request(client, path, request_kwds):
    """Create a request object."""
    # request_kwds contains the query, body, headers, auth, etc.
    yield client.post(path, **request_kwds)


@fixture(scope="class")
def body(request, created_at, name, permissions):
    """Inject and return a request body."""
    kwds = request.param if hasattr(request, "param") else {}
    if not isinstance(kwds, dict):
        return kwds  # Return the body as is
    for key, value in [
        ("created_at", created_at),
        ("name", name),
    ]:
        kwds.update({key: value} if value else {})
    kwds.update({f"permissions.{k}": r for k, r in permissions.items()})
    return kwds if kwds else None


@fixture(scope="class")
def created_after(request):
    """Inject and return the end date in iso format."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def created_before(request):
    """Inject and return the start date in iso format."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def created_at(request, created_after, created_before):
    """Inject and return a created_at filter."""
    datetime = request.param if hasattr(request, "param") else {}
    datetime.update({"$gte": created_after} if created_after else {})
    datetime.update({"$lte": created_before} if created_before else {})
    return datetime


@fixture(scope="class")
def name(request):
    """Inject and return a name filter."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def permissions(request):
    """Inject and return a permissions filter."""
    return request.param if hasattr(request, "param") else {}
