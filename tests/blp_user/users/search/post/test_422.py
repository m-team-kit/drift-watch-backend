"""Testing module for endpoint methods /user."""

# pylint: disable=redefined-outer-name
from pytest import mark


class CommonBaseTests:
    """Common tests for the /user endpoint."""

    def test_status_code(self, response):
        """Test the 422 response."""
        assert response.status_code == 422
        assert response.json["code"] == 422


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class ValidAuth(CommonBaseTests):
    """Base class for valid authenticated tests."""


@mark.parametrize("user_info", ["egi-admin"], indirect=True)
class IsAdmin(ValidAuth):
    """Base class for group with admin entitlement tests."""


@mark.parametrize("body", ["str"], indirect=True)
class InvalidInput(WithDatabase):
    """Test the bad_key parameter."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "_schema" in response.json["errors"]["json"]
        error = response.json["errors"]["json"]["_schema"]
        assert error == ["Invalid input type."]


@mark.parametrize("query", [{"bad_arg": 0}], indirect=True)
class InvalidQuery(WithDatabase):
    """Test the bad_key parameter."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "bad_arg" in response.json["errors"]["query"]
        error = response.json["errors"]["query"]["bad_arg"]
        assert error == ["Unknown field."]


class TestStringBody(IsAdmin, InvalidInput):
    """Test the response when body is a string."""


# class TestUnknownQuery(IsAdmin, InvalidQuery):
#     """Test the response when query arg is unknown."""
