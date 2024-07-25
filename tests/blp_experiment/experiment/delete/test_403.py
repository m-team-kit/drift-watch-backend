"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import mark


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class CommonBaseTests:
    """Common tests for the /experiment endpoint."""

    def test_status_code(self, response):
        """Test the 403 response."""
        assert response.status_code == 403
        assert response.json["code"] == 403

    def test_in_database(self, db_experiment):
        """Test the response items are in the database."""
        assert db_experiment is not None


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
        assert response.json["message"] == "Insufficient permissions."


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"
EXPERIMENT_2 = "00000000-0000-0001-0001-000000000002"


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
@mark.parametrize("subiss", [("unknown", "egi.com")], indirect=True)
@mark.usefixtures("accept_authorization")
class TestNotRegistered(NotRegistered, CommonBaseTests):
    """Test the authentication response when user not registered."""


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("experiment_id", [EXPERIMENT_2], indirect=True)
@mark.usefixtures("accept_authorization")
class TestPermission(PermissionDenied, CommonBaseTests):
    """Tests for message response when user does not have manage permission."""