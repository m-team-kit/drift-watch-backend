"""
## API Methods to list, register and remove groups.
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

blp = Blueprint("group", __name__, description=__doc__)
auth = Authentication(blueprint=blp)


@blp.route("")
class Groups(MethodView):
    """Groups API."""

    @auth.access_level("user")
    @blp.arguments(ma.Schema(), location="json", unknown="include")
    @blp.response(200, schemas.Group(many=True))
    @blp.paginate()
    def get(self, json, pagination_parameters):
        """Retrieve a paginated list of groups based on the provided JSON query
        and MongoDB format.
        ---
        Internal comment not meant to be exposed.

        Args:
            json: The JSON query used to filter the groups.
            pagination_parameters: The pagination parameters.

        Returns:
            A paginated list of groups based on the provided query.

        Raises:
            401: If the user is not authenticated.
            422: If the JSON query is not in the correct format.
        """
        # Search for groups based on the provided JSON query.
        groups = current_app.config["db"]["app.groups"]
        search = groups.find(json)

        # Return the paginated list of groups.
        page = pagination_parameters.page
        page_size = pagination_parameters.page_size
        return search.skip((page - 1) * page_size).limit(page_size)

    @auth.access_level("user")
    @auth.inject_user_infos()
    @blp.arguments(schemas.Group, location="json", unknown="raise")
    @blp.doc(responses={409: CONFLICT})
    @blp.response(201, schemas.Group)
    def post(self, json, user_infos):
        """Register and create the token owner as new group.
        ---
        Internal comment not meant to be exposed.

        Args:
            _json (dict): The JSON payload of the request.
            user_infos (dict): User information obtained from the

        Returns:
            dict: The newly created group.

        Raises:
            401: If the user is not authenticated or registered.
            403: If the user does not have the required permissions.
            409: If the group already exists.
            422: If the JSON query is not in the correct format.
        """
        # Check if the user is registered and retrieve the user object.
        user = utils.get_user(user_infos)

        # Modify the JSON object to include the user ID and permissions.
        json["created_at"] = dt.now().isoformat()
        json["_id"] = str(uuid.uuid4())
        if user["_id"] not in json["members"]:
            json["members"].append(user["_id"])

        # Insert it into the database.
        groups = current_app.config["db"]["app.groups"]
        if groups.find_one({"name": json["name"]}):
            abort(409, "Name conflict.")
        groups.insert_one(json)

        # Return the updated user object.
        return json
