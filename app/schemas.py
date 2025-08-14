"""
API request and response schema definitions using Marshmallow.

This module defines all the data schemas used for API request validation and
response serialization. The schemas provide type safety, validation rules,
and automatic OpenAPI documentation generation for all API endpoints.

Schema Categories:

Base Schemas:
- _BaseReqSchema: Common fields for request schemas
- _BaseRespSchema: Common fields for response schemas (ID, timestamps)

User Management:
- User: User profile information
- UsersEmails/UsersIds: Bulk user operations
- SearchUsers: User search and sorting parameters

Experiment Management:  
- Experiment: Complete experiment metadata
- CreateExperiment: Experiment creation request
- Permission: Access control permissions
- SortExperiments: Experiment search and sorting

Drift Detection:
- Drift: Complete drift record with metadata
- CreateDrift: Drift creation request  
- SortDrifts: Drift search and sorting parameters

Entitlements:
- Entitlements: User role and permission information

The schemas use Marshmallow for validation and serialization, providing:
- Type validation and coercion
- Field-level validation rules  
- Custom error messages
- Automatic OpenAPI schema generation
- Request/response data transformation
"""

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


class SearchUsers(ma.Schema):
    """Schema for searching users."""

    sort_by = ma.fields.String(
        load_default="created_at",
        validate=validate.OneOf(["created_at", "email", "subject", "issuer"]),
    )
    order_by = ma.fields.String(
        load_default="desc",
        validate=validate.OneOf(["asc", "desc"]),
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


class SortDrifts(ma.Schema):
    """Schema for sorting drift detection instances."""

    sort_by = ma.fields.String(
        load_default="created_at",
        validate=validate.OneOf(
            ["created_at", "job_status", "model", "drift_detected", "schema_version"],
        ),
    )
    order_by = ma.fields.String(
        load_default="desc",
        validate=validate.OneOf(["asc", "desc"]),
    )
