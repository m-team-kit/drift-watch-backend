"""Dfit Monitoring Backend Application."""

from app import config
from app.tools import authentication as auth
from app.tools import database as db
from app.tools import openapi as api
from flask import Flask


def create_app(**kwds):
    """Create and configure an instance of the Flask application."""
    # Application instantiation and configuration
    settings = config.Settings(**kwds)  # type: ignore
    app = Flask(__name__)
    app.config.from_object(settings)
    # Server modules init
    auth.init_app(app)
    db.init_app(app)
    api.init_app(app)
    # Add empty response to root route
    app.add_url_rule("/", "empty_response", empty_response)
    # Return application object
    return app


def empty_response():
    """Add a ping route to the application."""
    return ("", 204)
