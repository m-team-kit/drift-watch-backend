"""Testing module for endpoint methods /user."""

# pylint: disable=redefined-outer-name
from pytest import mark


class CommonBaseTests:
    """Common tests for the /users endpoint."""

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


@mark.parametrize("subiss", [("user_4", "issuer.1")], indirect=True)
class Registered(ValidAuth):
    """Tests for message response when user is  registered."""


@mark.parametrize("subiss", [("unknown", "issuer.1")], indirect=True)
class NotRegistered(ValidAuth):
    """Tests for message response when user is not registered."""


@mark.parametrize("entitlements", [None], indirect=True)
class NotAdmin:
    """Tests for message response when user is not admin."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Forbidden"
        assert "does not meet requirements" in response.json["message"]


class TestRegisteredUser(Registered, NotAdmin, CommonBaseTests):
    """Tests for message response when user has not the entitlements."""


class TestUnknownUser(NotRegistered, NotAdmin, CommonBaseTests):
    """Tests for message response when user has not the entitlements."""
