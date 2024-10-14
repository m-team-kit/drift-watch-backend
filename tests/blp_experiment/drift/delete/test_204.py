"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import mark


class CommonBaseTests:
    """Common tests for the /drift/<drift_id> endpoint."""

    def test_status_code(self, response):
        """Test the 204 response."""
        assert response.status_code == 204

    def test_not_in_database(self, db_drift):
        """Test the response items are in the database."""
        assert db_drift is None


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class ValidAuth(CommonBaseTests):
    """Base class for valid authenticated tests."""


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class Registered(CommonBaseTests):
    """Base class for registered user tests."""


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"
EXPERIMENT_2 = "00000000-0000-0001-0001-000000000002"
ENT_MANAGE_EXP1 = "urn:mace:egi.eu:group:vo_example1:role=group1#aai.egi.eu"
ENT_EDIT_EXP1 = "urn:mace:egi.eu:group:vo_example1:role=group2#aai.egi.eu"


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
@mark.parametrize("subiss", [("user_2", "issuer.1")], indirect=True)
@mark.parametrize("entitlements", [[ENT_MANAGE_EXP1]], indirect=True)
class ManageGroup(CommonBaseTests):
    """Base class for group with manage entitlement tests."""


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
@mark.parametrize("subiss", [("user_2", "issuer.1")], indirect=True)
@mark.parametrize("entitlements", [[ENT_EDIT_EXP1]], indirect=True)
class EditGroup(CommonBaseTests):
    """Base class for group with edit entitlement tests."""


@mark.parametrize("experiment_id", [EXPERIMENT_2], indirect=True)
@mark.parametrize("subiss", [("user_2", "issuer.1")], indirect=True)
class ManageUser(CommonBaseTests):
    """Base class for user with manage entitlement tests."""


@mark.parametrize("experiment_id", [EXPERIMENT_2], indirect=True)
@mark.parametrize("subiss", [("user_1", "issuer.1")], indirect=True)
class EditUser(CommonBaseTests):
    """Base class for user with manage entitlement tests."""


DRIFT_V100_1 = "00000000-0000-0004-0001-000000000001"


@mark.parametrize("drift_id", [DRIFT_V100_1], indirect=True)
class V100Experiment(ValidAuth, Registered):
    """Tests for deleting an experiment."""


class TestUserWithManage(V100Experiment, ManageUser):
    """Test when user has manage rights on the experiment."""


class TestUserWithEdit(V100Experiment, EditUser):
    """Test when user has edit rights on the experiment."""


class TestGroupWithManage(V100Experiment, ManageGroup):
    """Test when group has manage rights on the experiment."""


class TestGroupWithEdit(V100Experiment, EditGroup):
    """Test when group has edit rights on the experiment."""
