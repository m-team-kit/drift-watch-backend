"""
## API Methods to list, register, edit and remove experiments.
"""

import uuid
from datetime import datetime as dt

import marshmallow as ma
from flask import abort, current_app
from flask.views import MethodView

from app import schemas, utils
from app.config import Blueprint
from app.tools.authentication import Authentication
from app.tools.database import NOT_FOUND

blp = Blueprint("drift", __name__, description=__doc__)
auth = Authentication(blueprint=blp)


@blp.route("")
class Experiments(MethodView):
    """Experiments API."""

    @auth.access_level("everyone")
    @blp.arguments(ma.Schema(), location="json", unknown="include")
    @blp.response(200, schemas.Experiment(many=True))
    @blp.paginate()
    def get(self, json, pagination_parameters):
        """
        Get a paginated list of experiments based on the provided JSON query
        and MongoDB format.
        ---
        Internal comment not meant to be exposed.

        Args:
            json: A JSON object representing the query parameters.
            pagination_parameters: An object containing pagination parameters.

        Returns:
            A paginated list of experiments matching the query.

        Raises:
            422: If the JSON query is not in the correct format.
        """
        # Search for experiments based on the provided JSON query.
        experiments = current_app.config["db"]["app.experiments"]
        search = experiments.find(json)

        # Return the paginated list of experiments.
        page = pagination_parameters.page
        page_size = pagination_parameters.page_size
        return search.skip((page - 1) * page_size).limit(page_size)

    @auth.access_level("user")
    @auth.inject_user_infos()
    @blp.arguments(schemas.Experiment, location="json", unknown="raise")
    @blp.response(201, schemas.Experiment)
    def post(self, json, user_infos):
        """Create a new experiment record in the database.
        ---
        Internal comment not meant to be exposed.

        Args:
            json (dict): The JSON payload containing the experiment information.
            user_infos (dict): User information obtained from the
            authentication token.

        Returns:
            The newly created experiment record.

        Raises:
            401: If the user is not authenticated or registered.
            409: If the a experiment with the same name already exists.
            422: If the JSON query is not in the correct format.
        """
        # Check if the user is registered and retrieve the user object.
        user = utils.get_user(user_infos)

        # Modify the JSON object to include the user ID and permissions.
        json["created_at"] = dt.now().isoformat()
        json["_id"] = str(uuid.uuid4())
        json["permissions"][user["_id"]] = "Manage"

        # Insert it into the database.
        experiments = current_app.config["db"]["app.experiments"]
        if experiments.find_one({"name": json["name"]}):
            abort(409, "Name conflict.")
        experiments.insert_one(json)

        # Return the updated user object.
        return json


