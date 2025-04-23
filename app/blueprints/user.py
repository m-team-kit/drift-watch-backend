"""
## API Methods to list, register and remove users.
"""

import uuid
from datetime import datetime as dt

import marshmallow as ma
from flask import abort, current_app
from flask.views import MethodView

from app import schemas, utils
from app.config import Blueprint
from app.tools.authentication import Authentication
from app.tools.database import CONFLICT

blp = Blueprint("Users", __name__, description=__doc__)
auth = Authentication(blueprint=blp)


@blp.route("search")
class UsersSearch(MethodView):
    """Users API Custom method Search."""

    @auth.access_level("admin")
    @blp.arguments(ma.Schema(), location="json", unknown="include")
    @blp.arguments(schemas.SearchUsers(), location="query", unknown="include")
    @blp.response(200, schemas.User(many=True))
    @blp.paginate()
    def post(self, json, query_args, pagination_parameters):
        """Retrieve a paginated list of users based on the provided JSON query
        and MongoDB format.
        ---
        Internal comment not meant to be exposed.

        Args:
            json: The JSON query used to filter the users.
            query_args: A dictionary of query parameters.
            pagination_parameters: The pagination parameters.

        Returns:
            401: If the user is not authenticated or registered.
            403: If the user does not have the required permissions.
            422: If the JSON query is not in the correct format.
        """
        # Extract sort_by and order_by from query_args
        sort_by, order_by = query_args["sort_by"], query_args["order_by"]
        sort_order = 1 if order_by == "asc" else -1

        # Search for users based on the provided JSON query.
        users = current_app.config["db"]["app.users"]
        search = users.find(json).sort(sort_by, sort_order)

        # Return the paginated list of users.
        page = pagination_parameters.page
        page_size = pagination_parameters.page_size
        item_count = users.count_documents(json)

        # Return the paginated list of users.
        pagination_parameters.item_count = item_count
        return search.skip((page - 1) * page_size).limit(page_size)


@blp.route("")
class Users(MethodView):
    """Users API."""

    @auth.access_level("user")
    @auth.inject_user_infos()
    @blp.doc(responses={409: CONFLICT})
    @blp.response(201, schemas.User)
    def post(self, user_infos):
        """Register and create the token owner as new user.
        ---
        Internal comment not meant to be exposed.

        Args:
            user_infos (dict): User information from the authentication token.

        Returns:
            dict: The newly created user.

        Raises:
            401: If the user is not authenticated with a valid token.
            403: If the user does not have the required permissions.
            409: If the user already registered.
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


@blp.route("/self")
class Self(MethodView):
    """Users API."""

    @auth.access_level("user")
    @auth.inject_user_infos()
    @blp.response(200, schemas.User())
    def get(self, user_infos):
        """Retrieves the user information based on the provided auth token.
        ---
        Internal comment not meant to be exposed.

        Args:
            user_infos (dict): User information from the authentication token.

        Returns:
            401: If the user is not authenticated or registered.
            403: If the user does not have the required permissions.
        """
        # Check if the user is registered and validate access level.
        # Return the user information.
        return utils.get_user(user_infos)

    @auth.access_level("user")
    @auth.inject_user_infos()
    @blp.response(200, schemas.User())
    def put(self, user_infos):
        """Updates the user information based on the provided auth token.
        ---
        Internal comment not meant to be exposed.

        Args:
            user_infos (dict): User information from the authentication token.

        Returns:
            401: If the user is not authenticated or registered.
            403: If the user does not have the required permissions.
        """
        # Check if the user is registered and validate access level.
        user = utils.get_user(user_infos)

        # Update the user information and return it.
        users = current_app.config["db"]["app.users"]
        user["email"] = user_infos["email"]
        users.update_one({"_id": user["_id"]}, {"$set": user})
        return user
