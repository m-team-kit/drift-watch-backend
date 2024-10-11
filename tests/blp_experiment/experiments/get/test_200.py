"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from datetime import timezone as tz
from uuid import UUID

from pytest import mark


@mark.parametrize("auth", [None], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
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


class Permission:
    """Test the response items permissions field."""

    def test_group_level(self, response, permissions):
        """Test which experiments group 'x' has permissions level 'y'."""
        for item in response.json:
            assert set(permissions).issubset(set(item["permissions"]))


@mark.parametrize("name", ["experiment_1"], indirect=True)
class TestNameFilter(Name, CommonBaseTests):
    """Test the response items name field."""


@mark.parametrize("created_after", ["2021-01-02"], indirect=True)
@mark.parametrize("created_before", ["2021-01-03"], indirect=True)
class TestBetweenFilter(CreatedAfter, CreatedBefore, CommonBaseTests):
    """Test the response items created at."""


GROUP_1 = "urn:mace:egi.eu:group:vo_example1:role=group1#aai.egi.eu"
PERMISSIONS = {GROUP_1: "Manage"}


@mark.parametrize("permissions", [PERMISSIONS], indirect=True)
class TestPermissions(Permission, CommonBaseTests):
    """Test the response items permissions field."""
