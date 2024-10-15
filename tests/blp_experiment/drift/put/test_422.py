"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import mark


class CommonBaseTests:
    """Common tests for the /drift endpoint."""

    def test_status_code(self, response):
        """Test the 422 response."""
        assert response.status_code == 422
        assert response.json["code"] == 422


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""

    def test_not_saved(self, response, db_drift):
        """Test the response items are in the database."""
        assert db_drift is not None
        assert response.json != db_drift


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


@mark.parametrize("entitlements", [[ENT_EDIT]], indirect=True)
class EditGroup(Registered):
    """Base class for group with manage entitlement tests."""


@mark.parametrize("body", [{"unknown": "val"}], indirect=True)
class UnknownField(CommonBaseTests):
    """Test the response message for unknown key in body."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"].values()
        assert ["Unknown field."] in errors


NO_BOOL_CD_BODY = {"concept_drift": {"drift": "a", "parameters": {"n": 0}}}
NO_BOOL_DD_BODY = {"data_drift": {"drift": "a", "parameters": {"n": 0}}}


@mark.parametrize("body", [NO_BOOL_CD_BODY, NO_BOOL_DD_BODY], indirect=True)
class NoBoolDrift(CommonBaseTests):
    """Test the response message for missing drift boolean."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"].values()
        assert {"drift": ["Not a valid boolean."]} in errors


NO_PRAM_CD_BODY = {"concept_drift": {"drift": True}}
NO_PRAM_DD_BODY = {"data_drift": {"drift": True}}


@mark.parametrize("body", [NO_PRAM_CD_BODY, NO_PRAM_DD_BODY], indirect=True)
class MissingParam(CommonBaseTests):
    """Test the response message for missing drift parameter."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"].values()
        assert {"_schema": ["Include parameters if drift."]} in errors


DRIFT_1 = "00000000-0000-0000-0000-000000000001"


@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
class TestBadBodyKey(UnknownField, IsPrivate, EditGroup, WithDatabase):
    """Test the unknown key parameter in body."""


@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
class TestNoBoolDrift(NoBoolDrift, IsPrivate, EditGroup, WithDatabase):
    """Test the response when missing concept drift boolean."""


@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
class TestMissingParam(MissingParam, IsPrivate, EditGroup, WithDatabase):
    """Test the response when missing concept drift parameter."""
