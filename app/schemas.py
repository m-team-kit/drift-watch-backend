""""This module contains the schema for the API request and response."""

import marshmallow as ma
from marshmallow import validate


class Experiment(ma.Schema):
    """
    Experiment is a pointer to the collection of drifts.
    Authentication is carried by the groups that point here.
    A name is required for easy identification.
    """

    _id = ma.fields.UUID(dump_only=True, data_key="id")
    created_at = ma.fields.String(dump_only=True)
    name = ma.fields.String(required=True)


class Permission(ma.Schema):
    """
    Permission is a pointer from a group to the experiment.
    It indicates the authorization level of the group.
    """

    _id = ma.fields.UUID(dump_only=True, data_key="id")
    group_id = ma.fields.UUID(required=True)
    experiment_id = ma.fields.UUID(required=True)
    permission = ma.fields.String(one_of=["Read", "Edit"])


class Group(ma.Schema):
    """
    Group is a list of pointers to the experiments indicating
    the authorization level. Every user has at least an owned
    group for experiments they does not want to share.
    """

    _id = ma.fields.UUID(dump_only=True, data_key="id")
    created_at = ma.fields.String(dump_only=True)
    name = ma.fields.String(required=True)
    # experiments = ma.fields.List(Permission, dump_only=True)
    experiments = Permission(many=True)  # Check if it is correct


class User(ma.Schema):
    """
    User represent a person that access and uses the API.
    An user can be part of many groups.
    An user always has an owned group for experiments.
    """

    _id = ma.fields.UUID(dump_only=True, data_key="id")
    created_at = ma.fields.String(dump_only=True)
    subject = ma.fields.String(dump_only=True)
    issuer = ma.fields.String(dump_only=True)
    email = ma.fields.Email(dump_only=True)
    drift_ids = ma.fields.List(Group)
    drift_ids = Group(many=True)


class BaseDrift(ma.Schema):
    drift = ma.fields.Bool(required=True)
    parameters = ma.fields.Dict()

    @ma.validates_schema
    def if_drift_then_parameters(self, data, **kwds):
        if data["drift"]:
            if "parameters" not in data or not data["parameters"]:
                raise ma.ValidationError("Include parameters if drift.")


status = validate.OneOf(["Running", "Completed", "Failed"])
no_drift = {"drift": False, "parameters": {}}


class DriftV100(ma.Schema):
    """
    A drift is the basic unit of the API. It contains the drift
    information for a specific model and job.
    """

    _id = ma.fields.UUID(dump_only=True, data_key="id")
    schema_version = ma.fields.Constant("1.0.0")
    datetime = ma.fields.String(dump_only=True)
    job_status = ma.fields.String(required=True, validate=status)
    model = ma.fields.String()
    concept_drift = ma.fields.Nested(BaseDrift, load_default=no_drift)
    data_drift = ma.fields.Nested(BaseDrift, load_default=no_drift)
