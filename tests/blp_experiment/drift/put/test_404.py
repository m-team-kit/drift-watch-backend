"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /drift/<id> endpoint."""

    def test_status_code(self, response):
        """Test the 404 response."""
        assert response.status_code == 404
        assert response.json["code"] == 404


class ExperimentNotFound:
    """Test the when experiment Id is not in database."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Not Found"
        assert response.json["message"] == "Experiment not found."


class DriftNotFound:
    """Test the when drift Id is not in database."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Not Found"
        assert response.json["message"] == "Drift not found."


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"
EXPERIMENT_X = "00000000-0000-0001-0001-999999999999"

DRIFT_EXP1_X = "00000000-0000-0004-0001-999999999999"
DRIFT_EXPX_X = "00000000-0000-0004-9999-999999999999"


@mark.parametrize("experiment_id", [EXPERIMENT_X], indirect=True)
@mark.parametrize("drift_id", [DRIFT_EXPX_X], indirect=True)
class TestExperimentNotInDB(ExperimentNotFound, CommonBaseTests):
    """Test the when experiment Id is not in database."""


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
@mark.parametrize("drift_id", [DRIFT_EXP1_X], indirect=True)
class TestDriftNotInDB(DriftNotFound, CommonBaseTests):
    """Test the when drift Id is not in database."""
