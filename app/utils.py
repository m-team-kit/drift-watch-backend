"""Utilities for the application."""

from flask import abort, current_app


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
    entitlements_key = current_app.config["ENTITLEMENTS_FIELD"]
    titles = user_infos.get(entitlements_key, []) + [user_id]
    perms = set(r for k, r in resource["permissions"].items() if k in titles)
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
    match get_permission(resource, user_id, user_infos):
        case "Manage":
            return True
        case "Edit" if level in ["Read", "Edit"]:
            return True
        case "Read" if level == "Read":
            return True
    return abort(403, "Insufficient permissions.")
