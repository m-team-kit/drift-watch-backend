"""Module where database methods are defined."""

from pymongo import MongoClient, timeout


def init_app(app):
    """Initialize the database connection."""
    if app.config["TESTING"]:
        return  # Testing fixtures will set up the database
    client = app.config["db_client"] = MongoClient(
        username=app.config["DATABASE_USERNAME"],
        password=app.config["DATABASE_PASSWORD"],
        host=app.config["DATABASE_HOST"],
        port=app.config["DATABASE_PORT"],
        uuidRepresentation="standard",
    )
    with timeout(seconds=3):  # Check the connection
        app.config["db_info"] = client.server_info()
    app.config["db"] = client[app.config["DATABASE_NAME"]]


NOT_FOUND = {
    "description": "Not Found",
    "content": {
        "application/json": {
            "schema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "integer",
                        "description": "Error code",
                    },
                    "status": {
                        "type": "string",
                        "description": "Error name",
                    },
                    "message": {
                        "type": "string",
                        "description": "Error message",
                    },
                },
            }
        }
    },
}


CONFLICT = {
    "description": "Conflict",
    "content": {
        "application/json": {
            "schema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "integer",
                        "description": "Error code",
                    },
                    "status": {
                        "type": "string",
                        "description": "Error name",
                    },
                    "message": {
                        "type": "string",
                        "description": "Error message",
                    },
                },
            }
        }
    },
}
