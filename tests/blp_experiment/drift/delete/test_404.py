"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import mark


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


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"
EXPERIMENT_X = "00000000-0000-0001-0001-999999999999"
DRIFT_1 = "00000000-0000-0004-0001-000000000001"
DRIFT_X = "00000000-0000-0001-0001-999999999999"


@mark.parametrize("experiment_id", [EXPERIMENT_X], indirect=True)
@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
class ExperimentNotFound(WithDatabase):
    """Test the when experiment Id is not in database."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Not Found"
        assert response.json["message"] == "Experiment not found."


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
@mark.parametrize("drift_id", [DRIFT_X], indirect=True)
class DriftNotFound(WithDatabase):
    """Test the when drift Id is not in database."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Not Found"
        assert response.json["message"] == "Drift not found."


class TestExperimentNotInDB(ValidAuth, ExperimentNotFound):
    """Test the when experiment Id is not in database."""


class TestDriftNotInDB(ValidAuth, DriftNotFound):
    """Test the when drift Id is not in database."""
