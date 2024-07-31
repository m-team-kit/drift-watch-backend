"""Testing module for endpoint methods /user."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class", name="response")
def request(client, path, request_kwds):
    """Create a request object."""
    yield client.get(path, **request_kwds)


@fixture(scope="class")
def body(request, created_at, user_info):
    """Inject and return a request body."""
    kwds = request.param if hasattr(request, "param") else {}
    if not isinstance(kwds, dict):
        return kwds  # Return the body as is
    for key, value in [
        ("created_at", created_at),
        ("subject", user_info.get("subject", None)),
        ("issuer", user_info.get("issuer", None)),
        ("email", user_info.get("email", None)),
    ]:
        kwds.update({key: value} if value else {})
    kwds.update(request.param if hasattr(request, "param") else {})
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
def subject(request):
    """Inject and return a subject filter."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def issuer(request):
    """Inject and return a subject filter."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def email(request):
    """Inject and return a subject filter."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def user_info(request, subject, issuer, email):
    """Inject and returns user_info."""
    info = request.param if hasattr(request, "param") else {}
    info.update({"subject": subject} if subject else {})
    info.update({"issuer": issuer} if issuer else {})
    info.update({"email": email} if email else {})
    return info
