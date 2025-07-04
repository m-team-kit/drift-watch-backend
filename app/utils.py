"""Utilities for the application."""

from functools import reduce

from flask import abort, current_app

from app.tools import authentication


def get_user(user_infos):
    """Retrieve a user from the database from token information."""
    collection = current_app.config["db"]["app.users"]
    sub, iss = user_infos["sub"], user_infos["iss"]
    user = collection.find_one({"subject": sub, "issuer": iss})
    return user or abort(403, "User not registered.")


def get_experiment(experiment_id):
    """Retrieve an experiment from the database by its ID."""
    collection = current_app.config["db"]["app.experiments"]
    experiment = collection.find_one({"_id": experiment_id})
    return experiment or abort(404, "Experiment not found.")


def get_drifts(experiment_id, drift_id):
    """Retrieve a drift from the database by its ID."""
    collection = current_app.config["db"][f"app.{experiment_id}"]
    drift = collection.find_one({"_id": drift_id})
    return drift or abort(404, "Drift not found.")


def get_permission(resource, user_id, user_infos):
    """Check if the user has the required permission on a resource."""
    titles = authentication.get_entitlements(user_infos).union({user_id})
    permissions = resource.get("permissions", [])
    perms = set(p["level"] for p in permissions if p["entity"] in titles)
    if "Manage" in perms:  # Top level permission
        return "Manage"
    if "Edit" in perms:  # Second level permission
        return "Edit"
    if "Read" in perms:  # Third level permission
        return "Read"
    return None  # No permission found


def check_access(resource, user_id, user_infos, level="Read"):
    """Check if the user has the required permission on the resource."""
    if resource.get("public", False) and level == "Read":
        return True
    if not user_infos or not authentication.is_user(user_infos):
        return abort(403, "Resource is not public.")
    if authentication.is_admin(user_infos):
        return True
    match get_permission(resource, user_id, user_infos):
        case "Manage":
            return True
        case "Edit" if level in ["Read", "Edit"]:
            return True
        case "Read" if level == "Read":
            return True
    return abort(403, "Insufficient permissions.")


def pagination_header(page, page_size, total):
    """Generate the pagination header."""
    return {
        "total": total,
        "total_pages": (total + page_size - 1) // page_size,
        "first_page": 1 if total > 0 else 0,
        "last_page": (total + page_size - 1) // page_size,
        "page": page,
        "previous_page": page - 1 if page > 1 else 0,
        "next_page": page + 1 if page * page_size < total else None,
    }
