"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import mark


class CommonBaseTests:
    """Common tests for the /experiment endpoint."""

    def test_status_code(self, response):
        """Test the 403 response."""
        assert response.status_code == 403
        assert response.json["code"] == 403


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""

    def test_in_database(self, db_experiment):
        """Test the response items are in the database."""
        assert db_experiment is not None


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
class Registered(ValidAuth, WithDatabase):
    """Tests for message response when user is  registered."""


class PermissionDenied(Registered):
    """Tests for message response when user does not have permission."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Forbidden"
        assert response.json["message"] == "Insufficient permissions."


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"
EXPERIMENT_2 = "00000000-0000-0001-0001-000000000002"


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
class IsPrivate(CommonBaseTests):
    """Base class for group with public as false."""


@mark.parametrize("experiment_id", [EXPERIMENT_2], indirect=True)
class IsPublic(CommonBaseTests):
    """Base class for group with public as true."""


ENT_MANAGE = "urn:mace:egi.eu:group:vo_example1:role=manage#x.0"
ENT_EDIT = "urn:mace:egi.eu:group:vo_example1:role=edit#x.0"
ENT_READ = "urn:mace:egi.eu:group:vo_example1:role=read#x.0"
NO_MANAGE_ENTITLEMENTS = [[ENT_READ], [ENT_EDIT], []]


@mark.parametrize("entitlements", NO_MANAGE_ENTITLEMENTS, indirect=True)
class NoManageGroup(IsPrivate):
    """Base class for group with read entitlement tests."""


class TestNotRegistered(NotRegistered, IsPublic, WithDatabase):
    """Test the authentication response when user not registered."""


class TestIsPublic(PermissionDenied, IsPublic, WithDatabase):
    """Tests for message response for no permission."""


class TestNoManageAccess(PermissionDenied, NoManageGroup, WithDatabase):
    """Tests for message response for read permissions."""
