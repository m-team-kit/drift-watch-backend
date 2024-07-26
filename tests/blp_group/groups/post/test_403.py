"""Testing module for endpoint methods /group."""

# pylint: disable=redefined-outer-name
from pytest import mark


@mark.parametrize("name", ["group_a"], indirect=True)
class CommonBaseTests:
    """Common tests for the /group endpoint."""

    def test_status_code(self, response):
        """Test the 403 response."""
        assert response.status_code == 403
        assert response.json["code"] == 403


class NotRegistered:
    """Tests for message response when user is not registered."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Forbidden"
        assert response.json["message"] == "User not registered."


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class TestNotRegistered(NotRegistered, CommonBaseTests):
    """Test the authentication response when user not registered."""
