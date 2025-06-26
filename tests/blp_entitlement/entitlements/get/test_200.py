"""Testing module for endpoint methods /entitlement."""

# pylint: disable=redefined-outer-name
from pytest import mark

from tests.constants import *


class CommonBaseTests:
    """Common tests for the /entitlement endpoint."""

    def test_status_code(self, response):
        """Test the 200 response."""
        assert response.status_code == 200

    def test_response_is_list(self, response):
        """Test response data is delivered as list."""
        assert isinstance(response.json, dict)
        assert len(response.json["items"]) != 0


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class ValidAuth(CommonBaseTests):
    """Base class for valid authenticated tests."""


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class Registered(CommonBaseTests):
    """Base class for registered user tests."""


@mark.parametrize("user_info", ["egi-read"], indirect=True)
@mark.parametrize("entitlements_field", ["eduperson_entitlement"], indirect=True)
@mark.usefixtures("entitlements_field")
class Entitlements(ValidAuth, Registered):
    """Test the response items are correct entitlements."""

    def test_correct_titles(self, response, user_info, entitlements_field):
        """Test the response has correct entitlements."""
        assert response.json["items"] == user_info[entitlements_field]


class TestEmptyRequest(Entitlements):
    """Test the correct exchanges of emails by ids."""
