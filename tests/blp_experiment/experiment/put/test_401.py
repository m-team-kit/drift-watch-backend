"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import mark

from tests.constants import *


class CommonBaseTests:
    """Common tests for the /experiment endpoint."""

    def test_status_code(self, response):
        """Test the 401 response."""
        assert response.status_code == 401
        assert response.json["code"] == 401


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for registered user tests."""


@mark.parametrize("auth", [None], indirect=True)
class NoAuthHeader(CommonBaseTests):
    """Tests when missing authentication header."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Unauthorized"
        assert response.json["message"] == "No authorization header"


@mark.parametrize("auth", ["invalid_token"], indirect=True)
class UnknownIdentity(CommonBaseTests):
    """Test when identity provided is unknown."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Unauthorized"
        assert response.json["message"] == "User identity could not be determined"


@mark.parametrize("experiment_id", PRIVATE_EXPS, indirect=True)
class IsPrivate(CommonBaseTests):
    """Base class for group with public as false."""


class TestMissingToken(NoAuthHeader, IsPrivate):
    """Test the /experiment endpoint with missing token."""


class TestInvalidToken(UnknownIdentity, IsPrivate):
    """Test the /experiment endpoint with invalid token."""
