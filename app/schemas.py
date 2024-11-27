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


class Permission(ma.fields.Dict):
    """
    Permissions is a dictionary of group_id and role.
    """

    options = validate.OneOf(["Read", "Edit", "Manage"])

    def __init__(self, **kwds):
        super().__init__(
            keys=ma.fields.String(required=True, validate=self.options),
            values=ma.fields.String(required=True),
            validate=validate.Length(max=1),  # Do not group
            load_default={},
            **kwds,
        )


class Entitlements(ma.Schema):
    """
    Entitlement is a string of the form "vo#role".
    """

    items = ma.fields.List(ma.fields.String(), required=True)


class Experiment(BaseSchema):
    """
    Experiment is a pointer to the collection of drifts.
    Authentication is carried by the groups that point here.
    A name is required for easy identification.
    Includes the list of permissions for the groups.
    """

    name = ma.fields.String(required=True)
    description = ma.fields.String()
    public = ma.fields.Boolean(load_default=False)
    permissions = ma.fields.List(Permission(), load_default=[])


class User(BaseSchema):
    """
    User represent a person that access and uses the API.
    User's ids can also be used as group_ids.
    """

    subject = ma.fields.String(dump_only=True)
    issuer = ma.fields.String(dump_only=True)
    email = ma.fields.Email(dump_only=True)


class UsersEmails(ma.Schema):
    """Schema for a list of emails."""

    emails = ma.fields.List(
        ma.fields.Email(),
        required=True,
        validate=validate.Length(min=1, max=10),
    )


class UsersIds(ma.Schema):
    """Schema for a list of ids."""

    ids = ma.fields.List(
        ma.fields.UUID(),
        required=True,
        validate=validate.Length(min=1, max=10),
    )


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
    model = ma.fields.String(required=True)
    concept_drift = ma.fields.Nested(BaseDrift, load_default=no_drift)
    data_drift = ma.fields.Nested(BaseDrift, load_default=no_drift)
