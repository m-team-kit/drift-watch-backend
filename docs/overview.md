# System Overview

The Drift Watch Backend is a comprehensive REST API service designed to monitor and track data drift and concept drift in machine learning models. It provides a robust platform for storing, querying, and managing drift detection results across multiple experiments and models.

## Key Features

### Experiment Management

- **Hierarchical Organization**: Organize drift runs into experiments for better management
- **Access Control**: Role-based permissions with public/private experiment support
- **Metadata Management**: Store experiment descriptions, tags, and configuration

### Drift Detection Tracking

- **Comprehensive Records**: Store detailed drift detection results with model metadata
- **Job Status Tracking**: Monitor running, completed, and failed drift detection jobs
- **Flexible Parameters**: Store arbitrary drift detection parameters and configurations
- **Tagging System**: Categorize and organize drift runs with custom tags

### Authentication & Authorization

- **JWT-based Authentication**: Secure API access using JSON Web Tokens
- **Role-based Access Control**: Three-tier permission system (Read, Edit, Manage)
- **OpenID Connect Integration**: Compatible with standard OIDC providers
- **Multi-tenant Support**: User isolation and resource sharing controls

### Data Management

- **MongoDB Backend**: Scalable NoSQL database for flexible data storage
- **Flexible Querying**: MongoDB-style queries with sorting and filtering
- **Pagination Support**: Efficient handling of large result sets
- **Data Validation**: Comprehensive input validation and type checking

### API Features

- **RESTful Design**: Clean, consistent API following REST principles
- **OpenAPI Documentation**: Interactive Swagger UI with complete API docs
- **Error Handling**: Structured error responses with detailed messages
- **Versioning Support**: Schema versioning for backward compatibility

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client Apps   │────│ ---------------  │────│   API Gateway   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                         ┌───────────────────────────────┼─────────────────────────────┐
                         │                               │                             │
                  ┌──────▼──────┐               ┌────────▼────────┐         ┌─────────▼────────┐
                  │  Auth Service│              │ Drift Watch API │         │  Monitoring      │
                  │   (OIDC)     │              │   (Flask)       │         │   & Logging      │
                  └──────────────┘              └─────────────────┘         └──────────────────┘
                                                         │
                                                ┌────────▼────────┐
                                                │    MongoDB      │
                                                │   Database      │
                                                └─────────────────┘
```

## Core Components

### Flask Application

- **Framework**: Flask 3.0+ with modern Python async support
- **Extensions**: Flask-SMOREST for API documentation and validation
- **Configuration**: Pydantic Settings for type-safe configuration management
- **Error Handling**: Centralized exception handling with JSON responses

### Authentication Layer

- **FLAAT Integration**: Flask with Access And Authentication Tokens library
- **JWT Processing**: Token validation and user information extraction
- **Role Management**: Configurable entitlements and access levels
- **Security Headers**: CORS, security headers, and token validation

### Database Layer

- **MongoDB**: Document database for flexible schema evolution
- **PyMongo**: Official Python MongoDB driver
- **Connection Management**: Connection pooling and timeout handling
- **Data Modeling**: Flexible document structure with validation

### API Documentation

- **OpenAPI 3.1**: Latest specification for comprehensive API docs
- **Swagger UI**: Interactive documentation and API testing interface
- **Schema Generation**: Automatic documentation from Marshmallow schemas
- **Security Documentation**: Authentication requirements and examples

## Data Flow

### Experiment Lifecycle

1. **Creation**: User creates experiment with metadata and permissions
2. **Configuration**: Set up access controls and public visibility
3. **Population**: Add drift detection runs to experiment
4. **Analysis**: Query and analyze drift results
5. **Management**: Update metadata, permissions, or archive

### Drift Detection Workflow

1. **Job Submission**: Client submits drift detection job to experiment
2. **Status Updates**: Job status tracked through running/completed/failed states
3. **Result Storage**: Drift detection results stored with comprehensive metadata
4. **Querying**: Results retrieved via flexible search and filtering APIs

### Authentication Flow

1. **Token Acquisition**: Client obtains JWT from OIDC provider
2. **API Request**: Client includes JWT in Authorization header
3. **Token Validation**: FLAAT validates token and extracts user info
4. **Permission Check**: System verifies user permissions for requested resource
5. **Response**: API returns requested data or permission error

## Use Cases

### ML Operations Teams

- Monitor model performance across environments
- Track drift detection results over time
- Manage access to drift data across team members
- Integrate with CI/CD pipelines for automated drift monitoring

### Data Scientists

- Store and analyze drift detection experiments
- Compare different drift detection algorithms
- Share results with colleagues through controlled access
- Maintain historical records of model behavior

### Platform Teams

- Provide centralized drift monitoring service
- Implement governance and compliance controls
- Scale monitoring across multiple teams and projects
- Integrate with existing MLOps infrastructure

## Technology Stack

### Backend Framework

- **Python 3.11+**: Modern Python with type hints and async support
- **Flask 3.0+**: Lightweight web framework with extensive ecosystem
- **Flask-SMOREST**: API framework with OpenAPI integration
- **Marshmallow**: Schema validation and serialization

### Database & Storage

- **MongoDB 6.0+**: Document database with advanced querying
- **PyMongo**: Official MongoDB Python driver
- **GridFS**: Large file storage capabilities (if needed)

### Authentication & Security

- **FLAAT**: JWT authentication library for Flask
- **PyJWT**: JSON Web Token processing
- **OpenID Connect**: Standard authentication protocol
- **CORS**: Cross-origin resource sharing support

### Development & Deployment

- **Docker**: Containerization for consistent deployments
- **Gunicorn**: WSGI server for production deployments
- **pytest**: Comprehensive testing framework
- **MongoDB Mock**: Testing with mock database

## Performance Characteristics

### Scalability

- **Database Scaling**: MongoDB replica sets and sharding support
- **Caching**: In-memory caching for frequently accessed data
- **Pagination**: Efficient handling of large result sets

### Reliability

- **Error Handling**: Comprehensive error responses with recovery guidance
- **Health Checks**: Built-in health monitoring endpoints
- **Connection Management**: Database connection pooling and retry logic
- **Monitoring**: Structured logging and metrics collection

### Security

- **JWT Validation**: Token-based authentication with configurable validation
- **Role-based Access**: Fine-grained permissions with inheritance
- **Input Validation**: Comprehensive request validation and sanitization
- **HTTPS**: TLS encryption for all API communications
