"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import fixture


@fixture(scope="class")
def db_item(response, collection):
    """Return the item from the database."""
    item = collection.find_one({"_id": response.json["id"]})
    if item is not None:
        item["id"] = item.pop("_id")
    return item
