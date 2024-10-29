"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from uuid import UUID

from pytest import mark


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


@mark.parametrize("subiss", [("user_4", "issuer.1")], indirect=True)
class Registered(ValidAuth, WithDatabase):
    """Tests for message response when user is  registered."""


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"
EXPERIMENT_2 = "00000000-0000-0001-0001-000000000002"


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
class IsPrivate(CommonBaseTests):
    """Base class for group with manage entitlement tests."""


@mark.parametrize("experiment_id", [EXPERIMENT_2], indirect=True)
class IsPublic(CommonBaseTests):
    """Base class for group with manage entitlement tests."""


ENT_MANAGE = "urn:mace:egi.eu:group:vo_example1:role=manage#x.0"
ENT_EDIT = "urn:mace:egi.eu:group:vo_example1:role=edit#x.0"
ENT_READ = "urn:mace:egi.eu:group:vo_example1:role=read#x.0"
READ_ENTITLEMENTS = [[ENT_MANAGE], [ENT_EDIT], [ENT_READ]]


@mark.parametrize("entitlements", READ_ENTITLEMENTS, indirect=True)
class ReadGroup(ValidAuth, IsPrivate):
    """Base class for group with manage entitlement tests."""


class TestWithAccess(ReadGroup, IsPrivate, WithDatabase):
    """Test the responses item when user has access."""


class TestPublicRegistered(Registered, IsPublic, WithDatabase):
    """Test the responses items when the experiment is public."""


class TestMissingToken(NoAuthHeader, IsPublic, WithDatabase):
    """Test the response when no token and is public."""
