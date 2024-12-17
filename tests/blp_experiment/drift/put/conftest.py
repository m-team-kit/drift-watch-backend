"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class", name="response")
def request(client, path, request_kwds):
    """Create a request object."""
    yield client.put(path, **request_kwds)


@fixture(scope="class")
def body(request, job_status, tags, model, detected, parameters):
    """Inject and return a request body."""
    kwds = request.param.copy() if hasattr(request, "param") else {}
    if not isinstance(kwds, dict):
        return kwds  # Return the body as is
    for key, value in [
        ("job_status", job_status),
        ("tags", tags),
        ("model", model),
        ("drift_detected", detected),
        ("parameters", parameters),
    ]:
        kwds.update({key: value} if value is not None else {})
    kwds.update(request.param if hasattr(request, "param") else {})
    return kwds if kwds else None


@fixture(scope="class")
def job_status(request):
    """Return a job status for the drift."""
    return request.param if hasattr(request, "param") else "Completed"


@fixture(scope="class")
def tags(request):
    """Inject and return tags."""
    return request.param if hasattr(request, "param") else ["tag_1"]


@fixture(scope="class")
def model(request):
    """Return the model name for the drift."""
    return request.param if hasattr(request, "param") else "model_a"


@fixture(scope="class")
def detected(request):
    """Inject and return a drift detection."""
    return request.param if hasattr(request, "param") else False


@fixture(scope="class")
def parameters(request):
    """Return a data drift detection."""
    if hasattr(request, "param"):
        return request.param
    return {"p_value": 0.1}
