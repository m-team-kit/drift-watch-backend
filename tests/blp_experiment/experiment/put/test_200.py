"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from uuid import UUID

from pytest import mark

from tests.constants import *


class CommonBaseTests:
    """Common tests for the /experiment/<id> endpoint."""

    def test_status_code(self, response):
        """Test the 200 response."""
        assert response.status_code == 200

    def test_has_id(self, response):
        """Test the response items have an id."""
        assert "id" in response.json
        assert UUID(response.json["id"])

    def test_has_created_at(self, response):
        """Test the response items have a created_at."""
        assert "created_at" in response.json
        assert dt.fromisoformat(response.json["created_at"])

    def test_has_name(self, response):
        """Test the response items have a name."""
        assert response.json["name"] is not None

    def test_has_permissions(self, response, db_user):
        """Test the response items have permissions."""
        owner_permission = {"level": "Manage", "entity": db_user["id"]}
        assert owner_permission in response.json["permissions"]


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


# TODO: @mark.parametrize("user_info", CAN_MANAGE, indirect=True)
@mark.parametrize("user_info", ["ai4eosc-manage"], indirect=True)
class CanManage(ValidAuth):
    """Base class for group with manage entitlement tests."""


@mark.parametrize("name", ["new name 1"], indirect=True)
@mark.parametrize("experiment_id", [EDITABLE_EXPS[0]], indirect=True)
class TestChangeName(CanManage, WithDatabase):
    """Test changing the name of the experiment."""

    def test_new_name(self, response, name):
        """Test the response items have the new name."""
        assert response.json["name"] == name


@mark.parametrize("name", ["new name 2"], indirect=True)
@mark.parametrize("description", ["new description"], indirect=True)
@mark.parametrize("experiment_id", [EDITABLE_EXPS[1]], indirect=True)
class TestChangeDescription(CanManage, WithDatabase):
    """Test changing the description of the experiment."""

    def test_new_description(self, response, description):
        """Test the response items have the new description."""
        assert response.json["description"] == description


@mark.parametrize("name", ["new name 3"], indirect=True)
@mark.parametrize("public", [True], indirect=True)
@mark.parametrize("experiment_id", [EDITABLE_EXPS[2]], indirect=True)
class TestChangePublic(CanManage, WithDatabase):
    """Test changing the public status of the experiment."""

    def test_new_public(self, response):
        """Test the response items have the new public status."""
        assert response.json["public"] is True


@mark.parametrize("name", ["new name 4"], indirect=True)
@mark.parametrize("permissions", [[{"level": "Read", "entity": "a"}]], indirect=True)
@mark.parametrize("experiment_id", [EDITABLE_EXPS[3]], indirect=True)
class TestChangePerm(CanManage, WithDatabase):
    """Test changing the permissions of the experiment."""

    def test_new_permissions(self, response, permissions, db_user):
        """Test the response items have the new permissions."""
        expected_permissions = permissions.copy()
        owner_permission = {"level": "Manage", "entity": db_user["id"]}
        expected_permissions.append(owner_permission)
        assert response.json["permissions"] == expected_permissions
