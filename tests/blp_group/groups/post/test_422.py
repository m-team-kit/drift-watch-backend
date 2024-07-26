"""Testing module for endpoint methods /group."""

# pylint: disable=redefined-outer-name
from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /group endpoint."""

    def test_status_code(self, response):
        """Test the 422 response."""
        assert response.status_code == 422
        assert response.json["code"] == 422


class UnknownField:
    """Test response message contains unknown field."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Unprocessable Entity"
        errors = response.json["errors"]["json"].values()
        assert ["Unknown field."] in errors


class InvalidString:
    """Test response message contains invalid field."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Unprocessable Entity"
        errors = response.json["errors"]["json"].values()
        assert ["Not a valid string."] in errors


class InvalidList:
    """Test response message contains invalid field."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"].values()
        assert ["Not a valid list."] in errors


@mark.parametrize("body", [{"unknown": "val"}], indirect=True)
class TestBadBodyKey(UnknownField, CommonBaseTests):
    """Test the bad_key parameter in the body."""


@mark.parametrize("name", [1000], indirect=True)
class TestBadGroup(InvalidString, CommonBaseTests):
    """Test group name is not a string."""


@mark.parametrize("members", ["non_list"], indirect=True)
class TestBadMembers(InvalidList, CommonBaseTests):
    """Test members is not a list."""
