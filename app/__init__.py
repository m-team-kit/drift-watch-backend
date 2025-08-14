"""
Drift Monitoring Backend Application Factory.

This module implements the Flask application factory pattern for the Drift Watch
Backend, providing a clean way to create and configure application instances for
different environments (development, testing, production).

The application factory:
- Creates Flask app instances with environment-specific configuration
- Initializes all application modules (auth, database, error handling, API docs)
- Registers blueprints and routes
- Provides a health check endpoint

Application Architecture:
- Authentication: JWT-based auth with FLAAT integration
- Database: MongoDB with PyMongo driver  
- API Documentation: OpenAPI 3.1 with Flask-SMOREST
- Error Handling: Centralized JSON error responses
- Permission System: Role-based access control

Environment Support:
- Development: Local development with debug features
- Testing: Mock database and test fixtures  
- Production: Optimized for deployment with Gunicorn
"""

from flask import Flask

from app import config
from app.tools import authentication
from app.tools import database
from app.tools import exceptions
from app.tools import openapi


def create_app(**kwds):
    """
    Create and configure a Flask application instance.
    
    Implements the application factory pattern, allowing multiple app instances
    with different configurations for testing, development, and production.
    
    Args:
        **kwds: Configuration overrides passed to Settings constructor.
                Common overrides include:
                - TESTING=True: Enable testing mode
                - DATABASE_HOST: Override database connection
                - API_TITLE: Customize API documentation title
    
    Returns:
        Flask: Configured Flask application instance ready for use
        
    Application Initialization Order:
        1. Create Flask app and load configuration
        2. Initialize authentication system (FLAAT/JWT)
        3. Initialize database connection (MongoDB)
        4. Setup error handlers for consistent JSON responses  
        5. Initialize API documentation (OpenAPI/Swagger)
        6. Register health check route
        
    Example:
        # Development app
        app = create_app()
        
        # Testing app with overrides
        test_app = create_app(TESTING=True, DATABASE_HOST="localhost")
    """
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
    """
    Health check endpoint returning empty 204 No Content response.
    
    Provides a simple health check endpoint at the root path (/) that can be
    used for monitoring, load balancer health checks, and basic connectivity
    testing. Returns minimal response to reduce overhead.
    
    Returns:
        tuple: Empty response body and 204 status code
        
    HTTP Status:
        204 No Content: Indicates the server successfully processed the request
                       but has no content to return
                       
    Usage:
        GET / -> 204 No Content (healthy)
        Used by monitoring systems and load balancers
    """
    return ("", 204)
