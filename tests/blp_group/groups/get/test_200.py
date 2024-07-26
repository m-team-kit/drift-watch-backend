"""Testing module for endpoint methods /group."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from datetime import timezone as tz
from uuid import UUID

from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /group endpoint."""

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


class Name:
    """Test the response items name field."""

    def test_name(self, response, name):
        """Test the name field is correctly used for filtering."""
        assert all(x["name"] == name for x in response.json)


class Members:
    """Test the response items members field."""

    def test_members(self, response, members):
        """Test group members."""
        assert all(x["members"] == members for x in response.json)


@mark.parametrize("name", ["group_1"], indirect=True)
class TestNameFilter(Name, CommonBaseTests):
    """Test the response items name field."""


@mark.parametrize("created_after", ["2021-01-02"], indirect=True)
@mark.parametrize("created_before", ["2021-01-03"], indirect=True)
class TestBetweenFilter(CreatedAfter, CreatedBefore, CommonBaseTests):
    """Test the response items created at."""


GROUP_1 = "00000000-0000-0002-0001-000000000001"
MEMBERS = [
    "00000000-0000-0003-0001-000000000001",
    "00000000-0000-0003-0001-000000000002",
]


@mark.parametrize("members", [MEMBERS], indirect=True)
class TestMembers(Members, CommonBaseTests):
    """Test the response items members field."""
