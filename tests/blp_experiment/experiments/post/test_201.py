"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
import uuid
from datetime import datetime as dt

from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /experiment endpoint."""

    def test_status_code(self, response):
        """Test the 201 response."""
        assert response.status_code == 201

    def test_in_database(self, response, db_item):
        """Test the response items are in the database."""
        assert db_item is not None
        assert response.json == db_item

    def test_experiment_id(self, response):
        """Test the response item have correct id."""
        assert uuid.UUID(response.json["id"]).version == 4

    def test_created_at(self, response):
        """Test the response item has a correct date."""
        assert dt.fromisoformat(response.json["created_at"])

    def test_subset(self, response, body):
        """Test the response includes the body."""
        assert set(body).issubset(set(response.json))

    def test_user_in_permissions(self, response, db_user):
        """Test the user is in experiment permissions."""
        owner_permissions = {"group_id": db_user["id"], "role": "Manage"}
        assert owner_permissions in response.json["permissions"]

    def test_name(self, response, name):
        """Test the response item has correct name."""
        assert response.json["name"] == name


class Permissions:
    """Test the response items with extra permissions."""

    def test_extra_permissions(self, response, permissions):
        """Test the response items have extra permissions."""
        for permission in permissions:
            assert permission in response.json["permissions"]


@mark.parametrize("name", ["experiment_1"], indirect=True)
class TestSimpleExperiment(CommonBaseTests):
    """Test the /experiment endpoint with simple permissions."""


PERMISSIONS_1 = [{"group_id": "00000000-0000-0002-0001-000000000001", "role": "Read"}]


@mark.parametrize("permissions", [PERMISSIONS_1], indirect=True)
@mark.parametrize("name", ["experiment_1"], indirect=True)
class TestSharedExperiment(Permissions, CommonBaseTests):
    """Test the /experiment endpoint with shared permissions."""