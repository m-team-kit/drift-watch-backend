""" "This module contains the schema for the API request and response."""

import marshmallow as ma
from marshmallow import validate


class _BaseReqSchema(ma.Schema):
    pass


class _BaseRespSchema(ma.Schema):
    _id = ma.fields.UUID(required=True, data_key="id", dump_only=True)
    created_at = ma.fields.String(required=True, dump_only=True)


class Entitlements(ma.Schema):
    """
    Entitlement is a string of the form "vo#role".
    """

    items = ma.fields.List(ma.fields.String(), required=True)


level_options = validate.OneOf(["Read", "Edit", "Manage"])


class Permission(ma.Schema):
    """
    Permissions defines the entity and the access level.
    """

    class Meta:  # pylint: disable=R0903, C0115
        unknown = ma.RAISE

    entity = ma.fields.String(required=True)
    level = ma.fields.String(required=True, validate=level_options)


class _BaseExperiment(ma.Schema):
    name = ma.fields.String(required=True)
    description = ma.fields.String()
    public = ma.fields.Boolean(load_default=False)
    permissions = ma.fields.List(
        ma.fields.Nested(Permission),
        load_default=[],
    )


class Experiment(_BaseExperiment, _BaseRespSchema):
    """
    Experiment is a pointer to the collection of drifts.
    Authentication is carried by the groups that point here.
    A name is required for easy identification.
    Includes the list of permissions for the groups.
    """


class CreateExperiment(_BaseExperiment, _BaseReqSchema):
    """Create Experiment Schema."""


class SortExperiments(ma.Schema):
    """Schema for sorting experiments."""

    sort_by = ma.fields.String(
        load_default="created_at",
        validate=validate.OneOf(["created_at", "name", "public"]),
    )
    order_by = ma.fields.String(
        load_default="desc",
        validate=validate.OneOf(["asc", "desc"]),
    )


class User(_BaseRespSchema):
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
    """Base drift schema"""

    drift = ma.fields.Bool(required=True)
    parameters = ma.fields.Dict()


tag = ma.fields.String(validate=validate.Length(min=1, max=20))
status_options = validate.OneOf(["Running", "Completed", "Failed"])


class _BaseDriftJob(ma.Schema):
    job_status = ma.fields.String(required=True, validate=status_options)
    tags = ma.fields.List(tag, load_default=[])
    model = ma.fields.String(required=True)
    drift_detected = ma.fields.Bool(required=True)
    parameters = ma.fields.Dict(load_default={})


class Drift(_BaseDriftJob, _BaseRespSchema):
    """
    Response Job Schema. A drift is the basic unit of the API.
    It contains the drift information for a specific model and job.
    """

    schema_version = ma.fields.String(required=True, dump_only=True)


class CreateDrift(_BaseDriftJob, _BaseReqSchema):
    """Create Job Schema for job."""
