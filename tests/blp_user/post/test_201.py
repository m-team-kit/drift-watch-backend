"""Testing module for endpoint methods /user."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from uuid import UUID

from pytest import mark


@mark.parametrize("auth", ["mock-token"], indirect=True)
@mark.parametrize("with_database", ["database_1"], indirect=True)
@mark.usefixtures("with_context", "with_database")
@mark.usefixtures("accept_authorization")
class CommonBaseTests:
    """Common tests for the /user endpoint."""

    def test_status_code(self, response):
        """Test the 201 response."""
        assert response.status_code == 201

    def test_in_database(self, response, db_user):
        """Test the response items are in the database."""
        assert db_user is not None
        assert response.json == db_user

    def test_user_id(self, response):
        """Test the response item have correct id."""
        assert UUID(response.json["id"]).version == 4

    def test_created_at(self, response):
        """Test the response item has a correct created_at."""
        assert dt.fromisoformat(response.json["created_at"])

    def test_user_subject(self, response, subiss):
        """Test the response item have correct subject."""
        assert response.json["subject"] == subiss[0]

    def test_user_issuer(self, response, subiss):
        """Test the response item have correct issuer."""
        assert response.json["issuer"] == subiss[1]

    def test_user_email(self, response, email):
        """Test the response item have correct email."""
        assert response.json["email"] == email


@mark.parametrize("subiss", [("user_a", "issuer_a")], indirect=True)
class TestRegister(CommonBaseTests):
    """Test the responses items."""
