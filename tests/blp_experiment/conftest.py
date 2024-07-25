"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class")
def experiment_id(request):
    """Return Experiment id from request param."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def db_experiment(response, database, experiment_id):
    """Return the item from the database."""
    _id = experiment_id or response.json["id"]
    item = database["app.experiments"].find_one({"_id": _id})
    if item is not None:
        item["id"] = item.pop("_id")
    return item


@fixture(scope="class")
def drift_id(request):
    """Return Drift id from request param."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def db_drift(response, database, experiment_id, drift_id):
    """Return the item from the database."""
    _id = drift_id or response.json["id"]
    item = database[f"app.{experiment_id}"].find_one({"_id": _id})
    if item is not None:
        item["id"] = item.pop("_id")
    return item
