"""Testing module for endpoint methods /group/s."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class")
def group_id(request):
    """Return Group id from request param."""
    return request.param if hasattr(request, "param") else None


@fixture(scope="class")
def db_group(response, database, group_id):
    """Return the item from the database."""
    _id = group_id or response.json["id"]
    item = database["app.groups"].find_one({"_id": _id})
    if item is not None:
        item["id"] = item.pop("_id")
    return item
