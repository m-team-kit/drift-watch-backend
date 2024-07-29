"""
## API Methods to list, register and remove users.
"""

import uuid
from datetime import datetime as dt

import marshmallow as ma
from flask import abort, current_app
from flask.views import MethodView

from app import schemas
from app.config import Blueprint
from app.tools.authentication import Authentication
from app.tools.database import CONFLICT

blp = Blueprint("user", __name__, description=__doc__)
auth = Authentication(blueprint=blp)


@blp.route("")
class Users(MethodView):
    """Users API."""

    @auth.access_level("admin")
    @blp.arguments(schemas.ma.Schema(), location="json", unknown="include")
    @blp.response(200, schemas.User(many=True))
    @blp.paginate()
    def get(self, json, pagination_parameters):
        """Retrieve a paginated list of users based on the provided JSON query
        and MongoDB format.
        ---
        Internal comment not meant to be exposed.

        Args:
            json: The JSON query used to filter the users.
            pagination_parameters: The pagination parameters.

        Returns:
            401: If the user is not authenticated or registered.
            403: If the user does not have the required permissions.
            422: If the JSON query is not in the correct format.
        """
        # Search for users based on the provided JSON query.
        users = current_app.config["db"]["app.users"]
        search = users.find(json)

        # Return the paginated list of users.
        page = pagination_parameters.page
        page_size = pagination_parameters.page_size
        return search.skip((page - 1) * page_size).limit(page_size)

    @auth.access_level("user")
    @auth.inject_user_infos()
    @blp.arguments(ma.Schema(), location="json", unknown="raise")
    @blp.doc(responses={409: CONFLICT})
    @blp.response(201, schemas.User)
    def post(self, _json, user_infos):
        """Register and create the token owner as new user.
        ---
        Internal comment not meant to be exposed.

        Args:
            _json (dict): The JSON payload of the request.
            user_infos (dict): User information from the authentication token.

        Returns:
            dict: The newly created user.

        Raises:
            401: If the user is not authenticated with a valid token.
            409: If the user already registered.
            422: If a JSON is provided.
        """
        # Check if the user already exists.
        users = current_app.config["db"]["app.users"]
        sub, iss = user_infos["sub"], user_infos["iss"]
        if users.find_one({"subject": sub, "issuer": iss}):
            abort(409, "User already exists.")

        # Create the new user from the token information.
        user = {
            "email": user_infos["email"],
            "subject": user_infos["sub"],
            "issuer": user_infos["iss"],
            "_id": str(uuid.uuid4()),
            "created_at": dt.now().isoformat(),
        }

        # Store the user and return it as response body.
        users.insert_one(user)
        return user
