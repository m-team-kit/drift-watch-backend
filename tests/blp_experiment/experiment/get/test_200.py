"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from uuid import UUID

from pytest import mark

from tests.constants import *


class CommonBaseTests:
    """Common tests for the experiment/<id> endpoint."""

    def test_status_code(self, response):
        """Test the 200 response."""
        assert response.status_code == 200

    def test_has_id(self, response):
        """Test the response items have an id."""
        assert "id" in response.json
        assert UUID(response.json["id"])

    def test_has_created_at(self, response):
        """Test the response items have a created_at."""
        assert "created_at" in response.json
        assert dt.fromisoformat(response.json["created_at"])

    def test_has_name(self, response):
        """Test the response items have a name."""
        assert response.json["name"] is not None

    def test_has_permissions(self, response):
        """Test the response items have permissions."""
        assert response.json["permissions"] is not None


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""

    def test_in_database(self, response, db_experiment):
        """Test the response items are in the database."""
        assert db_experiment is not None
        assert response.json == db_experiment


@mark.parametrize("auth", [None], indirect=True)
class NoAuthHeader:
    """Tests when missing authentication header."""


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class ValidAuth(CommonBaseTests):
    """Base class for valid authenticated tests."""


@mark.parametrize("user_info", CAN_READ + ["ai4eosc-unknown"], indirect=True)
class AnyUser(ValidAuth, WithDatabase):
    """Tests for message response when user is  registered."""


@mark.parametrize("experiment_id", PRIVATE_EXPS + PUBLIC_EXPS, indirect=True)
class AnyExperiment(WithDatabase):
    """Base class for group with manage entitlement tests."""


class TestMissingToken(NoAuthHeader, AnyExperiment):
    """Test the response when no token and is public."""


class TestAnyAccess(AnyUser, AnyExperiment):
    """Test the responses item when user has access."""
