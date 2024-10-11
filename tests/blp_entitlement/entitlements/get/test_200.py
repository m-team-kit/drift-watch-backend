"""Testing module for endpoint methods /entitlement."""

# pylint: disable=redefined-outer-name
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

    def test_response_is_list(self, response):
        """Test response data is delivered as list."""
        assert isinstance(response.json, dict)
        assert len(response.json["items"]) != 0


class Entitlements:
    """Test the response items are correct entitlements."""

    def test_correct_titles(self, response, entitlements):
        """Test the response has correct entitlements."""
        assert response.json["items"] == entitlements


ENTITLEMENTS_1 = ["entitlements_1:vo#admin", "entitlements_1:vo:group1"]
ENTITLEMENTS = [ENTITLEMENTS_1]


@mark.parametrize("entitlements", ENTITLEMENTS, indirect=True)
class TestEmptyRequest(Entitlements, CommonBaseTests):
    """Test the correct exchanges of emails by ids."""
