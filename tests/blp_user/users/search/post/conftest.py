"""Testing module for endpoint methods /user."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class", name="response")
def request(client, path, request_kwds):
    """Create a request object."""
    yield client.post(path, **request_kwds)


@fixture(scope="class")
def query(request, sort_by, order_by):
    """Inject and return a query string."""
    query = request.param if hasattr(request, "param") else {}
    if not isinstance(query, dict):
        return query
    if sort_by:
        query.update({"sort_by": sort_by})
    if order_by:
        query.update({"order_by": order_by})
    return query if query else None  # Return the query as is


@fixture(scope="class")
def sort_by(request):
    """Inject and return a sort_by string."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def order_by(request):
    """Inject and return an order_by string."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def body(request, created_at, filter_info):
    """Inject and return a request body."""
    kwds = request.param if hasattr(request, "param") else {}
    if not isinstance(kwds, dict):
        return kwds  # Return the body as is
    for key, value in [
        ("created_at", created_at),
        ("subject", filter_info.get("subject", None)),
        ("issuer", filter_info.get("issuer", None)),
        ("email", filter_info.get("email", None)),
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
def filter_info(request, subject, issuer, email):
    """Inject and returns user_info."""
    info = request.param if hasattr(request, "param") else {}
    info.update({"subject": subject} if subject else {})
    info.update({"issuer": issuer} if issuer else {})
    info.update({"email": email} if email else {})
    return info
