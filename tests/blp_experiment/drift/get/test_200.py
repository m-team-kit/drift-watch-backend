"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from uuid import UUID

from pytest import mark

EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /drift/<drift_id> endpoint."""

    def test_status_code(self, response):
        """Test the 200 response."""
        assert response.status_code == 200

    def test_in_database(self, response, db_drift):
        """Test the response items are in the database."""
        assert db_drift is not None
        assert response.json == db_drift

    def test_id(self, response):
        """Test the response items have an id."""
        assert "id" in response.json
        assert UUID(response.json["id"])

    def test_version(self, response):
        """Test the response item contain a correct version."""
        assert "schema_version" in response.json

    def test_has_created_at(self, response):
        """Test the response items have a created_at."""
        assert "created_at" in response.json
        assert dt.fromisoformat(response.json["created_at"])


class V100Drift(CommonBaseTests):
    """Tests for using V100 drift schema."""

    def test_correct_version(self, response):
        """Test the response items contain the correct version."""
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


DRIFT_V100_1 = "00000000-0000-0000-0000-000000000001"


@mark.parametrize("drift_id", [DRIFT_V100_1], indirect=True)
class TestGetIdV100(V100Drift):
    """Test the responses items."""
