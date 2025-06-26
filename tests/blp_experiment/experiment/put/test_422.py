"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import mark

from tests.constants import *


class CommonBaseTests:
    """Common tests for the /experiment endpoint."""

    def test_status_code(self, response):
        """Test the 422 response."""
        assert response.status_code == 422
        assert response.json["code"] == 422


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""

    def test_not_saved(self, response, db_experiment):
        """Test the response items are in the database."""
        assert db_experiment is not None
        assert response.json != db_experiment


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class ValidAuth(CommonBaseTests):
    """Base class for valid authenticated tests."""


@mark.parametrize("experiment_id", PRIVATE_EXPS, indirect=True)
class IsPrivate(CommonBaseTests):
    """Base class for group with public as false."""


@mark.parametrize("user_info", CAN_MANAGE, indirect=True)
class CanManage(ValidAuth):
    """Base class for group with manage entitlement tests."""


@mark.parametrize("body", [{"unknown": "val"}], indirect=True)
class UnknownField(WithDatabase):
    """Test the response message for unknown key in body."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"].values()
        assert ["Unknown field."] in errors


@mark.parametrize("public", ["str"], indirect=True)
class NoBoolPublic(WithDatabase):
    """Test the response message for missing experiment boolean."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"]
        assert "Not a valid boolean." in errors["public"]


@mark.parametrize("permissions", ["str"], indirect=True)
class NoListPerm(WithDatabase):
    """Test the response message for missing experiment parameter."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"]
        assert "Not a valid list." in errors["permissions"]


@mark.parametrize("permissions", BAD_PERMISSIONS, indirect=True)
class BadLevel(WithDatabase):
    """Test the response message for bad permission level."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"]
        level_error = errors["permissions"]["0"]["level"]
        assert "Must be one of: Read, Edit, Manage." in level_error


class TestBadBodyKey(UnknownField, IsPrivate, CanManage):
    """Test the unknown key parameter in body."""


class TestNoBoolPublic(NoBoolPublic, IsPrivate, CanManage):
    """Test the response when missing concept experiment boolean."""


class TestNoListPerm(NoListPerm, IsPrivate, CanManage):
    """Test the response when missing concept experiment parameter."""


class TestUnknownLevel(BadLevel, CanManage, IsPrivate):
    """Test the response when unknown level in permissions."""
