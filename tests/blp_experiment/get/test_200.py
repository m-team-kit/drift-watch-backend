"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from datetime import timezone as tz

from pytest import mark


@mark.parametrize("auth", [None], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class TestCommon:
    """Common tests for the /experiment endpoint."""

    def test_status_code(self, response):
        """Test the 200 response."""
        assert response.status_code == 200

    def test_data_as_list(self, response):
        """Test response data is delivered as list."""
        assert isinstance(response.json, list)
        assert len(response.json) != 0


@mark.parametrize("created_after", ["2021-01-02"], indirect=True)
class TestCreatedAfterTests(TestCommon):
    """Test the response items created at."""

    def test_datetime(self, response):
        """Test the response items contain a correct date."""
        assert all(dt.fromisoformat(x["created_at"]) for x in response.json)

    def test_after_date(self, response, created_after):
        """Test the response items are after the indicated date."""
        req_date = dt.fromisoformat(created_after).replace(tzinfo=tz.utc)
        for item in response.json:
            assert dt.fromisoformat(item["created_at"]) >= req_date


@mark.parametrize("created_before", ["2021-01-03"], indirect=True)
class TestCreatedBeforeTests(TestCommon):
    """Test the response items created at."""

    def test_datetime(self, response):
        """Test the response items contain a correct date."""
        assert all(dt.fromisoformat(x["created_at"]) for x in response.json)

    def test_before_date(self, response, created_before):
        """Test the response items are before the indicated date."""
        req_date = dt.fromisoformat(created_before).replace(tzinfo=tz.utc)
        for item in response.json:
            assert dt.fromisoformat(item["created_at"]) <= req_date


@mark.parametrize("name", ["experiment_1"], indirect=True)
class TestName(TestCommon):
    """Test the response items name field."""

    def test_name(self, response, name):
        """Test the name field is correctly used for filtering."""
        assert all(x["name"] == name for x in response.json)


GROUP_1 = "00000000-0000-0001-0002-000000000001"


@mark.parametrize("permissions", [(GROUP_1, "Manage")], indirect=True)
class TestPermissions(TestCommon):
    """Test the response items permissions field."""

    def test_group_level(self, response, permissions):
        """Test which experiments group 'x' has permissions level 'y'."""
        group_id = permissions["permissions"]["$elemMatch"]["group_id"]
        role = permissions["permissions"]["$elemMatch"]["role"]
        for item in response.json:
            assert item["permissions"][group_id] == role
