"""Testing module for endpoint methods /entitlement."""

# pylint: disable=redefined-outer-name
from pytest import mark

from tests.constants import *


class CommonBaseTests:
    """Common tests for the /entitlement endpoint."""

    def test_status_code(self, response):
        """Test the 401 response."""
        assert response.status_code == 401
        assert response.json["code"] == 401


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


class TestMissingToken(NoAuthHeader):
    """Test the /entitlement endpoint with missing token."""


class TestInvalidToken(UnknownIdentity):
    """Test the /entitlement endpoint with invalid token."""
