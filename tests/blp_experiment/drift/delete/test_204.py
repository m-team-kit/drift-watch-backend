"""Testing module for endpoint methods /experiment."""

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


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"
EXPERIMENT_2 = "00000000-0000-0001-0001-000000000002"
EXPERIMENT_3 = "00000000-0000-0001-0001-000000000003"
EXPERIMENT_4 = "00000000-0000-0001-0001-000000000004"
ENT_MANAGE = "urn:mace:egi.eu:group:vo_example1:role=manage#x.0"
ENT_EDIT = "urn:mace:egi.eu:group:vo_example1:role=edit#x.0"


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
@mark.parametrize("subiss", [("user_4", "issuer.1")], indirect=True)
@mark.parametrize("entitlements", [[ENT_MANAGE]], indirect=True)
class ManageGroup(CommonBaseTests):
    """Base class for group with manage entitlement tests."""


@mark.parametrize("experiment_id", [EXPERIMENT_2], indirect=True)
@mark.parametrize("subiss", [("user_4", "issuer.1")], indirect=True)
@mark.parametrize("entitlements", [[ENT_EDIT]], indirect=True)
class EditGroup(CommonBaseTests):
    """Base class for group with edit entitlement tests."""


@mark.parametrize("experiment_id", [EXPERIMENT_3], indirect=True)
@mark.parametrize("subiss", [("user_1", "issuer.1")], indirect=True)
class ManageUser(CommonBaseTests):
    """Base class for user with manage entitlement tests."""


@mark.parametrize("experiment_id", [EXPERIMENT_4], indirect=True)
@mark.parametrize("subiss", [("user_2", "issuer.1")], indirect=True)
class EditUser(CommonBaseTests):
    """Base class for user with manage entitlement tests."""


DRIFT_1 = "00000000-0000-0000-0000-000000000001"
DRIFT_2 = "00000000-0000-0000-0000-000000000002"


@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
class TestUserWithManage(ValidAuth, WithDatabase, ManageUser):
    """Test when user has manage rights on the experiment."""


@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
class TestUserWithEdit(ValidAuth, WithDatabase, EditUser):
    """Test when user has edit rights on the experiment."""


@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
class TestGroupWithManage(ValidAuth, WithDatabase, ManageGroup):
    """Test when group has manage rights on the experiment."""


@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
class TestGroupWithEdit(ValidAuth, WithDatabase, EditGroup):
    """Test when group has edit rights on the experiment."""
