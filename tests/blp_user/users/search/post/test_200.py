"""Testing module for endpoint methods /user."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from datetime import timezone as tz
from uuid import UUID

from pytest import mark


class CommonBaseTests:
    """Common tests for the /user endpoint."""

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

    def test_created_at(self, response):
        """Test the response items contain a correct date."""
        assert all(dt.fromisoformat(x["created_at"]) for x in response.json)

    def test_subject(self, response):
        """Test the response items contain a correct subject."""
        assert all(isinstance(x["subject"], str) for x in response.json)

    def test_issuer(self, response):
        """Test the response items contain a correct issuer."""
        assert all(isinstance(x["issuer"], str) for x in response.json)

    def test_email(self, response):
        """Test the response items contain a correct email."""
        assert all(isinstance(x["email"], str) for x in response.json)

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


@mark.parametrize("subiss", [("user_4", "issuer.1")], indirect=True)
class Registered(ValidAuth):
    """Tests for message response when user is  registered."""


@mark.parametrize("subiss", [("unknown", "issuer.1")], indirect=True)
class NotRegistered(ValidAuth):
    """Tests for message response when user is not registered."""


@mark.parametrize("entitlements", [["iam:admin"]], indirect=True)
class IsAdmin(CommonBaseTests):
    """Base class for group with admin entitlement tests."""


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


@mark.parametrize("sort_by", ["created_at", "email", "subject", "issuer"], indirect=True)
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


class TestRegisteredAdmin(Registered, IsAdmin, WithDatabase):
    """Test the responses items for full query."""


class TestUnknownAdmin(NotRegistered, IsAdmin, WithDatabase):
    """Test the response items contain the correct users."""


class TestAfterFilter(Registered, IsAdmin, AfterFilter):
    """Test the response items contain the correct users."""


class TestBeforeFilter(Registered, IsAdmin, BeforeFilter):
    """Test the response items contain the correct users."""


class TestSorting(Registered, IsAdmin, SortBy):
    """Test the response items contain the correct order."""
