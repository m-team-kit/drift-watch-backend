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
        """Test the 404 response."""
        assert response.status_code == 404
        assert response.json["code"] == 404


class NotFound:
    """Test the when group Id is not in database."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Not Found"
        assert response.json["message"] == "Group not found."


GROUP_X = "00000000-0000-0002-0001-999999999999"


@mark.parametrize("group_id", [GROUP_X], indirect=True)
class TestNotInDatabase(NotFound, CommonBaseTests):
    """Test the when group Id is not in database."""
