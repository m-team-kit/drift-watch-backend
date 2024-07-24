"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt

from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /experiment endpoint."""

    def test_status_code(self, response):
        """Test the 200 response."""
        assert response.status_code == 200

    def test_in_database(self, response, db_item):
        """Test the response items are in the database."""
        assert db_item is not None
        assert response.json == db_item

    def test_created_at(self, response):
        """Test the response item has a correct date."""
        assert dt.fromisoformat(response.json["created_at"])

    def test_subset(self, response, body):
        """Test the response includes the body."""
        assert set(body).issubset(set(response.json))


class EditName:
    """Test the response items."""

    def test_name(self, response, name):
        """Test the response item has the correct name."""
        assert response.json["name"] == name


class EditPermissions:
    """Test the response items."""

    def test_permissions(self, response, permissions):
        """Test the response item has the correct permissions."""
        assert response.json["permissions"] == permissions


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"
PERMISSIONS_1 = [
    {"group_id": "00000000-0000-0002-0001-000000000001", "role": "Read"},
    {"group_id": "00000000-0000-0003-0001-000000000001", "role": "Manage"},
]


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
@mark.parametrize("name", ["new_name"], indirect=True)
@mark.parametrize("permissions", [PERMISSIONS_1], indirect=True)
class TestEditExperiment1(EditName, CommonBaseTests):
    """Test the responses items."""
