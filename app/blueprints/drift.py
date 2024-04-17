"""Drift endpoint, edit on app>blueprints>drift.
# TODO: Improve this endpoint description
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
        """Method docs, edit app>blueprints>drift>Drifts.
        ---
        Internal comment not meant to be exposed.
        # TODO: improve this doc endpoint.
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
        """Method docs, edit app>blueprints>drift>Drifts.
        ---
        Internal comment not meant to be exposed.
        # TODO: improve this doc endpoint.
        # TODO: fix error messages, point to issues
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
        """Method docs, edit app>blueprints>drift>Drift.
        ---
        Internal comment not meant to be exposed.
        # TODO: improve this doc endpoint.
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
        """Method docs, edit app>blueprints>drift>Drift.
        ---
        Internal comment not meant to be exposed.
        # TODO: improve this doc endpoint.
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
        """Method docs, edit app>blueprints>drift>Drift.
        ---
        Internal comment not meant to be exposed.
        # TODO: improve this doc endpoint.
        """
        drifts = current_app.config["db"]["app.blueprints.drift"]
        drift = drifts.find_one({"_id": str(drift_id)})
        if not drift:
            abort(404)
        drifts.delete_one({"_id": str(drift_id)})
