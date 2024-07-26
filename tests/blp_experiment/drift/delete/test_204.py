"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import mark

EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /drift/<drift_id> endpoint."""

    def test_status_code(self, response):
        """Test the 204 response."""
        assert response.status_code == 204

    def test_not_in_database(self, db_drift):
        """Test the response items are in the database."""
        assert db_drift is None


DRIFT_V100_1 = "00000000-0000-0004-0001-000000000001"


@mark.parametrize("drift_id", [DRIFT_V100_1], indirect=True)
class TestDelExperiment(CommonBaseTests):
    """Tests for deleting an experiment."""
