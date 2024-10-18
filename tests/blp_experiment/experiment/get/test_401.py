"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import mark


class CommonBaseTests:
    """Common tests for the /experiment endpoint."""

    def test_status_code(self, response):
        """Test the 401 response."""
        assert response.status_code == 401
        assert response.json["code"] == 401


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for registered user tests."""

    def test_in_database(self, db_experiment):
        """Test the response items are in the database."""
        assert db_experiment is not None


@mark.parametrize("auth", [None], indirect=True)
class NoAuthHeader:
    """Tests when missing authentication header."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Unauthorized"
        assert response.json["message"] == "No authorization header"


@mark.parametrize("auth", ["invalid_token"], indirect=True)
class UnknownIdentity:
    """Test when identity provided is unknown."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Unauthorized"
        assert response.json["message"] == "User identity could not be determined"


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
class TestMissingToken(NoAuthHeader, CommonBaseTests):
    """Test the /experiment endpoint with missing token."""


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
class TestInvalidToken(UnknownIdentity, CommonBaseTests):
    """Test the /experiment endpoint with invalid token."""
