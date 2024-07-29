"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("name", ["new_name"], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /drift endpoint."""

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


class PermissionDenied:
    """Tests for message response when user does not have permission."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Forbidden"
        assert response.json["message"] == "Not a member of the group."


GROUP_1 = "00000000-0000-0002-0001-000000000001"
GROUP_3 = "00000000-0000-0002-0001-000000000003"


@mark.parametrize("group_id", [GROUP_1], indirect=True)
@mark.parametrize("subiss", [("unknown", "egi.com")], indirect=True)
class TestNotRegistered(NotRegistered, CommonBaseTests):
    """Test the authentication response when user not registered."""


@mark.parametrize("group_id", [GROUP_3], indirect=True)
class TestPermission(PermissionDenied, CommonBaseTests):
    """Tests for message response when user is not member."""
