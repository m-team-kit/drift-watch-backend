"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class", name="response")
def request(client, path, request_kwds):
    """Create a request object."""
    yield client.post(path, **request_kwds)


@fixture(scope="class")
def body(request, schema_version, created_at, model_info, drifts):
    """Inject and return a request body."""
    kwds = request.param if hasattr(request, "param") else {}
    if not isinstance(kwds, dict):
        return kwds  # Return the body as is
    for key, value in [
        ("schema_version", schema_version),
        ("created_at", created_at),
        ("job_status", model_info["job_status"]),
        ("model", model_info["model"]),
        ("concept_drift", drifts["concept_drift"]),
        ("data_drift", drifts["data_drift"]),
    ]:
        kwds.update({key: value} if value else {})
    kwds.update(request.param if hasattr(request, "param") else {})
    return kwds if kwds else None


@fixture(scope="class")
def schema_version(request):
    """Inject and return a collection name."""
    return request.param if hasattr(request, "param") else None


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
def job_status(request):
    """Inject and return a job status."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def model(request):
    """Inject and return a drift detection type."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def model_info(model, job_status):
    """Return the model info from the parameters as dict."""
    return {"model": model, "job_status": job_status}


@fixture(scope="class")
def concept_drift(request):
    """Inject and return a concept drift detection type."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def data_drift(request):
    """Inject and return a data drift detection type."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def drifts(concept_drift, data_drift):
    """Return the drifts from the parameters as dict."""
    return {"concept_drift": concept_drift, "data_drift": data_drift}
