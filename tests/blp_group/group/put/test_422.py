"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /drift endpoint."""

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
    """Test response message contains invalid list."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"].values()
        assert ["Not a valid list."] in errors


GROUP_1 = "00000000-0000-0002-0001-000000000001"


@mark.parametrize("group_id", [GROUP_1], indirect=True)
@mark.parametrize("body", [{"bad_key": "val"}], indirect=True)
class TestBadBodyKey(UnknownField, CommonBaseTests):
    """Test the bad_key parameter in the body."""


@mark.parametrize("group_id", [GROUP_1], indirect=True)
@mark.parametrize("name", [1000], indirect=True)
class TestBadGroup(InvalidString, CommonBaseTests):
    """Test group name is not a string."""


@mark.parametrize("group_id", [GROUP_1], indirect=True)
@mark.parametrize("members", ["non_list"], indirect=True)
class TestBadMembers(InvalidList, CommonBaseTests):
    """Test members is not a list."""
