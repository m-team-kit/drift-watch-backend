"""API documentation generation."""

from app import blueprints as blp
from flask_smorest import Api  # type: ignore


def init_app(app):
    """Initialize the api endpoints."""
    api = app.config["api"] = Api(app, spec_kwargs=OPTIONS)
    # Register Custom Fields
    # api.register_field(ObjectId, "string", "ObjectId")
    # api.register_field(CustomString, "string", None)
    # api.register_field(CustomDateTime, ma.fields.DateTime)
    # Register Custom Path Parameter Converters
    pass
    # Register Blueprints
    api.register_blueprint(blp.drift, url_prefix="/drift")
    api.register_blueprint(blp.user, url_prefix="/user")


OPTIONS = {
    "openapi_version": "3.1.0",
    "security": [
        {"bearerAuth": []},
    ],
    "components": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
    # "info": {},  # TODO: add license
}
