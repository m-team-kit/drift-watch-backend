"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import mark


class CommonBaseTests:
    """Common tests for the /drift endpoint."""

    def test_status_code(self, response):
        """Test the 403 response."""
        assert response.status_code == 403
        assert response.json["code"] == 403


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""


@mark.parametrize("auth", [None], indirect=True)
class NoAuthHeader:
    """Tests when missing authentication header."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Forbidden"
        assert response.json["message"] == "Resource is not public."


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class ValidAuth(CommonBaseTests):
    """Base class for valid authenticated tests."""


@mark.parametrize("subiss", [("unknown", "issuer.1")], indirect=True)
class NotRegistered(ValidAuth):
    """Tests for message response when user is not registered."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Forbidden"
        assert response.json["message"] == "User not registered."


@mark.parametrize("subiss", [("user_4", "issuer.1")], indirect=True)
class Registered(ValidAuth):
    """Tests for message response when user is  registered."""


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"
EXPERIMENT_2 = "00000000-0000-0001-0001-000000000002"
ENT_READ = "urn:mace:egi.eu:group:vo_example1:role=read#x.0"


class PermissionDenied(Registered):
    """Tests for message response when user does not have permission."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Forbidden"
        assert response.json["message"] == "Insufficient permissions."


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
class IsPrivate(CommonBaseTests):
    """Base class for group with public as false."""


@mark.parametrize("experiment_id", [EXPERIMENT_2], indirect=True)
class IsPublic(CommonBaseTests):
    """Base class for group with public as true."""


@mark.parametrize("entitlements", [[]], indirect=True)
class NoAccess(PermissionDenied):
    """Base class for group without entitlement tests."""


DRIFT_1 = "00000000-0000-0000-0000-000000000001"


@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
class TestNotRegistered(NotRegistered, IsPublic, WithDatabase):
    """Test the authentication response when user not registered."""


@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
class TestNoAccessPrivate(NoAccess, IsPrivate, WithDatabase):
    """Tests for message response for no permission."""


@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
class TestMissingToken(NoAuthHeader, IsPrivate, WithDatabase):
    """Test the response when no token and is public."""
