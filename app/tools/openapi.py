"""
OpenAPI documentation configuration for the Drift Watch Backend.

This module configures the automatic OpenAPI (Swagger) documentation generation
using Flask-SMOREST. It registers all API blueprints and defines the OpenAPI
specification metadata including security schemes, API information, and
endpoint documentation.

The generated OpenAPI specification includes:
- Complete API endpoint documentation
- Request/response schema definitions
- Authentication requirements and security schemes
- Error response documentation
- Interactive Swagger UI for API testing

Security:
- Uses JWT Bearer token authentication
- All endpoints require valid JWT tokens unless explicitly marked as public
- Security scheme is automatically applied to protected endpoints

API Structure:
- /user: User management and authentication endpoints
- /experiment: Experiment management and metadata
- /experiment/{id}/drift: Drift detection run management
"""

from flask_smorest import Api  # type: ignore

from app import blueprints as blp


def init_app(app):
    """
    Initialize OpenAPI documentation and register API blueprints.

    Sets up the Flask-SMOREST API documentation system and registers all
    application blueprints with their respective URL prefixes. Creates the
    interactive Swagger UI for API exploration and testing.

    Args:
        app (Flask): The Flask application instance to configure

    Side Effects:
        - Creates API documentation at /docs endpoint
        - Registers all blueprints with URL prefixes
        - Sets up OpenAPI specification with security schemes
        - Enables automatic request/response validation
    """
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
        "summary": "Drift Detection Monitoring API for Machine Learning Models",
        "description": (
            "A comprehensive REST API for tracking and monitoring data and concept "
            "drift in machine learning models. This service provides endpoints for "
            "managing experiments, storing drift detection results, and querying "
            "drift metrics with flexible filtering and pagination capabilities.\n\n"
            "## Key Features\n"
            "- **Experiment Management**: Create and manage experiments as containers for drift runs\n"
            "- **Drift Tracking**: Store and retrieve drift detection results with detailed metadata\n"
            "- **Access Control**: Role-based permissions with public/private experiment support\n"
            "- **Search & Filter**: Advanced MongoDB-style querying with sorting and pagination\n"
            "- **User Management**: JWT-based authentication with entitlement support\n\n"
            "## Authentication\n"
            "This API uses JWT Bearer tokens for authentication. Obtain a token from your "
            "OpenID Connect provider and include it in the Authorization header:\n"
            "`Authorization: Bearer <your-jwt-token>`\n\n"
            "## Permission Levels\n"
            "- **Read**: View experiments and drift data\n"
            "- **Edit**: Modify experiments and create drift records  \n"
            "- **Manage**: Full control including deletion and permission management"
        ),
        "termsOfService": "https://github.com/m-team-kit/drift-watch-backend/blob/main/LICENSE",
        "contact": {
            "name": "Drift Watch API Support",
            "url": "https://github.com/m-team-kit/drift-watch-backend/issues",
            "email": "support@driftwatch.io",
        },
        "license": {
            "name": "Apache V2 License",
            "url": "https://github.com/m-team-kit/drift-watch-backend/blob/main/LICENSE",
        },
        "version": "1.0.0",
    },
    "components": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT token obtained from OpenID Connect provider",
            }
        }
    },
    "servers": [{"url": "/", "description": "Current server"}],
    "tags": [
        {"name": "Experiments", "description": "Experiment management and metadata operations"},
        {"name": "Drifts", "description": "Drift detection run management and querying"},
        {"name": "Users", "description": "User authentication and profile management"},
        {"name": "Entitlements", "description": "User role and permission information"},
    ],
}
