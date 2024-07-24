from werkzeug import exceptions
import json


def init_app(app):
    """Initialize the exceptions module."""
    app.errorhandler(exceptions.Unauthorized)(error_handler)
    app.errorhandler(exceptions.Forbidden)(error_handler)
    app.errorhandler(exceptions.NotFound)(error_handler)


def error_handler(error):
    """Return a JSON response for a given error."""
    response = error.get_response()
    response.data = json.dumps(
        {
            "error": error.name,
            "description": error.description,
        }
    )
    response.content_type = "application/json"
    return response
