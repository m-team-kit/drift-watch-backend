"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt

from pytest import mark

EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /drift endpoint."""

    def test_status_code(self, response):
        """Test the 200 response."""
        assert response.status_code == 200

    def test_in_database(self, response, db_drift):
        """Test the response items are in the database."""
        assert db_drift is not None
        assert response.json == db_drift

    def test_created_at(self, response):
        """Test the response item has a correct date."""
        assert dt.fromisoformat(response.json["created_at"])

    def test_versions(self, response):
        """Test the response items contain the correct version."""
        assert "schema_version" in response.json

    def test_subset(self, response, body):
        """Test the response includes the body."""
        assert set(body).issubset(set(response.json))


@mark.parametrize("schema_version", ["1.0.0"], indirect=True)
class V100Edit:
    """Test the response items."""

    def test_version(self, response):
        """Test the response item has the correct version."""
        assert response.json["schema_version"] == "1.0.0"

    def test_minimal_keys(self, response):
        """Test the response items contain the minimal keys."""
        assert "model" in response.json
        assert "concept_drift" in response.json
        assert "data_drift" in response.json

    def test_values_types(self, response):
        """Test the response items contain the correct types."""
        assert isinstance(response.json["model"], str)
        assert isinstance(response.json["concept_drift"], dict)
        assert isinstance(response.json["data_drift"], dict)

    def test_model(self, response, model):
        """Test the response item has the correct model."""
        assert response.json["model"] == model

    def test_job_status(self, response, job_status):
        """Test the response item has the correct job status."""
        assert response.json["job_status"] == job_status

    def test_concept_drift(self, response, concept_drift):
        """Test the response item has the correct concept drift."""
        assert response.json["concept_drift"] == concept_drift

    def test_data_drift(self, response, data_drift):
        """Test the response item has the correct data drift."""
        assert response.json["data_drift"] == data_drift


DRIFT_1 = "00000000-0000-0000-0000-000000000001"


@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
class TestEditV100Drift(V100Edit, CommonBaseTests):
    """Test the responses items."""


@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
@mark.parametrize("concept_drift", [None], indirect=True)
class TestRMConceptDrift(V100Edit, CommonBaseTests):
    """Test concept drift removal."""

    def test_concept_drift(self, response, concept_drift):
        """Test the response item has the correct concept drift."""
        no_drift = {"drift": False, "parameters": {}}
        assert response.json["concept_drift"] == no_drift


@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
@mark.parametrize("data_drift", [None], indirect=True)
class TestRMDataDrift(V100Edit, CommonBaseTests):
    """Test concept drift removal."""

    def test_data_drift(self, response, data_drift):
        """Test the response item has the correct concept drift."""
        no_drift = {"drift": False, "parameters": {}}
        assert response.json["data_drift"] == no_drift
