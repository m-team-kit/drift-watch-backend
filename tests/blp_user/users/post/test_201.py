"""Testing module for endpoint methods /user."""

# pylint: disable=redefined-outer-name
from datetime import datetime as dt
from uuid import UUID

from pytest import mark

from tests.constants import *


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

    def test_user_subject(self, response, user_info):
        """Test the response item have correct subject."""
        assert response.json["subject"] == user_info["sub"]

    def test_user_issuer(self, response, user_info):
        """Test the response item have correct issuer."""
        assert response.json["issuer"] == user_info["iss"]

    def test_user_email(self, response, user_info):
        """Test the response item have correct email."""
        assert response.json["email"] == user_info["email"]


@mark.parametrize("user_info", ["ai4eosc-unregist"], indirect=True)
class TestRegister(CommonBaseTests):
    """Test the responses items."""
