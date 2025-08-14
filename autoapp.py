"""
Application entry point for the Drift Watch Backend.

This module serves as the main entry point for the Flask application,
creating and configuring the app instance that can be used by WSGI servers
like Gunicorn or for development purposes.

The app instance created here is configured with all necessary components:
- Authentication and authorization
- Database connections
- API blueprints and routes
- Error handling

Usage:
    This file is typically used by WSGI servers:
    gunicorn autoapp:app

    Or can be imported for programmatic access:
    from autoapp import app

TODO: DB auto-migration goes here
TODO: Other auto-action goes here
"""

from app import create_app

# Create the Flask application instance
app = create_app()
