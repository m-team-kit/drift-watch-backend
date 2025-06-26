"""Testing module for endpoint methods /drifts."""

# pylint: disable=redefined-outer-name
from pytest import mark

from tests.constants import *


class CommonBaseTests:
    """Common tests for the /drifts endpoint."""

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


@mark.parametrize("experiment_id", PRIVATE_EXPS, indirect=True)
class IsPrivate(WithDatabase):
    """Base class for group with public as false."""


@mark.parametrize("user_info", CAN_EDIT, indirect=True)
class CanEdit(ValidAuth, WithDatabase):
    """Base class for group with manage entitlement tests."""


@mark.parametrize("body", [{"unknown": "val"}], indirect=True)
class UnknownField(CommonBaseTests):
    """Test the response message for unknown key in body."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"].values()
        assert ["Unknown field."] in errors


@mark.parametrize("job_status", [None], indirect=True)
class MissingJobStatus(CommonBaseTests):
    """Test the response message for missing drift boolean."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "job_status" in response.json["errors"]["json"]
        errors = response.json["errors"]["json"]["job_status"]
        assert "Missing data for required field." in errors


@mark.parametrize("job_status", ["text"], indirect=True)
class InvalidJobStatus(CommonBaseTests):
    """Test the response message for invalid drift boolean."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "job_status" in response.json["errors"]["json"]
        errors = response.json["errors"]["json"]["job_status"]
        assert "Must be one of: Running, Completed, Failed." in errors


@mark.parametrize("model", [None], indirect=True)
class MissingModel(CommonBaseTests):
    """Test the response message for missing drift parameter."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "model" in response.json["errors"]["json"]
        errors = response.json["errors"]["json"]["model"]
        assert "Missing data for required field." in errors


@mark.parametrize("detected", [None], indirect=True)
class MissingDetected(CommonBaseTests):
    """Test the response message for missing drift boolean."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "drift_detected" in response.json["errors"]["json"]
        errors = response.json["errors"]["json"]["drift_detected"]
        assert "Missing data for required field." in errors


@mark.parametrize("detected", ["text"], indirect=True)
class NoBoolDetected(CommonBaseTests):
    """Test the response message for missing drift boolean."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "drift_detected" in response.json["errors"]["json"]
        errors = response.json["errors"]["json"]["drift_detected"]
        assert "Not a valid boolean." in errors


class TestBadBodyKey(UnknownField, IsPrivate, CanEdit, WithDatabase):
    """Test the unknown key parameter in body."""


class TestMissingJobStatus(MissingJobStatus, IsPrivate, CanEdit):
    """Test the response when missing concept drift boolean."""


class TestInvalidJobStatus(InvalidJobStatus, IsPrivate, CanEdit):
    """Test the response when invalid concept drift boolean."""


class TestMissingModel(MissingModel, IsPrivate, CanEdit):
    """Test the response when missing drift parameter."""


class TestMissingDetected(MissingDetected, IsPrivate, CanEdit):
    """Test the response when missing drift boolean."""


class TestNoBoolDetected(NoBoolDetected, IsPrivate, CanEdit):
    """Test the response when missing drift boolean."""
