""""This module contains the schema for the API request and response."""

import marshmallow as ma
from marshmallow import validate


class BaseSchema(ma.Schema):
    """
    BaseSchema is the base class for all schemas.
    It includes the _id and created_at fields.
    """

    _id = ma.fields.UUID(dump_only=True, data_key="id")
    created_at = ma.fields.String(dump_only=True)


class Experiment(BaseSchema):
    """
    Experiment is a pointer to the collection of drifts.
    Authentication is carried by the groups that point here.
    A name is required for easy identification.
    Includes the list of permissions for the groups.
    """

    name = ma.fields.String(required=True)
    permissions = ma.fields.List(
        ma.fields.Nested("Permission"),
        validate=validate.Length(min=1),
        load_default=[],
    )


class Permission(ma.Schema):
    """
    Permission is a pointer from a group.
    Should not point to the resource but be included in the resource.
    It indicates the authorization role of the group.
    """

    group_id = ma.fields.UUID(required=True)
    role = ma.fields.String(
        validate=validate.OneOf(["Read", "Edit", "Manage"]),
        required=True,
    )

    @ma.post_load
    def members_str(self, data, **kwds):
        """Convert group_id uuid to string."""
        data["group_id"] = str(data["group_id"])
        return data


class Group(BaseSchema):
    """
    Group is a list of users that can access the API.
    A name is required for easy identification.
    """

    name = ma.fields.String(required=True)
    members = ma.fields.List(ma.fields.UUID, required=True)

    @ma.post_load
    def members_str(self, data, **kwds):
        """Convert members uuid to string."""
        data["members"] = [str(member) for member in data["members"]]
        return data


class User(BaseSchema):
    """
    User represent a person that access and uses the API.
    User's ids can also be used as group_ids.
    """

    subject = ma.fields.String(dump_only=True)
    issuer = ma.fields.String(dump_only=True)
    email = ma.fields.Email(dump_only=True)


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


class DriftV100(BaseSchema):
    """
    A drift is the basic unit of the API. It contains the drift
    information for a specific model and job.
    """

    schema_version = ma.fields.Constant("1.0.0")
    job_status = ma.fields.String(required=True, validate=status)
    model = ma.fields.String()
    concept_drift = ma.fields.Nested(BaseDrift, load_default=no_drift)
    data_drift = ma.fields.Nested(BaseDrift, load_default=no_drift)
