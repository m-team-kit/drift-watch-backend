"""Testing module for endpoint methods /user."""

# pylint: disable=redefined-outer-name
from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /drift endpoint."""

    def test_status_code(self, response):
        """Test the 403 response."""
        assert response.status_code == 403
        assert response.json["code"] == 403


class NotAdmin:
    """Tests for message response when user is not admin."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Forbidden"
        assert (
            response.json["message"]
            == "User user_1@issuer_1 does not meet requirements"
        )


class TestPermission(NotAdmin, CommonBaseTests):
    """Tests for message response when user has not the entitlements."""
