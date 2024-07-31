"""Testing module for endpoint methods /user."""

# pylint: disable=redefined-outer-name
from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /user endpoint."""

    def test_status_code(self, response):
        """Test the 422 response."""
        assert response.status_code == 422
        assert response.json["code"] == 422


class UnknownField:
    """Test response message contains unknown field."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Unprocessable Entity"
        errors = response.json["errors"]["query"].values()
        assert ["Unknown field."] in errors


class MissingList:
    """Test response message contains invalid field."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["query"].values()
        assert ["Missing data for required field."] in errors


class InvalidEmail:
    """Test response message contains invalid email."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["query"]["emails"].values()
        assert ["Not a valid email address."] in errors


class InvalidLength:
    """Test response message contains invalid email."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["query"].values()
        assert ["Length must be between 1 and 10."] in errors


@mark.parametrize("query", [{"unknown": "val"}], indirect=True)
class TestBadQuery(UnknownField, CommonBaseTests):
    """Test the unknown parameter in the query."""


@mark.parametrize("query", ["non_list"], indirect=True)
class TestInvalidEmails(MissingList, CommonBaseTests):
    """Test query is a not valid list of emails."""


@mark.parametrize("emails", ["some_txt"], indirect=True)
class TestBadEmails(InvalidEmail, CommonBaseTests):
    """Test the response when emails is not a list."""


@mark.parametrize("emails", [[]], indirect=True)
class TestMinimum(MissingList, CommonBaseTests):
    """Test the response when emails is not a list."""


@mark.parametrize("emails", [["a@b.com"] * 11], indirect=True)
class TestMaximum(InvalidLength, CommonBaseTests):
    """Test the response when emails is not a list."""