@blp.route("/<uuid:experiment_id>")
class Experiment(MethodView):
    """Experiment API."""

    @auth.access_level("everyone")
    @blp.doc(responses={"404": NOT_FOUND})
    @blp.response(200, schemas.Experiment)
    def get(self, experiment_id):
        """Retrieve an experiment by its ID from the database.
        ---
        Internal comment not meant to be exposed.

        Args:
            experiment_id (str): The ID of the experiment to retrieve.

        Returns:
            dict: The experiment object.

        Raises:
            404: If the experiment with the specified ID is not found.
        """
        experiment_id = str(experiment_id)
        return utils.get_experiment(experiment_id)

    @auth.access_level("user")
    @auth.inject_user_infos()
    @blp.arguments(schemas.Experiment, location="json", unknown="raise")
    @blp.doc(responses={"404": NOT_FOUND})
    @blp.response(200, schemas.Experiment)
    def put(self, json, experiment_id, user_infos):
        """
        Update a experiment record with the given JSON data.
        ---
        Internal comment not meant to be exposed.

        Args:
            json (dict): The JSON data containing the updated drift information.
            experiment_id (str): The ID of the experiment to retrieve drifts from.
            user_infos (dict): User information from the authentication token.

        Returns:
            dict: The updated experiment record.

        Raises:
            401: If the user is not authenticated or registered.
            403: If the user does not have the required permissions.
            404: If the drift or experiment specified are not found.
            422: If the JSON query is not in the correct format.
        """
        # Check if the user is registered and validate access level.
        user = utils.get_user(user_infos)
        experiment_id = str(experiment_id)
        experiment = utils.get_experiment(experiment_id)
        utils.check_access(user, experiment, level="Manage")

        # Modify the JSON object to include the user ID and permissions.
        experiment.update(json)
        json["permissions"][user["_id"]] = "Manage"

        # Replace the drift record in the database.
        experiments = current_app.config["db"]["app.experiments"]
        experiments.replace_one({"_id": experiment_id}, experiment)

        # Return the updated drift record.
        return experiment

    @auth.access_level("user")
    @auth.inject_user_infos()
    @blp.doc(responses={"404": NOT_FOUND})
    @blp.response(204)
    def delete(self, experiment_id, user_infos):
        """
        Delete a experiment record from the database.
        ---
        Internal comment not meant to be exposed.

        Args:
            json (dict): The JSON data containing the updated drift information.
            experiment_id (str): The ID of the experiment to retrieve drifts from.
            user_infos (dict): User information from the authentication token.

        Returns:
            dict: The updated experiment record.

        Raises:
            401: If the user is not authenticated or registered.
            403: If the user does not have the required permissions.
            404: If the drift or experiment specified are not found.
        """
        # Check if the user is registered and validate access level.
        user = utils.get_user(user_infos)
        experiment_id = str(experiment_id)
        experiment = utils.get_experiment(experiment_id)
        utils.check_access(user, experiment, level="Manage")

        # Replace the drift record in the database.
        experiments = current_app.config["db"]["app.experiments"]
        experiments.delete_one({"_id": experiment_id})

        # Return empty response.
        return None


@blp.route("/<uuid:experiment_id>/drift")
class Drifts(MethodView):
    """Drifts API."""

    @auth.access_level("user")
    @auth.inject_user_infos()
    @blp.arguments(ma.Schema(), location="json", unknown="include")
    @blp.response(200, schemas.DriftV100(many=True))
    @blp.paginate()
    def get(self, json, experiment_id, user_infos, pagination_parameters):
        """
        Get a paginated list of drift Jobs based on the provided JSON query
        and MongoDB format.
        ---
        Internal comment not meant to be exposed.

        Args:
            json: A JSON object representing the query parameters.
            experiment_id: The ID of the experiment to retrieve drifts from.
            user_infos: User information obtained from the authentication process.
            pagination_parameters: An object containing pagination parameters.

        Returns:
            A paginated list of drifts matching the query.

        Raises:
            401: If the user is not authenticated or registered.
            403: If the user does not have the required permissions.
            404: If the experiment with the specified ID is not found.
            422: If the JSON query is not in the correct format.
        """
        # Check if the user is registered and validate access level.
        user = utils.get_user(user_infos)
        experiment_id = str(experiment_id)
        experiment = utils.get_experiment(experiment_id)
        utils.check_access(user, experiment, level="Read")

        # Search for drifts based on the provided JSON query.
        drifts = current_app.config["db"][f"app.{experiment_id}"]
        search = drifts.find(json)

        # Return the paginated list of drifts.
        page = pagination_parameters.page
        page_size = pagination_parameters.page_size
        return search.skip((page - 1) * page_size).limit(page_size)

    @auth.access_level("user")
    @auth.inject_user_infos()
    @blp.arguments(schemas.DriftV100, location="json", unknown="raise")
    @blp.response(201, schemas.DriftV100)
    def post(self, json, experiment_id, user_infos):
        """Create a new drift Job record in the database.
        ---
        Internal comment not meant to be exposed.

        Args:
            json (dict): The JSON payload containing the drift information.
            user_infos (dict): User information obtained from the
                               authentication process.

        Returns:
            dict: The newly created drift record.

        Raises:
            401: If the user is not authenticated or registered.
            403: If the user does not have the required permissions.
            404: If the experiment with the specified ID is not found.
            422: If the JSON query is not in the correct format.
        """
        # Check if the user is registered and validate access level.
        user = utils.get_user(user_infos)
        experiment_id = str(experiment_id)
        experiment = utils.get_experiment(experiment_id)
        utils.check_access(user, experiment, level="Edit")

        # Insert the drift record into the database.
        drifts = current_app.config["db"][f"app.{experiment_id}"]
        json["created_at"] = dt.now().isoformat()
        json["_id"] = str(uuid.uuid4())
        drifts.insert_one(json)

        # Return the updated drift object.
        return json


