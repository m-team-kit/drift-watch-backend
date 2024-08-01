"""Testing module for endpoint methods /group."""

# pylint: disable=redefined-outer-name
from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /group endpoint."""

    def test_status_code(self, response):
        """Test the 409 response."""
        assert response.status_code == 409
        assert response.json["code"] == 409


class ConflictName:
    """Test response message contains name conflict."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Conflict"
        assert response.json["message"] == "Name conflict."


@mark.parametrize("name", ["experiment_1"], indirect=True)
class TestRepeatedName(ConflictName, CommonBaseTests):
    """Test the response when name exists in database."""
