"""Testing module for endpoint methods /drift."""

# pylint: disable=redefined-outer-name
from pytest import mark


EXPERIMENT_1 = "00000000-0000-0001-0001-000000000001"


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("experiment_id", [EXPERIMENT_1], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /drift endpoint."""

    def test_status_code(self, response):
        """Test the 422 response."""
        assert response.status_code == 422
        assert response.json["code"] == 422


class UnknownField:
    """Test the response message for unknown key in body."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"].values()
        assert ["Unknown field."] in errors


class NoBoolDrift:
    """Test the response message for missing drift boolean."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"].values()
        assert {"drift": ["Not a valid boolean."]} in errors


class MissingParam:
    """Test the response message for missing drift parameter."""

    def test_error_msg(self, response):
        """Test message contains useful information."""
        errors = response.json["errors"]["json"].values()
        assert {"_schema": ["Include parameters if drift."]} in errors


DRIFT_V100_1 = "00000000-0000-0000-0000-000000000001"
BAD_DRIFT_1 = {"drift": "str", "parameters": {"p_value": 5}}
BAD_DRIFT_2 = {"drift": True, "parameters": {}}


@mark.parametrize("drift_id", [DRIFT_V100_1], indirect=True)
@mark.parametrize("body", [{"unknown": "val"}], indirect=True)
class TestBadBodyKey(UnknownField, CommonBaseTests):
    """Test the unknown key parameter in body."""


@mark.parametrize("drift_id", [DRIFT_V100_1], indirect=True)
@mark.parametrize("concept_drift", [BAD_DRIFT_1], indirect=True)
class TestNoCBoolDrift(NoBoolDrift, CommonBaseTests):
    """Test the response when missing concept drift boolean."""


@mark.parametrize("drift_id", [DRIFT_V100_1], indirect=True)
@mark.parametrize("data_drift", [BAD_DRIFT_1], indirect=True)
class TestNoDBoolDrift(NoBoolDrift, CommonBaseTests):
    """Test the response when missing data drift boolean."""


@mark.parametrize("drift_id", [DRIFT_V100_1], indirect=True)
@mark.parametrize("concept_drift", [BAD_DRIFT_2], indirect=True)
class TestMissingCParam(MissingParam, CommonBaseTests):
    """Test the response when missing concept drift parameter."""


@mark.parametrize("drift_id", [DRIFT_V100_1], indirect=True)
@mark.parametrize("concept_drift", [BAD_DRIFT_2], indirect=True)
class TestMissingCDrift(MissingParam, CommonBaseTests):
    """Test the response when missing data drift parameter."""
