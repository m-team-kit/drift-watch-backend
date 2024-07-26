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

    def test_in_database(self, response, db_experiment):
        """Test the response items are in the database."""
        assert db_experiment is not None
        assert response.json == db_experiment

    def test_created_at(self, response):
        """Test the response item has a correct date."""
        assert dt.fromisoformat(response.json["created_at"])

    def test_subset(self, response, body):
        """Test the response includes the body."""
        assert set(body).issubset(set(response.json))

    def test_user_role(self, response, db_user):
        """Test the response item has the correct user role."""
        assert response.json["permissions"][db_user["id"]] == "Manage"


GROUP_1 = "00000000-0000-0002-0001-000000000001"
GROUP_2 = "00000000-0000-0002-0001-000000000002"
PERMISSIONS_1 = {GROUP_1: "Read", GROUP_2: "Edit"}


@mark.parametrize("name", ["new_name"], indirect=True)
@mark.parametrize("permissions", [PERMISSIONS_1], indirect=True)
class EditValues:
    """Test the item values match the request."""

    def test_name(self, response, name):
        """Test the response item has the correct name."""
        assert response.json["name"] == name

    def test_permissions(self, response, permissions, db_user):
        """Test the response item has the correct permissions."""
        permissions[db_user["id"]] = "Manage"  # Add the user to the permissions
        assert response.json["permissions"] == permissions


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
class TestEditExperiment1(EditValues, CommonBaseTests):
    """Test the responses items."""
