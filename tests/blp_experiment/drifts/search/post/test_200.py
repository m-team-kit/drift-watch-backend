"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from datetime import timezone as tz
from uuid import UUID

from pytest import mark

from tests.constants import *


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


@mark.parametrize("experiment_id", PRIVATE_EXPS, indirect=True)
class IsPrivate(CommonBaseTests):
    """Base class for group with public as false."""


@mark.parametrize("experiment_id", PUBLIC_EXPS, indirect=True)
class IsPublic(CommonBaseTests):
    """Base class for group with public as true."""


@mark.parametrize("user_info", CAN_READ, indirect=True)
class CanRead(ValidAuth):
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


@mark.parametrize("job_status", ALL_STATUS, indirect=True)
class StatusFilter(WithDatabase):
    """Test the response items job status."""

    def test_job_status(self, response, job_status):
        """Test the job status is correctly updated."""
        assert all(x["job_status"] == job_status for x in response.json)


@mark.parametrize(
    "sort_by",
    ["created_at", "job_status", "model", "drift_detected", "schema_version"],
    indirect=True,
)
class SortBy(WithDatabase):
    """Test the response items are sorted by the correct field."""

    @mark.parametrize("order_by", ["asc"], indirect=True)
    def test_sort_asc(self, response, sort_by):
        """Test the response items are sorted by the correct field."""
        assert all(
            x[sort_by] <= y[sort_by]
            for x, y in zip(response.json, response.json[1:])
        )  # fmt: skip

    @mark.parametrize("order_by", ["desc"], indirect=True)
    def test_sort_desc(self, response, sort_by):
        """Test the response items are sorted by the correct field."""
        assert all(
            x[sort_by] >= y[sort_by]
            for x, y in zip(response.json, response.json[1:])
        )  # fmt: skip


class TestPublicAccess(NoAuthHeader, IsPublic, WithDatabase):
    """Test the responses items for public access."""


class TestReadAccess(CanRead, IsPrivate, WithDatabase):
    """Test the responses items for private access."""


class TestAfterFilter(NoAuthHeader, IsPublic, AfterFilter):
    """Test the response items contain the correct drifts."""


class TestBeforeFilter(NoAuthHeader, IsPublic, BeforeFilter):
    """Test the response items contain the correct drifts."""


class TestBetweenFilter(NoAuthHeader, BeforeFilter, IsPublic, AfterFilter):
    """Test the response items contain the correct drifts."""


class TestStatusFilter(NoAuthHeader, IsPublic, StatusFilter):
    """Test the response items contain the correct drifts."""


class TestSorting(NoAuthHeader, IsPublic, SortBy):
    """Test the response items contain the correct order."""


class V100Drift(WithDatabase):
    """Tests for using V100 drift schema."""

    def test_version(self, response):
        """Test the response item has the correct version."""
        assert all(x["schema_version"] == "1.0.0" for x in response.json)

    def test_minimal_keys(self, response):
        """Test the response items contain the minimal keys."""
        assert all("tags" in x for x in response.json)
        assert all("model" in x for x in response.json)
        assert all("drift_detected" in x for x in response.json)
        assert all("parameters" in x for x in response.json)

    def test_values_types(self, response):
        """Test the response items contain the correct types."""
        assert all(isinstance(x["tags"], list) for x in response.json)
        assert all(isinstance(x["model"], str) for x in response.json)
        assert all(isinstance(x["drift_detected"], bool) for x in response.json)
        assert all(isinstance(x["parameters"], dict) for x in response.json)


@mark.parametrize("model", ["model_1"], indirect=True)
class ModelFilter(V100Drift):
    """Test the response items model."""

    def test_model(self, response, model):
        """Test the response items contain the correct model."""
        assert all(x["model"] == model for x in response.json)


@mark.parametrize("tags", [{"$in": ["concept_drift"]}], indirect=True)
class ConceptFilter(V100Drift):
    """Test the response items concept drift."""

    def test_concept_drift(self, response):
        """Test the response items concept drift."""
        assert all("concept_drift" in item["tags"] for item in response.json)


@mark.parametrize("tags", [{"$in": ["data_drift"]}], indirect=True)
class DataFilter(V100Drift):
    """Test the response items data drift."""

    def test_data_drift(self, response):
        """Test the response items data drift."""
        assert all("data_drift" in item["tags"] for item in response.json)


class TestV100ModelFilter(NoAuthHeader, IsPublic, StatusFilter):
    """Test the responses items."""


class TestV100ConceptFilter(NoAuthHeader, IsPublic, ConceptFilter):
    """Test the responses items."""


class TestV100DataFilter(NoAuthHeader, IsPublic, DataFilter):
    """Test the responses items."""
