"""Testing module for endpoint methods /user."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class", name="response")
def request(client, path, request_kwds):
    """Create a request object."""
    yield client.get(path, **request_kwds)


@fixture(scope="class")
def query(request, emails):
    """Inject and return a request query."""
    kwds = request.param if hasattr(request, "param") else {}
    if not isinstance(kwds, dict):
        return kwds  # Return the body as is
    kwds.update({"emails": emails} if emails is not None else {})
    kwds.update(request.param if hasattr(request, "param") else {})
    return kwds if kwds else None


@fixture(scope="class")
def emails(request):
    """Inject and return a emails filter."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def db_users(emails, collection):
    """Return a list of users from the database."""
    query = {"email": {"$in": emails}} if emails else {}
    return list(collection.find(query))
