"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import mark

from tests.constants import *


class CommonBaseTests:
    """Common tests for the /drift endpoint."""

    def test_status_code(self, response):
        """Test the 403 response."""
        assert response.status_code == 403
        assert response.json["code"] == 403


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""

    def test_in_database(self, db_drift):
        """Test the response items are in the database."""
        assert db_drift is not None


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


@mark.parametrize("user_info", NO_EDIT, indirect=True)
class PermissionDenied(ValidAuth, WithDatabase):
    """Tests for message response when user does not have permission."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Forbidden"
        assert response.json["message"] == "Insufficient permissions."


@mark.parametrize("experiment_id", PRIVATE_EXPS + PUBLIC_EXPS, indirect=True)
class AnyExperiment(CommonBaseTests):
    """Base class for tests with any experiment."""


@mark.parametrize("drift_id", DRIFTS, indirect=True)
class TestNoEditAccess(PermissionDenied, AnyExperiment, WithDatabase):
    """Tests for message response for read permissions."""
