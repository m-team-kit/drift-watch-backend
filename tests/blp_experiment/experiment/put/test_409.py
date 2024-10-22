"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import mark


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


@mark.parametrize("subiss", [("user_4", "issuer.1")], indirect=True)
class Registered(ValidAuth):
    """Tests for message response when user is  registered."""


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
class IsPrivate(CommonBaseTests):
    """Base class for group with public as false."""


ENT_MANAGE = "urn:mace:egi.eu:group:vo_example1:role=manage#x.0"
ENT_EDIT = "urn:mace:egi.eu:group:vo_example1:role=edit#x.0"
ENT_READ = "urn:mace:egi.eu:group:vo_example1:role=read#x.0"


@mark.parametrize("entitlements", [[ENT_MANAGE]], indirect=True)
class ManageGroup(Registered):
    """Base class for group with manage entitlement tests."""


@mark.parametrize("name", ["experiment_2"], indirect=True)
class ConflictName(WithDatabase):
    """Test response message contains name conflict."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert response.json["status"] == "Conflict"
        assert response.json["message"] == "Name conflict."


class TestRepeatedName(ManageGroup, IsPrivate, ConflictName):
    """Test the response when name exists in database."""
