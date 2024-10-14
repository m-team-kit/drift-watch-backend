"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import mark

EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class CommonBaseTests:
    """Common tests for the /drift endpoint."""

    def test_status_code(self, response):
        """Test the 401 response."""
        assert response.status_code == 401
        assert response.json["code"] == 401

    def test_in_database(self, db_drift):
        """Test the response items are in the database."""
        assert db_drift is not None


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


DRIFT_V100_1 = "00000000-0000-0000-0000-000000000001"


@mark.parametrize("drift_id", [DRIFT_V100_1], indirect=True)
@mark.parametrize("auth", [None], indirect=True)
class TestMissingToken(NoAuthHeader, CommonBaseTests):
    """Test the /experiment endpoint with missing token."""


@mark.parametrize("drift_id", [DRIFT_V100_1], indirect=True)
@mark.parametrize("auth", ["invalid_token"], indirect=True)
class TestInvalidToken(UnknownIdentity, CommonBaseTests):
    """Test the /experiment endpoint with invalid token."""
