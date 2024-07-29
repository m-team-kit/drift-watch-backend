"""Testing module for endpoint methods /group."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt

from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /group/<group_id> endpoint."""

    def test_status_code(self, response):
        """Test the 200 response."""
        assert response.status_code == 200

    def test_in_database(self, response, db_group):
        """Test the response item is in the database."""
        assert db_group is not None
        assert response.json == db_group

    def test_has_id(self, response):
        """Test the response item has an id."""
        assert response.json["id"] is not None

    def test_has_created_at(self, response):
        """Test the response item has a created_at."""
        assert response.json["created_at"] is not None
        assert dt.fromisoformat(response.json["created_at"])

    def test_has_name(self, response):
        """Test the response item has a name."""
        assert response.json["name"] is not None

    def test_has_members(self, response):
        """Test the response item has members."""
        assert response.json["members"] is not None


GROUP_1 = "00000000-0000-0002-0001-000000000001"


@mark.parametrize("group_id", [GROUP_1], indirect=True)
class TestGetGroup(CommonBaseTests):
    """Test the /group/<group_id> endpoint."""
