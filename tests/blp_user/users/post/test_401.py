"""Testing module for endpoint methods /user."""

# pylint: disable=redefined-outer-name
from pytest import mark

from tests.constants import *


class CommonBaseTests:
    """Common tests for the /user endpoint."""

    def test_status_code(self, response):
        """Test the 401 response."""
        assert response.status_code == 401
        assert response.json["code"] == 401


class NoAuthHeader:
    """Tests when missing authentication header."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Unauthorized"
        assert response.json["message"] == "No authorization header"


class UnknownIdentity:
    """Test when identity provided is unknown."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Unauthorized"
        assert response.json["message"] == "User identity could not be determined"


@mark.parametrize("auth", [None], indirect=True)
class TestMissingToken(NoAuthHeader, CommonBaseTests):
    """Test the /experiment endpoint with missing token."""


@mark.parametrize("auth", ["invalid_token"], indirect=True)
class TestInvalidToken(UnknownIdentity, CommonBaseTests):
    """Test the /experiment endpoint with invalid token."""
