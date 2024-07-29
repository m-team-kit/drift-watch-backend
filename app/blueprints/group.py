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
from app.tools.database import CONFLICT, NOT_FOUND

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
            409: If a group attribute conflicts an existing groups.
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


@blp.route("/<uuid:group_id>")
class Group(MethodView):
    """Group API."""

    @auth.access_level("user")
    @blp.doc(responses={"404": NOT_FOUND})
    @blp.response(200, schemas.Group)
    def get(self, group_id):
        """Retrieve an group by its ID from the database.
        ---
        Internal comment not meant to be exposed.

        Args:
            group_id (str): The ID of the group to retrieve.

        Returns:
            dict: The group object.

        Raises:
            401: If the user is not authenticated.
            404: If the group with the specified ID is not found.
        """
        group_id = str(group_id)
        return utils.get_group(group_id)

    @auth.access_level("user")
    @auth.inject_user_infos()
    @blp.arguments(schemas.Group, location="json", unknown="raise")
    @blp.doc(responses={"404": NOT_FOUND})
    @blp.response(200, schemas.Group)
    def put(self, json, group_id, user_infos):
        """
        Update a group record with the given JSON data.
        ---
        Internal comment not meant to be exposed.

        Args:
            json (dict): The JSON data containing the updated drift information.
            group_id (str): The ID of the group to retrieve drifts from.
            user_infos (dict): User information from the authentication token.

        Returns:
            dict: The updated group record.

        Raises:
            401: If the user is not authenticated or registered.
            403: If the user does not have the required permissions.
            404: If the drift or group specified are not found.
            409: If a group attribute conflicts an existing groups.
            422: If the JSON query is not in the correct format.
        """
        # Check if the user is registered and validate access level.
        user = utils.get_user(user_infos)
        group_id = str(group_id)
        group = utils.get_group(group_id)
        utils.check_member(user, group)

        # Modify the JSON object to include the user ID and permissions.
        group.update(json)
        if user["_id"] not in json["members"]:
            json["members"].append(user["_id"])

        # Replace the drift record in the database.
        groups = current_app.config["db"]["app.groups"]
        if groups.find_one({"name": json["name"]}):
            abort(409, "Name conflict.")
        groups.replace_one({"_id": group_id}, group)

        # Return the updated drift record.
        return group

    @auth.access_level("user")
    @auth.inject_user_infos()
    @blp.doc(responses={"404": NOT_FOUND})
    @blp.response(204)
    def delete(self, group_id, user_infos):
        """
        Delete a group record from the database.
        ---
        Internal comment not meant to be exposed.

        Args:
            json (dict): The JSON data containing the updated drift information.
            group_id (str): The ID of the group to retrieve drifts from.
            user_infos (dict): User information from the authentication token.

        Returns:
            dict: The updated group record.

        Raises:
            401: If the user is not authenticated or registered.
            403: If the user does not have the required permissions.
            404: If the drift or group specified are not found.
        """
        # Check if the user is registered and validate access level.
        user = utils.get_user(user_infos)
        group_id = str(group_id)
        group = utils.get_group(group_id)
        utils.check_member(user, group)

        # Replace the drift record in the database.
        groups = current_app.config["db"]["app.groups"]
        groups.delete_one({"_id": group_id})

        # Return empty response.
        return None
