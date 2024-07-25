"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import mark


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /drift endpoint."""

    def test_status_code(self, response):
        """Test the 422 response."""
        assert response.status_code == 422
        assert response.json["code"] == 422


class ErrorMessage:
    """Test the bad_key parameter."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "_schema" in response.json["errors"]["json"]
        error = response.json["errors"]["json"]["_schema"]
        assert error == ["Invalid input type."]


@mark.parametrize("body", ["string_body"], indirect=True)
class TestStringBody(ErrorMessage, CommonBaseTests):
    """Test the response when body is a string."""
