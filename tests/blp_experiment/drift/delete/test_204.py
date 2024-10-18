"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import mark


class CommonBaseTests:
    """Common tests for the /drift/<drift_id> endpoint."""

    def test_status_code(self, response):
        """Test the 204 response."""
        assert response.status_code == 204


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""

    def test_not_in_database(self, db_drift):
        """Test the response items are in the database."""
        assert db_drift is None


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class ValidAuth(CommonBaseTests):
    """Base class for valid authenticated tests."""


@mark.parametrize("subiss", [("user_4", "issuer.1")], indirect=True)
class Registered(ValidAuth, WithDatabase):
    """Tests for message response when user is  registered."""


USER_1 = ("user_1", "issuer.1")
USER_2 = ("user_2", "issuer.1")


@mark.parametrize("subiss", [USER_1, USER_2], indirect=True)
class CanEdit(ValidAuth, WithDatabase):
    """Tests for message response when user is  registered."""


ENT_MANAGE = "urn:mace:egi.eu:group:vo_example1:role=manage#x.0"
ENT_EDIT = "urn:mace:egi.eu:group:vo_example1:role=edit#x.0"
ENT_READ = "urn:mace:egi.eu:group:vo_example1:role=read#x.0"


@mark.parametrize("entitlements", [[ENT_MANAGE], [ENT_EDIT]], indirect=True)
class EditGroup(CommonBaseTests):
    """Base class for group with manage entitlement tests."""


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"
EXPERIMENT_2 = "00000000-0000-0001-0001-000000000002"

DRIFT_1 = "00000000-0000-0000-0000-000000000001"


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
class TestUserWithEdit(CanEdit, WithDatabase):
    """Test when user has edit rights on the experiment."""


@mark.parametrize("experiment_id", [EXPERIMENT_2], indirect=True)
@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
class TestGroupWithEdit(EditGroup, Registered, WithDatabase):
    """Test when group has edit rights on the experiment."""
