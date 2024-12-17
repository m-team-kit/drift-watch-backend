"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from datetime import timezone as tz
from uuid import UUID

from pytest import mark


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

    def test_pagination_header(self, response):
        """Test the response contains the pagination header."""
        assert "X-Pagination" in response.headers


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class ValidAuth(CommonBaseTests):
    """Base class for valid authenticated tests."""


@mark.parametrize("auth", [None], indirect=True)
class NoAuthHeader(CommonBaseTests):
    """Tests when missing authentication header."""


@mark.parametrize("subiss", [("user_4", "issuer.1")], indirect=True)
class Registered(ValidAuth):
    """Tests for message response when user is  registered."""


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"
EXPERIMENT_2 = "00000000-0000-0001-0001-000000000002"


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
class IsPrivate(CommonBaseTests):
    """Base class for group with public as false."""


@mark.parametrize("experiment_id", [EXPERIMENT_2], indirect=True)
class IsPublic(CommonBaseTests):
    """Base class for group with public as true."""


ENT_MANAGE = "urn:mace:egi.eu:group:vo_example1:role=manage#x.0"
ENT_EDIT = "urn:mace:egi.eu:group:vo_example1:role=edit#x.0"
ENT_READ = "urn:mace:egi.eu:group:vo_example1:role=read#x.0"
GROUPS_WITH_READ_RIGHTS = [[ENT_READ], [ENT_EDIT], [ENT_MANAGE]]


@mark.parametrize("entitlements", GROUPS_WITH_READ_RIGHTS, indirect=True)
class ReadGroup(Registered):
    """Base class for group with manage entitlement tests."""


@mark.parametrize("entitlements", [[]], indirect=True)
class NoGroup(Registered):
    """Base class for group with manage entitlement tests."""


@mark.parametrize("created_after", ["2020-12-31"], indirect=True)
class AfterFilter(WithDatabase):
    """Test the response items created at."""

    def test_after_date(self, response, created_after):
        """Test the response items are after the indicated date."""
        req_date = dt.fromisoformat(created_after).replace(tzinfo=tz.utc)
        for item in response.json:
            assert dt.fromisoformat(item["created_at"]) >= req_date


@mark.parametrize("created_before", ["2021-12-31"], indirect=True)
class BeforeFilter(WithDatabase):
    """Test the response items created at."""

    def test_before_date(self, response, created_before):
        """Test the response items are before the indicated date."""
        req_date = dt.fromisoformat(created_before).replace(tzinfo=tz.utc)
        for item in response.json:
            assert dt.fromisoformat(item["created_at"]) <= req_date


ALL_STATUS = ["Running", "Completed", "Failed"]


@mark.parametrize("job_status", ALL_STATUS, indirect=True)
class StatusFilter(WithDatabase):
    """Test the response items job status."""

    def test_job_status(self, response, job_status):
        """Test the job status is correctly updated."""
        assert all(x["job_status"] == job_status for x in response.json)


class TestPublicAccess(NoAuthHeader, IsPublic, WithDatabase):
    """Test the responses items for public access."""


class TestReadAccess(ReadGroup, IsPrivate, WithDatabase):
    """Test the responses items for private access."""


class TestAfterFilter(NoAuthHeader, IsPublic, AfterFilter):
    """Test the response items contain the correct drifts."""


class TestBeforeFilter(NoAuthHeader, IsPublic, BeforeFilter):
    """Test the response items contain the correct drifts."""


class TestBetweenFilter(NoAuthHeader, BeforeFilter, IsPublic, AfterFilter):
    """Test the response items contain the correct drifts."""


class TestStatusFilter(NoAuthHeader, IsPublic, StatusFilter):
    """Test the response items contain the correct drifts."""


class V100Drift(WithDatabase):
    """Tests for using V100 drift schema."""

    def test_version(self, response):
        """Test the response item has the correct version."""
        assert all(x["schema_version"] == "1.0.0" for x in response.json)

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


@mark.parametrize("model", ["model_1"], indirect=True)
class ModelFilter(V100Drift):
    """Test the response items model."""

    def test_model(self, response, model):
        """Test the response items contain the correct model."""
        assert all(x["model"] == model for x in response.json)


@mark.parametrize("concept_drift", [{"$exists": True}], indirect=True)
class ConceptFilter(V100Drift):
    """Test the response items concept drift."""

    def test_concept_drift(self, response):
        """Test the response items concept drift."""
        assert all("concept_drift" in item for item in response.json)


@mark.parametrize("data_drift", [{"$exists": True}], indirect=True)
class DataFilter(V100Drift):
    """Test the response items data drift."""

    def test_data_drift(self, response):
        """Test the response items data drift."""
        assert all("data_drift" in item for item in response.json)


class TestV100ModelFilter(NoAuthHeader, IsPublic, StatusFilter):
    """Test the responses items."""


class TestV100ConceptFilter(NoAuthHeader, IsPublic, ConceptFilter):
    """Test the responses items."""


class TestV100DataFilter(NoAuthHeader, IsPublic, DataFilter):
    """Test the responses items."""
