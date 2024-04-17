"""User endpoint, edit on app>blueprints>user.
# TODO: Improve this endpoint description
"""

import uuid
from datetime import datetime as dt

import marshmallow as ma
from app import schemas
from app.config import Blueprint
from app.tools.authentication import Authentication
from app.tools.database import CONFLICT
from flask import current_app
from flask.views import MethodView
from flask_smorest import abort  # type: ignore

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
        """Method docs, edit app>blueprints>user>Users.
        ---
        Internal comment not meant to be exposed.
        # TODO: improve this doc endpoint.
        """
        users = current_app.config["db"]["app.blueprints.user"]
        page = pagination_parameters.page
        page_size = pagination_parameters.page_size
        return users.find(json).skip((page - 1) * page_size).limit(page_size)

    @auth.access_level("new_user")
    @auth.inject_user_infos()
    @blp.arguments(ma.Schema(), location="json", unknown="raise")
    @blp.doc(responses={409: CONFLICT})
    @blp.response(201, schemas.User)
    def post(self, _json, user_infos):
        """Method docs, edit app>blueprints>user>Users.
        ---
        Internal comment not meant to be exposed.
        # TODO: improve this doc endpoint.
        # TODO: fix error messages, point to issues
        """
        users = current_app.config["db"]["app.blueprints.user"]
        sub, iss = user_infos["sub"], user_infos["iss"]
        if users.find_one({"subject": sub, "issuer": iss}):
            abort(409, message="User already exists")
        user = {
            "_id": str(uuid.uuid4()),
            "created_at": dt.now().isoformat(),
            "subject": user_infos["sub"],
            "issuer": user_infos["iss"],
            "email": user_infos["email"],
            "drift_ids": [],
        }
        users.insert_one(user)
        return user
