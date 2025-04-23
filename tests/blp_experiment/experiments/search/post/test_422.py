"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import mark


class CommonBaseTests:
    """Common tests for the /experiment endpoint."""

    def test_status_code(self, response):
        """Test the 422 response."""
        assert response.status_code == 422
        assert response.json["code"] == 422


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""


@mark.parametrize("auth", [None], indirect=True)
class NoAuthHeader(CommonBaseTests):
    """Tests when missing authentication header."""


@mark.parametrize("body", ["string_body"], indirect=True)
class InvalidInput(CommonBaseTests):
    """Test the bad_key parameter."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "_schema" in response.json["errors"]["json"]
        error = response.json["errors"]["json"]["_schema"]
        assert error == ["Invalid input type."]


@mark.parametrize("query", [{"bad_arg": 0}], indirect=True)
class InvalidQuery(CommonBaseTests):
    """Test the bad_key parameter."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "bad_arg" in response.json["errors"]["query"]
        error = response.json["errors"]["query"]["bad_arg"]
        assert error == ["Unknown field."]


class TestStringBody(NoAuthHeader, InvalidInput):
    """Test the response when body is a string."""


class TestUnknownQuery(NoAuthHeader, InvalidQuery):
    """Test the response when query arg is unknown."""
