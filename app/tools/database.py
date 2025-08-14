"""
Database connection and configuration module for the Drift Watch Backend.

This module handles MongoDB database connectivity, initialization, and provides
standardized error response schemas for database-related operations. It manages
the database connection lifecycle and ensures proper timeout handling.

The module supports:
- MongoDB client initialization with authentication
- Connection validation with timeout protection
- Test environment database mocking support
- Standardized OpenAPI error response schemas

Environment Variables Required:
- DATABASE_USERNAME: MongoDB authentication username
- DATABASE_PASSWORD: MongoDB authentication password
- DATABASE_HOST: MongoDB server hostname or IP
- DATABASE_PORT: MongoDB server port (default: 27017)
- DATABASE_NAME: Target database name for the application

Collections Used:
- app.users: User account information
- app.experiments: Experiment metadata and permissions
- app.{experiment_id}: Individual drift detection runs per experiment
"""

from pymongo import MongoClient, timeout


def init_app(app):
    """
    Initialize MongoDB database connection for the Flask application.

    Sets up the MongoDB client with authentication and validates the connection.
    In testing mode, database initialization is skipped to allow test fixtures
    to configure mock databases.

    Args:
        app (Flask): The Flask application instance to configure.

    Raises:
        ConnectionFailure: If unable to connect to MongoDB server.
        TimeoutError: If connection validation exceeds timeout.

    Side Effects:
        - Sets app.config['db_client'] to MongoDB client instance
        - Sets app.config['db_info'] to server information
        - Sets app.config['db'] to the target database instance
    """
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
