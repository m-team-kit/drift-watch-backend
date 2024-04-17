"""API Description, edit at backend>app>__init__.py.
# TODO: Use description in Swagger documentation (__doc__)
# TODO: Fix description
"""

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
    # Return application object
    return app
