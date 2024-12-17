"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import mark


DRIFT_1 = "00000000-0000-0000-0000-000000000001"


@mark.parametrize("drift_id", [DRIFT_1], indirect=True)
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
class TestUnknownField(WithDatabase, IsPrivate, EditGroup):
    """Test the response message for unknown key in body."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"].values()
        assert ["Unknown field."] in errors


@mark.parametrize("body", [{"job_status": None}], indirect=True)
class TestMissingJobStatus(WithDatabase, IsPrivate, EditGroup):
    """Test the response message for missing job status."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "job_status" in response.json["errors"]["json"]
        errors = response.json["errors"]["json"]["job_status"]
        assert "Field may not be null." in errors


@mark.parametrize("body", [{"job_status": "string"}], indirect=True)
class TestInvalidJobStatus(WithDatabase, IsPrivate, EditGroup):
    """Test the response message for invalid job status."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "job_status" in response.json["errors"]["json"]
        errors = response.json["errors"]["json"]["job_status"]
        assert "Must be one of: Running, Completed, Failed." in errors


@mark.parametrize("body", [{"tags": "string"}], indirect=True)
class TestInvalidTags(WithDatabase, IsPrivate, EditGroup):
    """Test the response message for invalid tags."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "tags" in response.json["errors"]["json"]
        errors = response.json["errors"]["json"]["tags"]
        assert "Not a valid list." in errors


@mark.parametrize("body", [{"drift_detected": None}], indirect=True)
class TestMissingDetected(WithDatabase, IsPrivate, EditGroup):
    """Test the response message for missing drift detected."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "drift_detected" in response.json["errors"]["json"]
        errors = response.json["errors"]["json"]["drift_detected"]
        assert "Field may not be null." in errors


@mark.parametrize("body", [{"drift_detected": "string"}], indirect=True)
class TestInvalidDetected(WithDatabase, IsPrivate, EditGroup):
    """Test the response message for invalid drift detected."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "drift_detected" in response.json["errors"]["json"]
        errors = response.json["errors"]["json"]["drift_detected"]
        assert "Not a valid boolean." in errors


@mark.parametrize("body", [{"parameters": None}], indirect=True)
class TestMissingParam(WithDatabase, IsPrivate, EditGroup):
    """Test the response message for missing parameters."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        assert "parameters" in response.json["errors"]["json"]
        errors = response.json["errors"]["json"]["parameters"]
        assert "Field may not be null." in errors
