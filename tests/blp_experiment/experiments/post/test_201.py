"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from uuid import UUID

from pytest import mark

from tests.constants import *


class CommonBaseTests:
    """Common tests for the /experiment endpoint."""

    def test_status_code(self, response):
        """Test the 201 response."""
        assert response.status_code == 201

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
        owner_permission = {"level": "Manage", "entity": db_user["id"]}
        assert owner_permission in response.json["permissions"]

    def test_name(self, response, name):
        """Test the response item has correct name."""
        assert response.json["name"] == name


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""

    def test_in_database(self, response, db_experiment):
        """Test the response items are in the database."""
        assert db_experiment is not None
        assert response.json == db_experiment


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class ValidAuth(CommonBaseTests):
    """Base class for valid authenticated tests."""


@mark.parametrize("user_info", ["ai4eosc-null"], indirect=True)
class Registered(ValidAuth):
    """Tests for message response when user is  registered."""


@mark.parametrize("description", ["Some description"], indirect=True)
class WithDescription(WithDatabase):
    """Test the response items with description."""

    def test_description(self, response, description):
        """Test the response items have a description."""
        assert response.json["description"] == description
        assert isinstance(response.json["description"], str)


@mark.parametrize("public", [True], indirect=True)
class WithPublic(WithDatabase):
    """Test the response items with public permissions."""

    def test_public_permissions(self, response):
        """Test the response items have public permissions."""
        assert "public" in response.json
        assert response.json["public"] is True


@mark.parametrize("permissions", NEW_PERMISSIONS, indirect=True)
class WithPermissions(WithDatabase):
    """Test the response items with extra permissions."""

    def test_extra_permissions(self, response, permissions, db_user):
        """Test the response items have extra permissions."""
        expected_permissions = permissions.copy()
        owner_permission = {"level": "Manage", "entity": db_user["id"]}
        expected_permissions.append(owner_permission)
        assert response.json["permissions"] == expected_permissions


@mark.parametrize("name", ["new_simple_exp"], indirect=True)
class TestSimpleExperiment(Registered, WithDatabase):
    """Test the /experiment endpoint with simple permissions."""


@mark.parametrize("name", ["new_descrip_exp"], indirect=True)
class TestDescriptionExperiment(Registered, WithDescription):
    """Test the /experiment endpoint with simple permissions."""


@mark.parametrize("name", ["new_shared_exp"], indirect=True)
class TestSharedExperiment(Registered, WithPermissions):
    """Test the /experiment endpoint with shared permissions."""


@mark.parametrize("name", ["new_public_exp"], indirect=True)
class TestPublicExperiment(Registered, WithPublic):
    """Test the /experiment endpoint with simple permissions."""