@blp.route("/<uuid:experiment_id>/drift/<uuid:drift_id>")
class Drift(MethodView):
    """Drift API."""

    @auth.access_level("user")
    @auth.inject_user_infos()
    @blp.doc(responses={"404": NOT_FOUND})
    @blp.response(200, schemas.DriftV100)
    def get(self, experiment_id, drift_id, user_infos):
        # def get(self, experiment_id, drift_id, user_infos):
        """Retrieve a drift job by its id from the database.
        ---
        Internal comment not meant to be exposed.

        Args:
            experiment_id (str): ID of the experiment to retrieve drifts from.
            drift_id (str): The ID of the drift to retrieve.
            user_infos (dict): User information from the authentication token.

        Returns:
            dict: The drift object.

        Raises:
            401: If the user is not authenticated or registered.
            403: If the user does not have the required permissions.
            404: If the drift or experiment specified are not found.
            422: If the JSON query is not in the correct format.
        """
        # Check if the user is registered and validate access level.
        user = utils.get_user(user_infos)
        experiment_id = str(experiment_id)
        experiment = utils.get_experiment(experiment_id)
        utils.check_access(user, experiment, level="Edit")

        # Retrieve and return the drift object from the database.
        drift_id = str(drift_id)
        return utils.get_drifts(experiment_id, drift_id)

    @auth.access_level("user")
    @auth.inject_user_infos()
    @blp.arguments(schemas.DriftV100, location="json", unknown="raise")
    @blp.doc(responses={"404": NOT_FOUND})
    @blp.response(200, schemas.DriftV100)
    def put(self, json, experiment_id, drift_id, user_infos):
        """
        Update a drift job record with the given JSON data.
        ---
        Internal comment not meant to be exposed.

        Args:
            json (dict): The JSON data containing the updated drift information.
            experiment_id (str): The ID of the experiment to retrieve drifts from.
            drift_id (str): The ID of the drift record to be updated.
            user_infos (dict): User information from the authentication token.

        Returns:
            dict: The updated drift record.

        Raises:
            401: If the user is not authenticated or registered.
            403: If the user does not have the required permissions.
            404: If the drift or experiment specified are not found.
        """
        # Check if the user is registered and validate access level.
        user = utils.get_user(user_infos)
        experiment_id = str(experiment_id)
        experiment = utils.get_experiment(experiment_id)
        utils.check_access(user, experiment, level="Edit")

        # Collect the drift record from the database and update it.
        drift_id = str(drift_id)
        drift = utils.get_drifts(experiment_id, drift_id)
        drift.update(json)

        # Replace the drift record in the database.
        drifts = current_app.config["db"][f"app.{experiment_id}"]
        drifts.replace_one({"_id": str(drift_id)}, drift)

        # Return the updated drift record.
        return drift

    @auth.access_level("user")
    @auth.inject_user_infos()
    @blp.doc(responses={"404": NOT_FOUND})
    @blp.response(204)
    def delete(self, experiment_id, drift_id, user_infos):
        """
        Delete a drift job record from the database.
        ---
        Internal comment not meant to be exposed.

        Args:
            experiment_id (str): The ID of the experiment to retrieve drifts from.
            drift_id (str): The ID of the drift record to be deleted.
            user_infos (dict): User information from the authentication token.

        Returns:
            None

        Raises:
            401: If the user is not authenticated or registered.
            403: If the user does not have the required permissions.
            404: If the drift specified is not found.
        """
        # Check if the user is registered and validate access level.
        user = utils.get_user(user_infos)
        experiment_id = str(experiment_id)
        experiment = utils.get_experiment(experiment_id)
        utils.check_access(user, experiment, level="Edit")

        # Collect the drift record from the database.
        drift_id = str(drift_id)
        _drift = utils.get_drifts(experiment_id, drift_id)

        # Delete the drift record from the database.
        drifts = current_app.config["db"][f"app.{experiment_id}"]
        drifts.delete_one({"_id": drift_id})
