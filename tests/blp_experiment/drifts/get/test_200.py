"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from datetime import timezone as tz
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
        """Test the 200 response."""
        assert response.status_code == 200

    def test_data_as_list(self, response):
        """Test response data is delivered as list."""
        assert isinstance(response.json, list)
        assert len(response.json) != 0

    def test_id_uuid(self, response):
        """Test the response items have correct id."""
        assert all(UUID(x["id"]) for x in response.json)

    def test_versions(self, response, schema_version):
        """Test the response items contain the correct version."""
        sv = schema_version
        assert all(x["schema_version"] == sv for x in response.json)

    def test_datetime(self, response):
        """Test the response items contain a correct date."""
        assert all(dt.fromisoformat(x["created_at"]) for x in response.json)


class CreatedAfter:
    """Test the response items created at."""

    def test_after_date(self, response, created_after):
        """Test the response items are after the indicated date."""
        req_date = dt.fromisoformat(created_after).replace(tzinfo=tz.utc)
        for item in response.json:
            assert dt.fromisoformat(item["created_at"]) >= req_date


class CreatedBefore:
    """Test the response items created at."""

    def test_before_date(self, response, created_before):
        """Test the response items are before the indicated date."""
        req_date = dt.fromisoformat(created_before).replace(tzinfo=tz.utc)
        for item in response.json:
            assert dt.fromisoformat(item["created_at"]) <= req_date


class ValidStatus:
    """Test the response items job status."""

    def test_job_status(self, response, job_status):
        """Test the job status is correctly updated."""
        assert all(x["job_status"] == job_status for x in response.json)


@mark.parametrize("schema_version", ["1.0.0"], indirect=True)
@mark.parametrize("model", ["model_1"], indirect=True)
class V100Drift(CommonBaseTests):
    """Tests for using V100 drift schema."""

    def test_minimal_keys(self, response):
        """Test the response items contain the minimal keys."""
        assert all("model" in x for x in response.json)
        assert all("concept_drift" in x for x in response.json)
        assert all("data_drift" in x for x in response.json)

    def test_values_types(self, response):
        """Test the response items contain the correct types."""
        assert all(isinstance(x["model"], str) for x in response.json)
        assert all(isinstance(x["concept_drift"], dict) for x in response.json)
        assert all(isinstance(x["data_drift"], dict) for x in response.json)

    def test_model(self, response, model):
        """Test the response items contain the correct model."""
        assert all(x["model"] == model for x in response.json)


class ConceptDrift:
    """Test the response items concept drift."""

    def test_concept_drift(self, response):
        """Test the response items concept drift."""
        assert all("concept_drift" in item for item in response.json)


class DataDrift:
    """Test the response items data drift."""

    def test_data_drift(self, response):
        """Test the response items data drift."""
        assert all("data_drift" in item for item in response.json)


ALL_STATUS = ["Running", "Completed", "Failed"]


@mark.parametrize("job_status", ALL_STATUS, indirect=True)
class TestV100StatusFilter(ValidStatus, V100Drift):
    """Test the responses items."""


@mark.parametrize("concept_drift", [{"$exists": True}], indirect=True)
class TestV100ConceptFilter(ConceptDrift, V100Drift):
    """Test the responses items."""


@mark.parametrize("data_drift", [{"$exists": True}], indirect=True)
class TestV100DataFilter(DataDrift, V100Drift):
    """Test the responses items."""


@mark.parametrize("created_after", ["2021-01-02"], indirect=True)
@mark.parametrize("created_before", ["2021-01-03"], indirect=True)
class TestBetweenFilter(CreatedAfter, CreatedBefore, V100Drift):
    """Test the response items contain the correct drifts."""
