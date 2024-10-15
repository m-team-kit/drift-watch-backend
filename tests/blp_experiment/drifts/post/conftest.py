"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class", name="response")
def request(client, path, request_kwds):
    """Create a request object."""
    yield client.post(path, **request_kwds)


@fixture(scope="class")
def body(request, schema_version, model, job_status, drifts):
    """Inject and return a request body."""
    kwds = request.param.copy() if hasattr(request, "param") else {}
    if not isinstance(kwds, dict):
        return kwds  # Return the body as is
    for key, value in [
        ("schema_version", schema_version),
        ("model", model),
        ("job_status", job_status),
    ]:
        kwds.update({key: value} if value else {})
    kwds.update(drifts if drifts else {})
    kwds.update(request.param if hasattr(request, "param") else {})
    return kwds if kwds else None


@fixture(scope="class")
def schema_version(request):
    """Inject and return a collection name."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def model(request):
    """Return an end date."""
    return request.param if hasattr(request, "param") else "model_a"


@fixture(scope="class")
def job_status(request):
    """Return a job status for the drift."""
    return request.param if hasattr(request, "param") else "Completed"


@fixture(scope="class")
def concept_drift(request):
    """Return a concept drift detection."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def data_drift(request):
    """Return a data drift detection."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def drifts(concept_drift, data_drift):
    """Return the drifts from the parameters as dict."""
    drifts = {}
    drifts.update({"concept_drift": concept_drift} if concept_drift else {})
    drifts.update({"data_drift": data_drift} if data_drift else {})
    return drifts if drifts else None
