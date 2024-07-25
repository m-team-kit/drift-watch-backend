"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from uuid import UUID

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
        """Test the 201 response."""
        assert response.status_code == 201

    def test_in_database(self, response, db_drift):
        """Test the response items are in the database."""
        assert db_drift is not None
        assert response.json == db_drift

    def test_drift_id(self, response):
        """Test the response item have correct id."""
        assert UUID(response.json["id"]).version == 4

    def test_datetime(self, response):
        """Test the response item has a correct date."""
        assert dt.fromisoformat(response.json["created_at"])

    def test_subset(self, response, body):
        """Test the response includes the body."""
        assert set(body).issubset(set(response.json))


@mark.parametrize("schema_version", ["1.0.0"], indirect=True)
class V100Drift(CommonBaseTests):
    """Test the responses items."""

    def test_version(self, response):
        """Test the response item has the correct version."""
        assert response.json["schema_version"] == "1.0.0"

    def test_minimal_keys(self, response):
        """Test the response item contains the minimal keys."""
        assert "schema_version" in response.json
        assert "job_status" in response.json
        assert "model" in response.json

    def test_values_types(self, response):
        """Test the response item correct types."""
        assert isinstance(response.json["schema_version"], str)
        assert isinstance(response.json["job_status"], str)
        assert isinstance(response.json["model"], str)


class ConceptDrift:
    """Test the concept drift responses."""

    def test_concept_drift(self, response, concept_drift):
        """Test the concept drift response."""
        assert response.json["concept_drift"] == concept_drift


class NoConcept:
    """Test the no concept drift responses."""

    def test_no_concept_drift(self, response):
        """Test the no concept drift response."""
        no_drift = {"drift": False, "parameters": {}}
        assert response.json["concept_drift"] == no_drift


class DataDrift:
    """Test the data drift responses."""

    def test_data_drift(self, response, data_drift):
        """Test the data drift response."""
        assert response.json["data_drift"] == data_drift


class NoData:
    """Test the no data drift responses."""

    def test_no_data_drift(self, response):
        """Test the no data drift response."""
        no_drift = {"drift": False, "parameters": {}}
        assert response.json["data_drift"] == no_drift


ALL_STATUS = ["Running", "Completed", "Failed"]
DRIFT_1 = {"drift": True, "parameters": {"p_value": 0.1}}
DRIFT_2 = {"drift": True, "parameters": {"p_value": 0.1}}


@mark.parametrize("job_status", ALL_STATUS, indirect=True)
class TestV100Status(V100Drift):
    """Test the responses items."""


@mark.parametrize("concept_drift", [DRIFT_1], indirect=True)
class TestConceptV100(V100Drift, ConceptDrift, NoData):
    """Test the endpoint with concept drift."""


@mark.parametrize("data_drift", [DRIFT_1], indirect=True)
class TestDataV100(V100Drift, DataDrift, NoConcept):
    """Test the endpoint with data drift."""


@mark.parametrize("concept_drift", [DRIFT_1], indirect=True)
@mark.parametrize("data_drift", [DRIFT_1], indirect=True)
class TestFullV100(V100Drift, ConceptDrift, DataDrift):
    """Test the endpoint with concept and data drift."""
