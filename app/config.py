"""Configuration settings for the application."""

# https://docs.pydantic.dev/latest/concepts/pydantic_settings/
import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from webargs.flaskparser import FlaskParser
from marshmallow import INCLUDE, RAISE
import flask_smorest


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        secrets_dir=os.environ["APP_SECRETS_DIR"],
        env_prefix="APP_",
        case_sensitive=False,
    )

    API_TITLE: str = "Drift Detection Monitor API"
    API_VERSION: str = "1.0.0"
    API_SPEC_OPTIONS: dict = {}
    TESTING: bool = False

    OPENAPI_JSON_PATH: str = "specification.json"
    OPENAPI_URL_PREFIX: str = "/"

    ENTITLEMENTS_FIELD: str = "eduperson_entitlement"
    ADMIN_ENTITLEMENTS: list[str]
    TRUSTED_OP_LIST: list[str]

    DATABASE_NAME: str = "drifts-data"
    DATABASE_PORT: int = 27017
    DATABASE_HOST: str
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str


class MyFlaskParser(FlaskParser):
    DEFAULT_UNKNOWN_BY_LOCATION = {
        "query": INCLUDE,  # Manual raise 400 on unknown query parameters
        "json": RAISE,  # Raise 422 if json has unknown fields
        # ...
    }


class Blueprint(flask_smorest.Blueprint):
    ARGUMENTS_PARSER = MyFlaskParser()
