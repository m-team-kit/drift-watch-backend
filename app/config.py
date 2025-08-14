"""
Configuration management for the Drift Watch Backend application.

This module defines the application configuration using Pydantic Settings for
type-safe configuration management with environment variable support and secrets
handling. It also customizes Flask-SMOREST behavior for API request parsing.

Configuration Sources:
- Environment variables (prefixed with APP_)
- Secret files from configured secrets directory
- Default values defined in Settings class

Key Configuration Areas:
- API metadata and OpenAPI settings
- Database connection parameters  
- Authentication and authorization settings
- Request parsing and validation behavior

The configuration system supports different environments through environment
variables and provides secure secret management through file-based secrets.
"""

# https://docs.pydantic.dev/latest/concepts/pydantic_settings/
import os

import flask_smorest
from marshmallow import INCLUDE, RAISE
from pydantic_settings import BaseSettings, SettingsConfigDict
from webargs.flaskparser import FlaskParser


class Settings(BaseSettings):
    """
    Application configuration settings with environment variable support.
    
    Uses Pydantic Settings for type-safe configuration management with automatic
    environment variable loading and secrets file support. All settings can be
    overridden via environment variables prefixed with 'APP_'.
    
    Configuration Categories:
    
    API Settings:
        - API_TITLE: OpenAPI documentation title
        - API_VERSION: API version for documentation
        - OPENAPI_*: OpenAPI specification configuration
        
    Database Settings:
        - DATABASE_*: MongoDB connection parameters
        - Supports authentication and custom ports/hosts
        
    Authentication Settings:
        - ENTITLEMENTS_PATH: JWT claim path for user roles
        - USERS_ENTITLEMENTS: Required roles for user access
        - ADMIN_ENTITLEMENTS: Required roles for admin access
        - TRUSTED_OP_LIST: List of trusted OpenID providers
        
    Environment Variables:
        All settings can be set via environment variables:
        export APP_DATABASE_HOST=mongodb.example.com
        export APP_API_TITLE="Custom API Title"
        
    Secrets Management:
        Sensitive values are loaded from files in the secrets directory:
        - secrets/app_database_password
        - secrets/app_admin_entitlements (JSON array)
    """
    model_config = SettingsConfigDict(
        secrets_dir=os.environ["APP_SECRETS_DIR"],
        env_prefix="APP_",
        case_sensitive=False,
    )

    API_TITLE: str = "Drift Detection Monitor API"
    API_VERSION: str = "1.0.0"
    API_SPEC_OPTIONS: dict = {}
    TESTING: bool = False

    OPENAPI_JSON_PATH: str = "specification.json"
    OPENAPI_URL_PREFIX: str = "/"

    ENTITLEMENTS_PATH: str = "realm_access/roles"
    USERS_ENTITLEMENTS: list[str]
    ADMIN_ENTITLEMENTS: list[str]
    TRUSTED_OP_LIST: list[str]

    DATABASE_NAME: str = "drifts-data"
    DATABASE_PORT: int = 27017
    DATABASE_HOST: str
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str


class MyFlaskParser(FlaskParser):
    """
    Custom Flask request parser with enhanced error handling.
    
    Extends the default WebArgs FlaskParser to provide stricter validation
    behavior and better error messages for API requests. Configures different
    validation strategies for different request locations.
    
    Validation Strategy:
        - Query Parameters: INCLUDE unknown parameters (manual validation)
        - JSON Body: RAISE errors on unknown fields (strict validation)
        - Other locations: Use WebArgs defaults
        
    Benefits:
        - Prevents injection of unexpected query parameters
        - Ensures JSON request bodies match expected schemas exactly
        - Provides clear error messages for validation failures
        - Enables manual handling of query parameter validation where needed
    """
    DEFAULT_UNKNOWN_BY_LOCATION = {
        "query": INCLUDE,  # Manual raise 400 on unknown query parameters
        "json": RAISE,  # Raise 422 if json has unknown fields
        # ...
    }


class Blueprint(flask_smorest.Blueprint):
    """
    Custom Flask-SMOREST Blueprint with enhanced argument parsing.
    
    Extends the standard Flask-SMOREST Blueprint to use our custom request parser
    for consistent validation behavior across all API endpoints. All blueprints
    in the application inherit this behavior automatically.
    
    Features:
        - Uses MyFlaskParser for consistent request validation
        - Inherits all Flask-SMOREST features (OpenAPI docs, validation, etc.)
        - Provides foundation for all API blueprint definitions
        
    Usage:
        Use this class instead of flask_smorest.Blueprint when defining API blueprints:
        
        from app.config import Blueprint
        blp = Blueprint("MyAPI", __name__, description="My API endpoints")
    """
    ARGUMENTS_PARSER = MyFlaskParser()
