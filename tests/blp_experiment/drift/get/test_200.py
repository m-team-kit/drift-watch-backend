"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from uuid import UUID

from pytest import mark

from tests.constants import *


class CommonBaseTests:
    """Common tests for the drift/<drift_id> endpoint."""

    def test_status_code(self, response):
        """Test the 200 response."""
        assert response.status_code == 200

    def test_id(self, response):
        """Test the response items have an id."""
        assert "id" in response.json
        assert UUID(response.json["id"])

    def test_version(self, response):
        """Test the response item contain a correct version."""
        assert "schema_version" in response.json

    def test_has_created_at(self, response):
        """Test the response items have a created_at."""
        assert "created_at" in response.json
        assert dt.fromisoformat(response.json["created_at"])


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""

    def test_in_database(self, response, db_drift):
        """Test the response items are in the database."""
        assert db_drift is not None
        assert response.json == db_drift


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class ValidAuth(CommonBaseTests):
    """Base class for valid authenticated tests."""


@mark.parametrize("auth", [None], indirect=True)
class NoAuthHeader:
    """Tests when missing authentication header."""


@mark.parametrize("experiment_id", PRIVATE_EXPS, indirect=True)
class IsPrivate(CommonBaseTests):
    """Base class for group with manage entitlement tests."""


@mark.parametrize("experiment_id", PUBLIC_EXPS, indirect=True)
class IsPublic(CommonBaseTests):
    """Base class for group with manage entitlement tests."""


@mark.parametrize("user_info", CAN_READ, indirect=True)
class CanRead(ValidAuth):
    """Base class for group with manage entitlement tests."""


@mark.parametrize("drift_id", DRIFTS, indirect=True)
class TestWithAccess(IsPrivate, CanRead, WithDatabase):
    """Test the responses item when user has access."""


@mark.parametrize("drift_id", DRIFTS, indirect=True)
class TestPublic(IsPublic, NoAuthHeader, WithDatabase):
    """Test the responses items when the drift is public."""
