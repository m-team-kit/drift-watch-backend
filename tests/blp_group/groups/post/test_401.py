"""Testing module for endpoint methods /group."""

# pylint: disable=redefined-outer-name
from pytest import mark


@mark.parametrize("name", ["group_a"], indirect=True)
class CommonBaseTests:
    """Common tests for the /group endpoint."""

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
    """Test the /group endpoint with missing token."""


@mark.parametrize("auth", ["invalid_token"], indirect=True)
class TestInvalidToken(UnknownIdentity, CommonBaseTests):
    """Test the /group endpoint with invalid token."""
