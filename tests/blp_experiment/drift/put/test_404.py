"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import mark

from tests.constants import *


class CommonBaseTests:
    """Common tests for the /drift/<id> endpoint."""

    def test_status_code(self, response):
        """Test the 404 response."""
        assert response.status_code == 404
        assert response.json["code"] == 404


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class ValidAuth(CommonBaseTests):
    """Base class for valid authenticated tests."""


@mark.parametrize("experiment_id", UNKNOWN_EXPS, indirect=True)
@mark.parametrize("drift_id", DRIFTS, indirect=True)
class ExperimentNotFound(WithDatabase):
    """Test the when experiment Id is not in database."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Not Found"
        assert response.json["message"] == "Experiment not found."


@mark.parametrize("user_info", CAN_EDIT, indirect=True)
class CanEdit(ValidAuth, WithDatabase):
    """Base class for tests with edit permissions."""


@mark.parametrize("experiment_id", PRIVATE_EXPS, indirect=True)
@mark.parametrize("drift_id", UNKNWON_DRIFTS, indirect=True)
class DriftNotFound(WithDatabase):
    """Test the when drift Id is not in database."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Not Found"
        assert response.json["message"] == "Drift not found."


class TestExperimentNotInDB(ValidAuth, ExperimentNotFound):
    """Test the when experiment Id is not in database."""


class TestDriftNotInDB(CanEdit, DriftNotFound):
    """Test the when drift Id is not in database."""
