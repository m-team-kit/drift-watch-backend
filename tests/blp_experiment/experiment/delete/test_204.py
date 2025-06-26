"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import mark

from tests.constants import *


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


@mark.parametrize("user_info", CAN_MANAGE, indirect=True)
class CanManage(ValidAuth, WithDatabase):
    """Base class for group with manage entitlement tests."""


@mark.parametrize("experiment_id", PRIVATE_EXPS, indirect=True)
class TestGroupWithManage(CanManage):
    """Test when group has manage rights on the experiment."""
