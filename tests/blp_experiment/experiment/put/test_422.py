"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
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


class InvalidMapping:
    """Test response message contains invalid list."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"].values()
        assert ["Not a valid mapping type."] in errors


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
@mark.parametrize("body", [{"bad_key": "val"}], indirect=True)
class TestBadBodyKey(UnknownField, CommonBaseTests):
    """Test the bad_key parameter in the body."""


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
@mark.parametrize("name", [1000], indirect=True)
class TestBadExperiment(InvalidString, CommonBaseTests):
    """Test experiment name is not a string."""


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
@mark.parametrize("permissions", ["non_map"], indirect=True)
class TestBadPermissions(InvalidMapping, CommonBaseTests):
    """Test permissions is not a list."""