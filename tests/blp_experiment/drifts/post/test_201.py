"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from uuid import UUID

from pytest import mark

from tests.constants import *


class CommonBaseTests:
    """Common tests for the /drift endpoint."""

    def test_status_code(self, response):
        """Test the 201 response."""
        assert response.status_code == 201

    def test_drift_id(self, response):
        """Test the response item have correct id."""
        assert UUID(response.json["id"]).version == 4

    def test_datetime(self, response):
        """Test the response item has a correct date."""
        assert dt.fromisoformat(response.json["created_at"])

    def test_subset(self, response, body):
        """Test the response includes the body."""
        assert set(body).issubset(set(response.json))


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""

    def test_in_database(self, response, db_drift):
        """Test the response items are in the database."""
        assert db_drift is not None
        assert response.json == db_drift


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


class V100Drift(CommonBaseTests):
    """Test the responses items."""

    def test_version(self, response):
        """Test the response item has the correct version."""
        assert response.json["schema_version"] == "1.0.0"

    def test_minimal_keys(self, response):
        """Test the response item contains the minimal keys."""
        assert "schema_version" in response.json
        assert "job_status" in response.json
        assert "tags" in response.json
        assert "model" in response.json
        assert "drift_detected" in response.json

    def test_values_types(self, response):
        """Test the response item correct types."""
        assert isinstance(response.json["schema_version"], str)
        assert isinstance(response.json["job_status"], str)
        assert isinstance(response.json["tags"], list)
        assert isinstance(response.json["model"], str)
        assert isinstance(response.json["drift_detected"], bool)

    def test_drift_values(self, response, detected, parameters):
        """Test the response item has the correct parameters."""
        assert response.json["drift_detected"] is detected
        if parameters is not None:
            assert response.json["parameters"] == parameters
        else:
            assert response.json["parameters"] == {}


@mark.parametrize("tags", [["concept_drift"]], indirect=True)
@mark.parametrize("parameters", [{"p_value": 0.1}], indirect=True)
@mark.parametrize("detected", [True], indirect=True)
class WithConceptDrift(V100Drift):
    """Test the concept drift responses."""

    def test_tags(self, response):
        """Test the response item has the correct tags."""
        assert "concept_drift" in response.json["tags"]


@mark.parametrize("tags", [["data_drift"]], indirect=True)
@mark.parametrize("parameters", [{"p_value": 0.1}], indirect=True)
@mark.parametrize("detected", [True], indirect=True)
class WithDataDrift(V100Drift):
    """Test the data drift responses."""

    def test_tags(self, response):
        """Test the response item has the correct tags."""
        assert "data_drift" in response.json["tags"]


@mark.parametrize("job_status", ALL_STATUS, indirect=True)
class TestV100Status(V100Drift, IsPrivate, CanEdit):
    """Test the responses items."""


class TestConcept(WithConceptDrift, IsPrivate, CanEdit):
    """Test the endpoint with concept drift."""


class TestData(WithDataDrift, IsPrivate, CanEdit):
    """Test the endpoint with data drift."""
