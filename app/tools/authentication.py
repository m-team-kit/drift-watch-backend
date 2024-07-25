"""Authentication module."""

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


def is_admin(user_infos):
    """Assert registration and entitlements."""
    if "eduperson_entitlement" in user_infos.user_info:
        entitlements = set(user_infos.user_info["eduperson_entitlement"])
    else:
        entitlements = set()
    return all(
        [
            (
                entitlements & set(current_app.config["ADMIN_ENTITLEMENTS"])
                or not current_app.config["ADMIN_ENTITLEMENTS"]
            )
        ]
    )


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


def authentication_doc(description):
    return {
        "description": f"{description}",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "description": "Error name",
                        },
                        "error_description": {
                            "type": "string",
                            "description": "Error message",
                        },
                    },
                }
            }
        },
    }


extra_responses = {
    "401": authentication_doc("Unauthorized"),
    "403": authentication_doc("Forbidden"),
}


class Authentication:
    def __init__(self, blueprint):
        """Initialize the authentication module."""
        self.blueprint = blueprint

    def access_level(self, level: str) -> Callable:
        """Decorator to check access level."""
        match level:
            case "everyone":
                return lambda f: f  # Return without modifications
            case "user" | "admin":
                auth_docs = {k: extra_responses[k] for k in ["401", "403"]}
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
