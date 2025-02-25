"""Testing module for endpoint methods /experiment."""

# pylint: disable=redefined-outer-name
from pytest import mark


class CommonBaseTests:
    """Common tests for the /experiment endpoint."""

    def test_status_code(self, response):
        """Test the 422 response."""
        assert response.status_code == 422
        assert response.json["code"] == 422


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


@mark.parametrize("body", [{"unknown": "val"}], indirect=True)
class UnknownField(WithDatabase):
    """Test the response message for unknown key in body."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"].values()
        assert ["Unknown field."] in errors


@mark.parametrize("public", ["str"], indirect=True)
class NoBoolPublic(WithDatabase):
    """Test the response message for missing experiment boolean."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"]
        assert "Not a valid boolean." in errors["public"]


@mark.parametrize("permissions", ["str"], indirect=True)
class NoListPerm(WithDatabase):
    """Test the response message for missing experiment parameter."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"]
        assert "Not a valid list." in errors["permissions"]


BAD_PERMISSIONS = [[{"entity": "g1", "level": "bad_level"}]]


@mark.parametrize("permissions", [BAD_PERMISSIONS[0]], indirect=True)
class BadLevel(WithDatabase):
    """Test the response message for bad permission level."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"]
        level_error = errors["permissions"]["0"]["level"]
        assert "Must be one of: Read, Write, Manage." in level_error


class TestBadBodyKey(UnknownField, IsPrivate, ManageGroup):
    """Test the unknown key parameter in body."""


class TestNoBoolPublic(NoBoolPublic, IsPrivate, ManageGroup):
    """Test the response when missing concept experiment boolean."""


class TestNoListPerm(NoListPerm, IsPrivate, ManageGroup):
    """Test the response when missing concept experiment parameter."""


class TestUnknownLevel(BadLevel, ManageGroup, IsPrivate):
    """Test the response when unknown level in permissions."""
