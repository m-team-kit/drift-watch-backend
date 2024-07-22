"""Authentication module."""

from typing import Callable
from flaat.config import AccessLevel  # type: ignore
from flaat.flask import Flaat  # type: ignore
from flaat.requirements import IsTrue  # type: ignore
from flask import current_app, request


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


def is_registered(user_infos):
    """Assert user is registered in the database."""
    users = current_app.config["db"]["app.blueprints.user"]
    return users.find_one(
        {
            "subject": user_infos.subject,
            "issuer": user_infos.issuer,
        }
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


# TODO: Add permissions "Manage", "Edit", "Read" to the application
# Define access levels for the application
access_levels = [
    # AccessLevel("everyone", IsTrue(lambda x: True)),
    AccessLevel("new_user", IsTrue(valid_user_infos)),
    AccessLevel("registered", IsTrue(is_registered)),
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
            case "new_user":
                auth_docs = {k: extra_responses[k] for k in ["401"]}
            case "registered" | "admin":
                auth_docs = {k: extra_responses[k] for k in ["401", "403"]}
        auth_decorator = flaat.access_level(level)
        doc_decorator = self.blueprint.doc(responses=auth_docs)
        return lambda f: doc_decorator(auth_decorator(f))

    inject_user_infos = flaat.inject_user_infos
