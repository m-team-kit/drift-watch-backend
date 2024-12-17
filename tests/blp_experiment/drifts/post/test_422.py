"""Testing module for endpoint methods /drifts."""

# pylint: disable=redefined-outer-name
from pytest import mark


class CommonBaseTests:
    """Common tests for the /drifts endpoint."""

    def test_status_code(self, response):
        """Test the 422 response."""
        assert response.status_code == 422
        assert response.json["code"] == 422


@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
class WithDatabase(CommonBaseTests):
    """Base class for tests using database."""


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class ValidAuth(CommonBaseTests):
    """Base class for valid authenticated tests."""


@mark.parametrize("subiss", [("user_4", "issuer.1")], indirect=True)
class Registered(ValidAuth, WithDatabase):
    """Tests for message response when user is  registered."""


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"


@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
class IsPrivate(WithDatabase):
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


@mark.parametrize("job_status", [None], indirect=True)
class MissingJobStatus(CommonBaseTests):
    """Test the response message for missing drift boolean."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "job_status" in response.json["errors"]["json"]
        errors = response.json["errors"]["json"]["job_status"]
        assert "Missing data for required field." in errors


@mark.parametrize("job_status", ["text"], indirect=True)
class InvalidJobStatus(CommonBaseTests):
    """Test the response message for invalid drift boolean."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "job_status" in response.json["errors"]["json"]
        errors = response.json["errors"]["json"]["job_status"]
        assert "Must be one of: Running, Completed, Failed." in errors


@mark.parametrize("model", [None], indirect=True)
class MissingModel(CommonBaseTests):
    """Test the response message for missing drift parameter."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "model" in response.json["errors"]["json"]
        errors = response.json["errors"]["json"]["model"]
        assert "Missing data for required field." in errors


@mark.parametrize("detected", [None], indirect=True)
class MissingDetected(CommonBaseTests):
    """Test the response message for missing drift boolean."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "drift_detected" in response.json["errors"]["json"]
        errors = response.json["errors"]["json"]["drift_detected"]
        assert "Missing data for required field." in errors


@mark.parametrize("detected", ["text"], indirect=True)
class NoBoolDetected(CommonBaseTests):
    """Test the response message for missing drift boolean."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "drift_detected" in response.json["errors"]["json"]
        errors = response.json["errors"]["json"]["drift_detected"]
        assert "Not a valid boolean." in errors


class TestBadBodyKey(UnknownField, IsPrivate, EditGroup, WithDatabase):
    """Test the unknown key parameter in body."""


class TestMissingJobStatus(MissingJobStatus, IsPrivate, EditGroup):
    """Test the response when missing concept drift boolean."""


class TestInvalidJobStatus(InvalidJobStatus, IsPrivate, EditGroup):
    """Test the response when invalid concept drift boolean."""


class TestMissingModel(MissingModel, IsPrivate, EditGroup):
    """Test the response when missing drift parameter."""


class TestMissingDetected(MissingDetected, IsPrivate, EditGroup):
    """Test the response when missing drift boolean."""


class TestNoBoolDetected(NoBoolDetected, IsPrivate, EditGroup):
    """Test the response when missing drift boolean."""
