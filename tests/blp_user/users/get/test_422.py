"""Testing module for endpoint methods /user."""

# pylint: disable=redefined-outer-name
from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("entitlements", [["iam:admin"]], indirect=True)
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /user endpoint."""

    def test_status_code(self, response):
        """Test the 422 response."""
        assert response.status_code == 422
        assert response.json["code"] == 422


class InvalidInput:
    """Test the bad_key parameter."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "_schema" in response.json["errors"]["json"]
        error = response.json["errors"]["json"]["_schema"]
        assert error == ["Invalid input type."]


@mark.parametrize("body", ["string_body"], indirect=True)
class TestStringBody(InvalidInput, CommonBaseTests):
    """Test the response when body is a string."""
