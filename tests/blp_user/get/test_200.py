"""Testing module for endpoint methods /user."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from datetime import timezone as tz
from uuid import UUID

from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("entitlements", [["iam:admin"]], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
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


class TestNoFilter(CommonBaseTests):
    """Test the responses items for full query."""


@mark.parametrize("created_after", ["2021-01-02"], indirect=True)
@mark.parametrize("created_before", ["2021-01-03"], indirect=True)
class TestBetweenFilter(CreatedAfter, CreatedBefore, CommonBaseTests):
    """Test the response items created before a date."""


@mark.parametrize("issuer", ["issuer_1"], indirect=True)
class TestIssuerFilter(CommonBaseTests):
    """Test the response items filtered by issuer."""
