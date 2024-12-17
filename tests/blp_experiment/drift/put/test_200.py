"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt

from pytest import mark


class CommonBaseTests:
    """Common tests for the /drift endpoint."""

    def test_status_code(self, response):
        """Test the 200 response."""
        assert response.status_code == 200

    def test_versions(self, response):
        """Test the response items contain the correct version."""
        assert "schema_version" in response.json

    def test_subset(self, response, body):
        """Test the response includes the body."""
        assert set(body).issubset(set(response.json))

    def test_has_created_at(self, response):
        """Test the response items have a created_at."""
        assert "created_at" in response.json
        assert dt.fromisoformat(response.json["created_at"])


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


@mark.parametrize("subiss", [("user_4", "issuer.1")], indirect=True)
class Registered(ValidAuth, WithDatabase):
    """Tests for message response when user is  registered."""


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"
EXPERIMENT_2 = "00000000-0000-0001-0001-000000000002"


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
class IsPrivate(WithDatabase):
    """Base class for group with public as false."""


@mark.parametrize("experiment_id", [EXPERIMENT_2], indirect=True)
class IsPublic(WithDatabase):
    """Base class for group with public as true."""


ENT_MANAGE = "urn:mace:egi.eu:group:vo_example1:role=manage#x.0"
ENT_EDIT = "urn:mace:egi.eu:group:vo_example1:role=edit#x.0"
ENT_READ = "urn:mace:egi.eu:group:vo_example1:role=read#x.0"


@mark.parametrize("entitlements", [[ENT_MANAGE], [ENT_EDIT]], indirect=True)
class EditGroup(Registered):
    """Base class for group with manage entitlement tests."""


class V100Edit(CommonBaseTests):
    """Test the response items."""

    def test_version(self, response):
        """Test the response item has the correct version."""
        assert response.json["schema_version"] == "1.0.0"

    def test_minimal_keys(self, response):
        """Test the response items contain the minimal keys."""
        assert "job_status" in response.json
        assert "tags" in response.json
        assert "model" in response.json
        assert "drift_detected" in response.json
        assert "parameters" in response.json

    def test_values_types(self, response):
        """Test the response items contain the correct types."""
        assert isinstance(response.json["job_status"], str)
        assert isinstance(response.json["tags"], list)
        assert isinstance(response.json["model"], str)
        assert isinstance(response.json["drift_detected"], bool)
        assert isinstance(response.json["parameters"], dict)

    def test_job_status(self, response, job_status):
        """Test the response item has the correct job status."""
        assert response.json["job_status"] == job_status

    def test_tags(self, response, tags):
        """Test the response item has the correct tags."""
        assert response.json["tags"] == tags

    def test_model(self, response, model):
        """Test the response item has the correct model."""
        assert response.json["model"] == model

    def test_drift_detected(self, response, detected):
        """Test the response item has the correct drift detected."""
        assert response.json["drift_detected"] == detected

    def test_parameters(self, response, parameters):
        """Test the response item has the correct data drift."""
        assert response.json["parameters"] == parameters


DRIFT_1 = "00000000-0000-0000-0000-000000000001"


@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
class TestPublicV100Drift(V100Edit, IsPublic, EditGroup):
    """Test the responses items."""


@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
class TestPrivateV100Drift(V100Edit, IsPrivate, EditGroup):
    """Test the responses items."""
