"""Utilities for the application."""

from flask import current_app
from flask_smorest import abort


def get_user(user_infos):
    """Retrieve a user from the database from token information."""
    collection = current_app.config["db"]["app.users"]
    sub, iss = user_infos["sub"], user_infos["iss"]
    user = collection.find_one({"subject": sub, "issuer": iss})
    return user or abort(401, msg="User not registered.")


def get_experiment(experiment_id):
    """Retrieve an experiment from the database by its ID."""
    collection = current_app.config["db"]["app.experiments"]
    experiment = collection.find_one({"_id": experiment_id})
    return experiment or abort(404, msg="Experiment not found.")


def get_groups(user):
    """Retrieve the groups a user belongs to."""
    collection = current_app.config["db"]["app.groups"]
    groups = collection.find({"members": {"$in": user["_id"]}})
    return set([group["_id"] for group in groups] + [user["_id"]])


def get_drifts(experiment_id, drift_id):
    """Retrieve a drift from the database by its ID."""
    collection = current_app.config["db"][f"app.{experiment_id}"]
    drift = collection.find_one({"_id": drift_id})
    return drift or abort(404, msg="Drift not found.")


def get_permission(user, resource):
    """Check if the user has the required permission on a resource."""
    groups = get_groups(user)
    perms = [p["level"] for p in resource["permissions"] if p["group_id"] in groups]
    if "Manage" in perms:  # Top level permission
        return "Manage"
    if "Edit" in perms:  # Second level permission
        return "Edit"
    if "Read" in perms:  # Third level permission
        return "Read"
    return None  # No permission found


def check_access(user, resource, level="Read"):
    """Check if the user has the required permission on the resource."""
    match get_permission(user, resource):
        case "Manage":
            return True
        case "Edit" if level in ["Read", "Edit"]:
            return True
        case "Read" if level == "Read":
            return True
    return abort(403, msg="Insufficient permissions.")
