"""
Authentication and authorization module for the Drift Watch Backend.

This module provides JWT-based authentication and role-based authorization using
the FLAAT (FLAsk with Access And Authentication Tokens) library. It handles user
validation, permission checking, and access level enforcement across API endpoints.

The authentication system supports:
- JWT token validation and user info extraction
- Role-based access control with configurable entitlements  
- Multi-level access control (everyone, user, admin)
- Integration with OpenID Connect providers
- Flexible entitlement path configuration

Access Levels:
- everyone: No authentication required
- user: Valid token with user entitlements required
- admin: Valid token with admin entitlements required

The module uses entitlements (roles/groups) from JWT tokens to determine user
permissions and provides decorators for protecting API endpoints.
"""

from functools import reduce
from typing import Callable

from flaat.config import AccessLevel  # type: ignore
from flaat.flask import Flaat  # type: ignore
from flaat.requirements import IsTrue  # type: ignore
from flask import abort, current_app


def valid_user_infos(user_infos):
    """
    Validate that user information contains all required fields for authentication.
    
    Checks that the JWT token contains the essential user information fields
    needed for user identification and verification. This includes user identity,
    issuer information, and email verification status.
    
    Args:
        user_infos: User information object containing JWT token claims
        
    Returns:
        bool: True if all required fields are present and valid, False otherwise
        
    Required Fields:
        - sub: Subject identifier (unique user ID from identity provider)
        - iss: Issuer URL (identity provider that issued the token)  
        - email: User's email address
        - email_verified: Boolean indicating email verification status
        
    Validation Rules:
        - All fields must be present in the token
        - email_verified must be True for security
    """
    return all(
        [
            "sub" in user_infos.user_info,
            "iss" in user_infos.user_info,
            "email" in user_infos.user_info,
            "email_verified" in user_infos.user_info,
            user_infos["email_verified"],
        ]
    )


def get_entitlements(user_infos):
    """
    Extract user entitlements (roles/groups) from JWT token claims.
    
    Retrieves the user's roles or group memberships from the JWT token using
    a configurable path. Supports nested claim structures commonly used by
    OpenID Connect providers like Keycloak.
    
    Args:
        user_infos (dict): User information from JWT token
        
    Returns:
        set: Set of entitlement strings (roles/groups) the user belongs to
        
    Configuration:
        Uses ENTITLEMENTS_PATH from app config to locate entitlements in token.
        Default path: "realm_access/roles" (Keycloak format)
        
    Example:
        # For token with structure: {"realm_access": {"roles": ["user", "admin"]}}
        entitlements = get_entitlements(user_infos)  
        # Returns: {"user", "admin"}
    """
    entitlements_path = current_app.config["ENTITLEMENTS_PATH"]
    # split entitlements key by '/' if it is a path
    entitlements_path = entitlements_path.split("/")
    # reduce the path to get the entitlements
    entitlements = reduce(lambda d, k: d.get(k, []), entitlements_path, user_infos)
    return set(entitlements)


def is_user(user_infos):
    """
    Check if the authenticated user has basic user-level entitlements.
    
    Verifies that the user's entitlements include at least one of the configured
    user-level roles required for basic API access. This is the minimum access
    level for registered users.
    
    Args:
        user_infos (dict): User information from JWT token
        
    Returns:
        bool: True if user has required user entitlements, False otherwise
        
    Configuration:
        Uses USERS_ENTITLEMENTS from app config to define required user roles.
        Example: ["platform-access", "basic-user"]
        
    Access Control:
        Users must have at least one matching entitlement to access user-level endpoints.
    """
    entitlements = get_entitlements(user_infos)
    user_entitlements = set(current_app.config["USERS_ENTITLEMENTS"])
    return bool(entitlements & user_entitlements)


def is_admin(user_infos):
    """
    Check if the authenticated user has administrative privileges.
    
    Verifies that the user's entitlements include at least one of the configured
    admin-level roles required for administrative operations. Admin users have
    elevated privileges and can access all resources regardless of permissions.
    
    Args:
        user_infos (dict): User information from JWT token
        
    Returns:
        bool: True if user has admin entitlements, False otherwise
        
    Configuration:
        Uses ADMIN_ENTITLEMENTS from app config to define admin roles.
        Example: ["urn:mace:egi.eu:group:vo_example:role=admin#aai.egi.eu"]
        
    Access Control:
        Admin users bypass normal permission checks and have full system access.
    """
    entitlements = get_entitlements(user_infos)
    admin_entitlements = set(current_app.config["ADMIN_ENTITLEMENTS"])
    return bool(entitlements & admin_entitlements)


