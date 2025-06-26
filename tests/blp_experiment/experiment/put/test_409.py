"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import mark

from tests.constants import *


class CommonBaseTests:
    """Common tests for the /experiment endpoint."""

    def test_status_code(self, response):
        """Test the 409 response."""
        assert response.status_code == 409
        assert response.json["code"] == 409


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""

    def test_not_saved(self, response, db_experiment):
        """Test the response items are in the database."""
        assert db_experiment is not None
        assert response.json != db_experiment


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class ValidAuth(CommonBaseTests):
    """Base class for valid authenticated tests."""


@mark.parametrize("experiment_id", PRIVATE_EXPS + PUBLIC_EXPS, indirect=True)
class AnyExperiment(CommonBaseTests):
    """Base class for group with public as false."""


# TODO: @mark.parametrize("user_info", CAN_MANAGE, indirect=True)
@mark.parametrize("user_info", ["egi-manage"], indirect=True)
class CanManage(ValidAuth):
    """Base class for group with manage entitlement tests."""


@mark.parametrize("name", ["conflict_exp"], indirect=True)
class ConflictName(WithDatabase):
    """Test response message contains name conflict."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Conflict"
        assert response.json["message"] == "Name conflict."


class TestRepeatedName(CanManage, AnyExperiment, ConflictName):
    """Test the response when name exists in database."""
