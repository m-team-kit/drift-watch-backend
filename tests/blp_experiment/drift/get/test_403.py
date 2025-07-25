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


@mark.parametrize("auth", [None], indirect=True)
class NoAuthHeader:
    """Tests when missing authentication header."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Forbidden"
        assert response.json["message"] == "Resource is not public."


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class ValidAuth(CommonBaseTests):
    """Base class for valid authenticated tests."""


@mark.parametrize("user_info", ["ai4eosc-unregist"], indirect=True)
class NotRegistered(ValidAuth):
    """Tests for message response when user is not registered."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Forbidden"
        assert response.json["message"] == "User not registered."


@mark.parametrize("user_info", NO_READ, indirect=True)
class PermissionDenied(ValidAuth):
    """Tests for message response when user does not have permission."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Forbidden"
        assert response.json["message"] == "Insufficient permissions."


@mark.parametrize("experiment_id", PRIVATE_EXPS, indirect=True)
class IsPrivate(CommonBaseTests):
    """Base class for group with public as false."""


@mark.parametrize("experiment_id", PUBLIC_EXPS, indirect=True)
class IsPublic(CommonBaseTests):
    """Base class for group with public as true."""


@mark.parametrize("drift_id", DRIFTS, indirect=True)
class TestNotRegistered(NotRegistered, IsPublic, WithDatabase):
    """Test the authentication response when user not registered."""


@mark.parametrize("drift_id", DRIFTS, indirect=True)
class TestNoAccessPrivate(PermissionDenied, IsPrivate, WithDatabase):
    """Tests for message response for no permission."""


@mark.parametrize("drift_id", DRIFTS, indirect=True)
class TestMissingToken(NoAuthHeader, IsPrivate, WithDatabase):
    """Test the response when no token and is public."""
