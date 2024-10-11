"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("name", ["experiment_a"], indirect=True)
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /experiment endpoint."""

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


GROUP_1 = "urn:mace:egi.eu:group:vo_example1:role=group1#aai.egi.eu"
PERMISSIONS = {GROUP_1: "Read"}


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.parametrize("permissions", [PERMISSIONS], indirect=True)
class TestBadEntitlements(CommonBaseTests):
    """Tests for message response when mismatch user's with new entitlements."""


@mark.parametrize("permissions", [[]], indirect=True)
class TestNotRegistered(NotRegistered, CommonBaseTests):
    """Test the authentication response when user not registered."""
