"""
Exception handling module for the Drift Watch Backend.

This module provides centralized error handling for the Flask application,
converting HTTP exceptions into consistent JSON error responses that follow
a standard format across all API endpoints.

The error handler formats all HTTP exceptions into JSON responses with:
- code: HTTP status code
- status: HTTP status name
- message: Error description

Supported HTTP exceptions:
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 404 Not Found: Resource not found
- 409 Conflict: Resource conflict (e.g., duplicate names)
"""

import json

from werkzeug import exceptions


def init_app(app):
    """
    Initialize the exceptions module with the Flask application.

    Registers error handlers for common HTTP exceptions to provide
    consistent JSON error responses across all API endpoints.

    Args:
        app (Flask): The Flask application instance to configure.
    """
    app.errorhandler(exceptions.Unauthorized)(error_handler)
    app.errorhandler(exceptions.Forbidden)(error_handler)
    app.errorhandler(exceptions.NotFound)(error_handler)
    app.errorhandler(exceptions.Conflict)(error_handler)


def error_handler(error):
    """
    Return a JSON response for a given HTTP error.

    Converts Werkzeug HTTP exceptions into consistent JSON error responses
    that include the error code, status name, and descriptive message.

    Args:
        error (HTTPException): The Werkzeug HTTP exception to handle.

    Returns:
        Response: Flask response object with JSON error data and appropriate
                 HTTP status code.

    Example:
        For a 404 error, returns:
        {
            "code": 404,
            "status": "Not Found",
            "message": "The requested URL was not found on the server."
        }
    """
    response = error.get_response()
    response.data = json.dumps(
        {
            "code": error.code,
            "status": error.name,
            "message": error.description,
        }
    )
    response.content_type = "application/json"
    return response
