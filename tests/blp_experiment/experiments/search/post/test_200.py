"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from datetime import timezone as tz
from uuid import UUID

from pytest import mark


class CommonBaseTests:
    """Common tests for the /experiment endpoint."""

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

    def test_datetime(self, response):
        """Test the response items contain a correct date."""
        assert all(dt.fromisoformat(x["created_at"]) for x in response.json)

    def test_has_name(self, response):
        """Test the response items have a name."""
        assert all(x["name"] is not None for x in response.json)

    def test_has_permissions(self, response):
        """Test the response items have permissions."""
        assert all(x["permissions"] is not None for x in response.json)

    def test_pagination_header(self, response):
        """Test the response contains the pagination header."""
        assert "X-Pagination" in response.headers


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""


@mark.parametrize("auth", [None], indirect=True)
class NoAuthHeader(CommonBaseTests):
    """Tests when missing authentication header."""


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


@mark.parametrize("name", ["experiment_1"], indirect=True)
class NameFilter(WithDatabase):
    """Test the response items name field."""

    def test_name(self, response, name):
        """Test the name field is correctly used for filtering."""
        assert all(x["name"] == name for x in response.json)


@mark.parametrize("sort_by", ["created_at", "name", "public"], indirect=True)
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


class TestPublicAccess(NoAuthHeader, WithDatabase):
    """Test the responses items for public access."""


class TestAfterFilter(NoAuthHeader, AfterFilter):
    """Test the response items contain the correct experiments."""


class TestBeforeFilter(NoAuthHeader, BeforeFilter):
    """Test the response items contain the correct experiments."""


class TestBetweenFilter(NoAuthHeader, BeforeFilter, AfterFilter):
    """Test the response items contain the correct experiments."""


class TestNameFilter(NoAuthHeader, NameFilter):
    """Test the response items contain the correct experiments."""


class TestSorting(NoAuthHeader, SortBy):
    """Test the response items contain the correct order."""