# Define access levels for the application
access_levels = [
    AccessLevel("user", IsTrue(valid_user_infos)),
    AccessLevel("admin", IsTrue(is_admin)),
]

# Initialize the Flaat module
flaat = Flaat(access_levels)


def init_app(app):
    """
    Initialize the authentication module for the Flask application.
    
    Configures the FLAAT authentication system with the Flask app instance,
    enabling JWT token processing and access level enforcement across the
    application.
    
    Args:
        app (Flask): The Flask application instance to configure
        
    Side Effects:
        - Sets app.config['flaat'] to the FLAAT instance
        - Initializes FLAAT with the app for request processing
        - Enables authentication decorators and token validation
    """
    app.config["flaat"] = flaat
    app.config["flaat"].init_app(app)


UNAUTHORIZED = {
    "description": "Unauthorized",
    "content": {
        "application/json": {
            "schema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "integer",
                        "description": "HTTP status code",
                    },
                    "status": {
                        "type": "string",
                        "description": "HTTP status message",
                    },
                    "message": {
                        "type": "string",
                        "description": "Error message",
                    },
                },
            }
        }
    },
}


FORBIDDEN = {
    "description": "Forbidden",
    "content": {
        "application/json": {
            "schema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "integer",
                        "description": "HTTP status code",
                    },
                    "status": {
                        "type": "string",
                        "description": "HTTP status message",
                    },
                    "message": {
                        "type": "string",
                        "description": "Error message",
                    },
                },
            }
        }
    },
}


class Authentication:
    """
    Authentication decorator class for protecting API endpoints.
    
    Provides decorators for enforcing access levels on Flask-SMOREST API endpoints.
    Integrates with FLAAT for JWT token validation and adds appropriate OpenAPI
    documentation for authentication requirements.
    
    The class supports three access levels:
    - everyone: No authentication required  
    - user: Valid JWT token with user entitlements required
    - admin: Valid JWT token with admin entitlements required
    
    Features:
    - Automatic OpenAPI documentation generation for auth requirements
    - Consistent error handling with proper HTTP status codes
    - Integration with Flask-SMOREST for API documentation
    """

    def __init__(self, blueprint):
        """
        Initialize the authentication module for a specific blueprint.
        
        Args:
            blueprint: Flask-SMOREST blueprint instance to apply authentication to
        """
        self.blueprint = blueprint

    def access_level(self, level: str) -> Callable:
        """
        Decorator factory for enforcing access levels on API endpoints.
        
        Creates a decorator that enforces the specified access level and adds
        appropriate OpenAPI documentation for authentication requirements.
        
        Args:
            level (str): Required access level:
                - "everyone": No authentication required
                - "user": User-level authentication required  
                - "admin": Admin-level authentication required
                
        Returns:
            Callable: Decorator function to apply to API endpoint methods
            
        Behavior:
            - "everyone": Returns function unchanged (no auth required)
            - "user"/"admin": Applies FLAAT authentication with error handling
            - Automatically adds 401/403 responses to OpenAPI documentation
            
        Example:
            @auth.access_level("user")
            def protected_endpoint(self):
                return {"message": "User authenticated successfully"}
        """
        match level:
            case "everyone":
                return lambda f: f  # Return without modifications
            case "user" | "admin":
                auth_docs = {"401": UNAUTHORIZED, "403": FORBIDDEN}
        auth_decorator = flaat.access_level(
            access_level_name=level,
            on_failure=self.raise_correct_error,
        )
        doc_decorator = self.blueprint.doc(responses=auth_docs)
        return lambda f: doc_decorator(auth_decorator(f))

    inject_user_infos = flaat.inject_user_infos

    def raise_correct_error(self, error, user_infos=None):
        """
        Handle authentication failures with appropriate HTTP error responses.
        
        Converts FLAAT authentication errors into Flask HTTP exceptions with
        proper status codes and error messages.
        
        Args:
            error: FLAAT error object containing status code and message
            user_infos: User information (unused, for FLAAT compatibility)
            
        Raises:
            HTTPException: Flask abort with appropriate status code and message
        """
        abort(error.status_code, error.args[0])
