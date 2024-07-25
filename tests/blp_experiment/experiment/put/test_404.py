"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("name", ["experiment_a"], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /experiment endpoint."""

    def test_status_code(self, response):
        """Test the 404 response."""
        assert response.status_code == 404
        assert response.json["code"] == 404


class NotFound:
    """Test the when experiment Id is not in database."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Not Found"
        assert response.json["message"] == "Experiment not found."


EXPERIMENT_X = "00000000-0000-0001-0001-999999999999"


@mark.parametrize("experiment_id", [EXPERIMENT_X], indirect=True)
class TestNotInDatabase(NotFound, CommonBaseTests):
    """Test the when experiment Id is not in database."""
