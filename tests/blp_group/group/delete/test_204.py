"""Testing module for endpoint methods /group."""

# pylint: disable=redefined-outer-name
from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /group/<group_id> endpoint."""

    def test_status_code(self, response):
        """Test the 204 response."""
        assert response.status_code == 204

    def test_not_in_database(self, db_group):
        """Test the response items are in the database."""
        assert db_group is None


GROUP_1 = "00000000-0000-0002-0001-000000000001"


@mark.parametrize("group_id", [GROUP_1], indirect=True)
class TestDelGroup(CommonBaseTests):
    """Tests for deleting an group."""
