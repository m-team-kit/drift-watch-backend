"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from uuid import UUID

from pytest import mark


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
ENT_LIST = [[ENT_MANAGE], [ENT_EDIT], [ENT_READ]]


@mark.parametrize("subiss", [("user_4", "issuer.1")], indirect=True)
@mark.parametrize("entitlements", ENT_LIST, indirect=True)
class ValidGroup(ValidAuth, IsPrivate):
    """Base class for group with manage entitlement tests."""


DRIFT_1 = "00000000-0000-0000-0000-000000000001"


@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
class TestWithAccess(ValidGroup, WithDatabase):
    """Test the responses item when user has access."""


@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
class TestPublic(IsPublic, ValidAuth, WithDatabase):
    """Test the responses items when the drift is public."""
