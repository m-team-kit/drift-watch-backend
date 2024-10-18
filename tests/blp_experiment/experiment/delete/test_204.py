"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import mark


class CommonBaseTests:
    """Common tests for the /experiment/<id> endpoint."""

    def test_status_code(self, response):
        """Test the 204 response."""
        assert response.status_code == 204


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""

    def test_not_in_database(self, db_experiment):
        """Test the response items are in the database."""
        assert db_experiment is None


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class ValidAuth(CommonBaseTests):
    """Base class for valid authenticated tests."""


@mark.parametrize("subiss", [("user_4", "issuer.1")], indirect=True)
class Registered(ValidAuth, WithDatabase):
    """Tests for message response when user is  registered."""


@mark.parametrize("subiss", [("user_1", "issuer.1")], indirect=True)
class IsOwner(ValidAuth, WithDatabase):
    """Tests for message response when user is  registered."""


ENT_MANAGE = "urn:mace:egi.eu:group:vo_example1:role=manage#x.0"
ENT_EDIT = "urn:mace:egi.eu:group:vo_example1:role=edit#x.0"
ENT_READ = "urn:mace:egi.eu:group:vo_example1:role=read#x.0"


@mark.parametrize("entitlements", [[ENT_MANAGE]], indirect=True)
class ManageGroup(CommonBaseTests):
    """Base class for group with manage entitlement tests."""


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"
EXPERIMENT_2 = "00000000-0000-0001-0001-000000000002"
EXPERIMENT_3 = "00000000-0000-0001-0001-000000000003"
EXPERIMENT_4 = "00000000-0000-0001-0001-000000000004"


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
class TestGroupWithManage(ManageGroup, Registered):
    """Test when group has manage rights on the experiment."""


@mark.parametrize("experiment_id", [EXPERIMENT_2], indirect=True)
class TestUserWithManage(IsOwner):
    """Test when user has manage rights on the experiment."""
