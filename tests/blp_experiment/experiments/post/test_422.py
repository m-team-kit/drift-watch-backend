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


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.usefixtures("accept_authorization")
class ValidAuth(CommonBaseTests):
    """Base class for valid authenticated tests."""


@mark.parametrize("subiss", [("user_4", "issuer.1")], indirect=True)
class Registered(ValidAuth):
    """Tests for message response when user is  registered."""


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
        assert "Not a valid mapping type." in errors["permissions"]


class TestBadBodyKey(Registered, UnknownField):
    """Test the unknown key parameter in body."""


class TestNoBoolPublic(Registered, NoBoolPublic):
    """Test the response when missing concept experiment boolean."""


class TestNoListPerm(Registered, NoListPerm):
    """Test the response when missing concept experiment parameter."""
