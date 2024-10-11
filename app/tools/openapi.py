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
    api.register_blueprint(blp.entitlement, url_prefix="/entitlement")
    api.register_blueprint(blp.experiment, url_prefix="/experiment")
    api.register_blueprint(blp.user, url_prefix="/user")


OPTIONS = {
    "openapi_version": "3.1.0",
    "security": [{"bearerAuth": []}],
    "info": {
        "summary": "A drift tracking server.",
        "description": (
            "This is server to track and monitor data and concept "
            "drifts for machine learning models."
        ),
        "termsOfService": "TODO: Add terms of service",  # TODO
        "contact": {  # TODO: add contact
            "name": "API Support",
            "url": "https://www.example.com/support",
            "email": "support@example.com",
        },
        "license": {  # TODO: add link to license
            "name": "MIT License",
            "url": "https://www.example.com/support",
        },
    },
    "components": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
}
