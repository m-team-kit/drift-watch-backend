"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import mark


@mark.parametrize("name", ["experiment_a"], indirect=True)
@mark.parametrize("permissions", [[]], indirect=True)
class CommonBaseTests:
    """Common tests for the /experiment endpoint."""

    def test_status_code(self, response):
        """Test the 403 response."""
        assert response.status_code == 403


class NotRegistered:
    """Tests for message response when user is not registered."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["error"] == "Forbidden"
        assert response.json["description"] == "User not registered."


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class TestNotRegistered(NotRegistered, CommonBaseTests):
    """Test the authentication response when user not registered."""
