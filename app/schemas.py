""""This module contains the schema for the API request and response."""

import marshmallow as ma
from marshmallow import validate


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
    _id = ma.fields.UUID(dump_only=True, data_key="id")
    schema_version = ma.fields.Constant("1.0.0")
    datetime = ma.fields.String(dump_only=True)
    job_status = ma.fields.String(required=True, validate=status)
    model = ma.fields.String()
    concept_drift = ma.fields.Nested(BaseDrift, load_default=no_drift)
    data_drift = ma.fields.Nested(BaseDrift, load_default=no_drift)


class User(ma.Schema):
    _id = ma.fields.UUID(dump_only=True, data_key="id")
    created_at = ma.fields.String(dump_only=True)
    subject = ma.fields.String(dump_only=True)
    issuer = ma.fields.String(dump_only=True)
    email = ma.fields.Email(dump_only=True)
    drift_ids = ma.fields.List(ma.fields.UUID(), dump_only=True)
