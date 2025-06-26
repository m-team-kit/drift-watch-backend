"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import mark

from tests.constants import *


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


@mark.parametrize("user_info", CAN_EDIT, indirect=True)
class CanEdit(ValidAuth, WithDatabase):
    """Tests for message response when user is  registered."""


@mark.parametrize("experiment_id", PRIVATE_EXPS, indirect=True)
@mark.parametrize("drift_id", DRIFTS, indirect=True)
class TestUserWithEdit(CanEdit, WithDatabase):
    """Test when user has edit rights on the experiment."""
