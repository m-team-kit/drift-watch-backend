"""Drift Monitoring Backend Application."""

from flask import Flask

from app import config
from app.tools import authentication
from app.tools import database
from app.tools import exceptions
from app.tools import openapi


def create_app(**kwds):
    """Create and configure an instance of the Flask application."""
    # Application instantiation and configuration
    settings = config.Settings(**kwds)  # type: ignore
    app = Flask(__name__)
    app.config.from_object(settings)
    # Server modules init
    authentication.init_app(app)
    database.init_app(app)
    exceptions.init_app(app)
    openapi.init_app(app)
    # Add empty response to root route
    app.add_url_rule("/", "empty_response", empty_response)
    # Return application object
    return app


def empty_response():
    """Add a ping route to the application."""
    return ("", 204)
