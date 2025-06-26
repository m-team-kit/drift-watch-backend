"""Testing module for endpoint methods /drifts."""

# pylint: disable=redefined-outer-name
from pytest import mark

from tests.constants import *


class CommonBaseTests:
    """Common tests for the /drifts endpoint."""

    def test_status_code(self, response):
        """Test the 403 response."""
        assert response.status_code == 403
        assert response.json["code"] == 403


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class ValidAuth(CommonBaseTests):
    """Base class for valid authenticated tests."""


@mark.parametrize("user_info", ["ai4eosc-unknown"], indirect=True)
class NotRegistered(ValidAuth):
    """Tests for message response when user is not registered."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Forbidden"
        assert response.json["message"] == "User not registered."


@mark.parametrize("experiment_id", PRIVATE_EXPS, indirect=True)
class IsPrivate(WithDatabase):
    """Base class for group with public as false."""


@mark.parametrize("experiment_id", PUBLIC_EXPS, indirect=True)
class IsPublic(WithDatabase):
    """Base class for group with public as true."""


@mark.parametrize("user_info", NO_EDIT, indirect=True)
class PermissionDenied(ValidAuth):
    """Tests for message response when user does not have permission."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Forbidden"
        assert response.json["message"] == "Insufficient permissions."


@mark.parametrize("parameters", [{"p_value": 0.1}], indirect=True)
class TestNotRegistered(NotRegistered, IsPublic, WithDatabase):
    """Test the authentication response when user not registered."""


@mark.parametrize("parameters", [{"p_value": 0.1}], indirect=True)
class TestNoAccessPublic(PermissionDenied, IsPublic, WithDatabase):
    """Tests for message response for no permission."""


@mark.parametrize("parameters", [{"p_value": 0.1}], indirect=True)
class TestNoAccessPrivate(PermissionDenied, IsPrivate, WithDatabase):
    """Tests for message response for no permission."""
