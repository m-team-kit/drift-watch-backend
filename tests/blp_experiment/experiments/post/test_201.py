"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from uuid import UUID

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

    def test_in_database(self, response, db_experiment):
        """Test the response items are in the database."""
        assert db_experiment is not None
        assert response.json == db_experiment

    def test_experiment_id(self, response):
        """Test the response item have correct id."""
        assert UUID(response.json["id"]).version == 4

    def test_created_at(self, response):
        """Test the response item has a correct date."""
        assert dt.fromisoformat(response.json["created_at"])

    def test_subset(self, response, body):
        """Test the response includes the body."""
        assert set(body).issubset(set(response.json))

    def test_user_role(self, response, db_user):
        """Test the response item has the correct user role."""
        assert response.json["permissions"][db_user["id"]] == "Manage"

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


GROUP_1 = "00000000-0000-0002-0001-000000000001"
PERMISSIONS_1 = {GROUP_1: "Read"}


@mark.parametrize("permissions", [PERMISSIONS_1], indirect=True)
@mark.parametrize("name", ["experiment_1"], indirect=True)
class TestSharedExperiment(Permissions, CommonBaseTests):
    """Test the /experiment endpoint with shared permissions."""
