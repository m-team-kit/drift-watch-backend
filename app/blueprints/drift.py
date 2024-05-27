"""
## API Methods to create, read, update and delete drift detection jobs.
"""

import uuid
from datetime import datetime as dt

import marshmallow as ma
from app import schemas
from app.config import Blueprint
from app.tools.authentication import Authentication
from app.tools.database import NOT_FOUND
from flask import current_app
from flask.views import MethodView
from flask_smorest import abort  # type: ignore

blp = Blueprint("drift", __name__, description=__doc__)
auth = Authentication(blueprint=blp)


@blp.route("")
class Drifts(MethodView):
    """Drifts API."""

    @auth.access_level("everyone")
    @blp.arguments(ma.Schema(), location="json", unknown="include")
    @blp.response(200, schemas.DriftV100(many=True))
    @blp.paginate()
    def get(self, json, pagination_parameters):
        """
        Get a paginated list of drift Jobs based on the provided JSON query
        and MongoDB format.
        ---
        Internal comment not meant to be exposed.

        Args:
            json: A JSON object representing the query parameters.
            pagination_parameters: An object containing pagination parameters.

        Returns:
            A paginated list of drifts matching the query.

        Raises:
            None
        """
        drifts = current_app.config["db"]["app.blueprints.drift"]
        page = pagination_parameters.page
        page_size = pagination_parameters.page_size
        return drifts.find(json).skip((page - 1) * page_size).limit(page_size)

    @auth.access_level("registered")
    @auth.inject_user_infos()
    @blp.arguments(schemas.DriftV100, location="json")
    @blp.response(201, schemas.DriftV100)
    def post(self, json, user_infos):
        """Create a new drift Job record in the database.
        ---
        Internal comment not meant to be exposed.

        Args:
            json (dict): The JSON payload containing the drift information.
            user_infos (dict): User information obtained from the
                               authentication process.

        Returns:
            dict: The newly created drift record.

        Raises:
            None
        """
        drifts = current_app.config["db"]["app.blueprints.drift"]
        users = current_app.config["db"]["app.blueprints.user"]
        sub, iss = user_infos["sub"], user_infos["iss"]
        user = users.find_one({"subject": sub, "issuer": iss})
        json["_id"] = str(uuid.uuid4())
        json["datetime"] = dt.now().isoformat()
        drifts.insert_one(json)
        user["drift_ids"].append(json["_id"])
        users.replace_one({"_id": str(user["_id"])}, user)
        return json


@blp.route("/<uuid:drift_id>")
class Drift(MethodView):
    """Drift API."""

    @auth.access_level("everyone")
    @blp.doc(responses={"404": NOT_FOUND})
    @blp.response(200, schemas.DriftV100)
    def get(self, drift_id):
        """Retrieve a drift job by its id from the database.
        ---
        Internal comment not meant to be exposed.

        Args:
            drift_id (str): The ID of the drift to retrieve.

        Returns:
            dict: The drift object.

        Raises:
            404: If the drift with the specified ID is not found.
        """
        drifts = current_app.config["db"]["app.blueprints.drift"]
        drift = drifts.find_one({"_id": str(drift_id)})
        if not drift:
            abort(404)
        return drift

    @auth.access_level("drift_owner")
    @blp.arguments(schemas.DriftV100, location="json")
    @blp.doc(responses={"404": NOT_FOUND})
    @blp.response(200, schemas.DriftV100)
    def put(self, json, drift_id):
        """
        Update a drift job record with the given JSON data.
        ---
        Internal comment not meant to be exposed.

        Args:
            json (dict): The JSON data containing the updated drift information.
            drift_id (str): The ID of the drift record to be updated.

        Returns:
            dict: The updated drift record.

        Raises:
            404: If the drift record with the given ID is not found.
        """
        drifts = current_app.config["db"]["app.blueprints.drift"]
        drift = drifts.find_one({"_id": str(drift_id)})
        if not drift:
            abort(404)
        drift.update(json)
        drifts.replace_one({"_id": str(drift_id)}, drift)
        return drift

    @auth.access_level("drift_owner")
    @blp.doc(responses={"404": NOT_FOUND})
    @blp.response(204)
    def delete(self, drift_id):
        """
        Delete a drift job record from the database.
        ---
        Internal comment not meant to be exposed.

        Args:
            drift_id (str): The ID of the drift record to be deleted.

        Returns:
            None

        Raises:
            404: If the drift record with the given ID is not found.
        """
        drifts = current_app.config["db"]["app.blueprints.drift"]
        drift = drifts.find_one({"_id": str(drift_id)})
        if not drift:
            abort(404)
        drifts.delete_one({"_id": str(drift_id)})
