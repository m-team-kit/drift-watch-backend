"""Authentication module."""

from functools import reduce
from typing import Callable

from flaat.config import AccessLevel  # type: ignore
from flaat.flask import Flaat  # type: ignore
from flaat.requirements import IsTrue  # type: ignore
from flask import abort, current_app


def valid_user_infos(user_infos):
    """Assert user_infos contains valid information."""
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
    """Retrieve the entitlements from user information."""
    entitlements_path = current_app.config["ENTITLEMENTS_PATH"]
    # split entitlements key by '/' if it is a path
    entitlements_path = entitlements_path.split("/")
    # reduce the path to get the entitlements
    entitlements = reduce(lambda d, k: d.get(k, []), entitlements_path, user_infos)
    return set(entitlements)


def is_user(user_infos):
    """Assert user is registered."""
    entitlements = get_entitlements(user_infos)
    user_entitlements = set(current_app.config["USERS_ENTITLEMENTS"])
    return bool(entitlements & user_entitlements)


def is_admin(user_infos):
    """Assert registration and entitlements."""
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
    """Initialize the authentication module."""
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
    """Authentication class for the application."""

    def __init__(self, blueprint):
        """Initialize the authentication module."""
        self.blueprint = blueprint

    def access_level(self, level: str) -> Callable:
        """Decorator to check access level."""
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
        """Raises the correct flask error."""
        abort(error.status_code, error.args[0])
