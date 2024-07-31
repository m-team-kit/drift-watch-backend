"""Testing module for endpoint methods /user."""

# pylint: disable=redefined-outer-name
from uuid import UUID

from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /user endpoint."""

    def test_status_code(self, response):
        """Test the 200 response."""
        assert response.status_code == 200

    def test_ids_is_list(self, response):
        """Test response data is delivered as list."""
        assert isinstance(response.json["ids"], list)
        assert len(response.json["ids"]) != 0


class ItemsUUID:
    """Test the response items are UUID and correct order."""

    def test_ids_uuid(self, response):
        """Test the response items have correct id."""
        assert all(UUID(x) for x in response.json["ids"])


EMAILS_1 = ["user_1@issuer.1.com", "user_2@issuer.1.com", "user_1@issuer.2.com"]


@mark.parametrize("emails", [EMAILS_1], indirect=True)
class TestExchangeEmails(ItemsUUID, CommonBaseTests):
    """Test the correct exchanges of emails by ids."""
