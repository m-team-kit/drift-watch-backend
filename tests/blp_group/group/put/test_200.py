"""Testing module for endpoint methods /group."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt

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

    def test_in_database(self, response, db_group):
        """Test the response items are in the database."""
        assert db_group is not None
        assert response.json == db_group

    def test_created_at(self, response):
        """Test the response item has a correct date."""
        assert dt.fromisoformat(response.json["created_at"])

    def test_subset(self, response, body):
        """Test the response includes the body."""
        assert set(body).issubset(set(response.json))

    def test_user_member(self, response, db_user):
        """Test the response item the user as member."""
        assert db_user["id"] in response.json["members"]

    def test_no_repeated(self, response):
        """Test the response items have no repeated members."""
        members = response.json["members"]
        assert len(set(members)) == len(members)


USER_1 = "00000000-0000-0003-0001-000000000001"
USER_2 = "00000000-0000-0003-0001-000000000002"
MEMBERS_1 = [USER_1, USER_2, USER_2]


@mark.parametrize("name", ["new_name"], indirect=True)
@mark.parametrize("members", [MEMBERS_1], indirect=True)
class EditValues:
    """Test the item values match the request."""

    def test_name(self, response, name):
        """Test the response item has the correct name."""
        assert response.json["name"] == name

    def test_members(self, response, members, db_user):
        """Test the response item has the correct permissions."""
        members = members + [db_user["id"]]
        assert set(response.json["members"]) == set(members)


GROUP_1 = "00000000-0000-0002-0001-000000000001"


@mark.parametrize("group_id", [GROUP_1], indirect=True)
class TestEditGroup1(EditValues, CommonBaseTests):
    """Test the responses items."""
