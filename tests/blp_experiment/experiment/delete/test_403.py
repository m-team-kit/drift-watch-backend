"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import mark

from tests.constants import *


class CommonBaseTests:
    """Common tests for the /experiment endpoint."""

    def test_status_code(self, response):
        """Test the 403 response."""
        assert response.status_code == 403
        assert response.json["code"] == 403


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""

    def test_in_database(self, db_experiment):
        """Test the response items are in the database."""
        assert db_experiment is not None


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class ValidAuth(CommonBaseTests):
    """Base class for valid authenticated tests."""


@mark.parametrize("user_info", ["egi-unknown"], indirect=True)
class NotRegistered(ValidAuth):
    """Tests for message response when user is not registered."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Forbidden"
        assert response.json["message"] == "User not registered."


@mark.parametrize("user_info", NO_MANAGE, indirect=True)
class PermissionDenied(ValidAuth, WithDatabase):
    """Tests for message response when user does not have permission."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Forbidden"
        assert response.json["message"] == "Insufficient permissions."


@mark.parametrize("experiment_id", PUBLIC_EXPS + PRIVATE_EXPS, indirect=True)
class AnyExperiment(CommonBaseTests):
    """Base class for all experiments."""


class TestNotRegistered(NotRegistered, AnyExperiment, WithDatabase):
    """Test the authentication response when user not registered."""


class TestNoManageAccess(PermissionDenied, AnyExperiment, WithDatabase):
    """Tests for message response for read permissions."""
