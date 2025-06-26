"""Testing module for endpoint methods /user."""

# pylint: disable=redefined-outer-name
from pytest import mark

from tests.constants import *


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /user endpoint."""

    def test_status_code(self, response):
        """Test the 409 response."""
        assert response.status_code == 409
        assert response.json["code"] == 409


class ConflictSubIss:
    """Test response message contains subject and issuer conflict."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Conflict"
        assert response.json["message"] == "User already exists."


@mark.parametrize("user_info", ["egi-null"], indirect=True)
class TestRegisterAgain(ConflictSubIss, CommonBaseTests):
    """Test the response if registering again parameter."""
