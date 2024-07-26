"""Testing module for endpoint methods /group."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from uuid import UUID

from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /group endpoint."""

    def test_status_code(self, response):
        """Test the 201 response."""
        assert response.status_code == 201

    def test_in_database(self, response, db_group):
        """Test the response items are in the database."""
        assert db_group is not None
        assert response.json == db_group

    def test_group_id(self, response):
        """Test the response item have correct id."""
        assert UUID(response.json["id"]).version == 4

    def test_created_at(self, response):
        """Test the response item has a correct date."""
        assert dt.fromisoformat(response.json["created_at"])

    def test_subset(self, response, body):
        """Test the response includes the body."""
        assert set(body).issubset(set(response.json))

    def test_user_member(self, response, db_user):
        """Test the response item the user as member."""
        assert db_user["id"] in response.json["members"]

    def test_name(self, response, name):
        """Test the response item has correct name."""
        assert response.json["name"] == name


class Members:
    """Test the response items with extra members."""

    def test_extra_members(self, response, members):
        """Test the response items have extra permissions."""
        for member in members:
            assert member in response.json["members"]

    def test_unique_members(self, response):
        """Test the response items have unique members."""
        members = response.json["members"]
        assert len(set(members)) == len(members)


@mark.parametrize("name", ["group_a"], indirect=True)
class TestSimpleGroup(CommonBaseTests):
    """Test the /group endpoint with simple permissions."""


GROUP_1 = "00000000-0000-0002-0001-000000000001"
MEMBERS_1 = ["00000000-0000-0003-0001-000000000002"]


@mark.parametrize("name", ["group_a"], indirect=True)
@mark.parametrize("members", [MEMBERS_1], indirect=True)
class TestSharedGroup(Members, CommonBaseTests):
    """Test the /group endpoint with shared permissions."""


@mark.parametrize("name", ["group_a"], indirect=True)
@mark.parametrize("members", [MEMBERS_1 * 2], indirect=True)
class TestRepeatedMembers(Members, CommonBaseTests):
    """Test the /group endpoint with repeated members."""
