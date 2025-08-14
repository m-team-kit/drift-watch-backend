# Drift Watch Backend Documentation

Welcome to the comprehensive documentation for the Drift Watch Backend API. This documentation provides detailed information about the system architecture, API endpoints, deployment, and development workflows.

## Table of Contents

- [Overview](overview.md) - System overview and key features
- [API Reference](api-reference.md) - Complete API endpoint documentation
- [Architecture](architecture.md) - System design and component overview
- [Authentication](authentication.md) - Authentication and authorization guide
- [Database Schema](database-schema.md) - MongoDB collections and data models
- [Deployment](deployment.md) - Production deployment guide
- [Development](development.md) - Development setup and workflows
- [Configuration](configuration.md) - Environment variables and settings
- [Error Handling](error-handling.md) - Error codes and troubleshooting
- [Security](security.md) - Security considerations and best practices

## Quick Links

- **API Documentation**: Access the interactive Swagger UI at `/docs` when running the server
- **Source Code**: [GitHub Repository](https://github.com/m-team-kit/drift-watch-backend)
- **Issues & Support**: [GitHub Issues](https://github.com/m-team-kit/drift-watch-backend/issues)

## Getting Started

1. **Quick Start**: See [Development Guide](development.md) for local setup
2. **API Usage**: Check [API Reference](api-reference.md) for endpoint details
3. **Authentication**: Review [Authentication Guide](authentication.md) for JWT setup
4. **Deployment**: Follow [Deployment Guide](deployment.md) for production setup

## Documentation Standards

This documentation follows the following conventions:
- API endpoints use OpenAPI 3.1 specification
- Code examples are provided in Python and shell scripts
- Configuration uses environment variables with `APP_` prefix
- All examples use realistic sample data
- Error responses include detailed troubleshooting information

## Contributing

To contribute to this documentation:
1. Edit the relevant markdown files in the `docs/` directory
2. Follow the existing structure and formatting conventions
3. Test any code examples for accuracy
4. Submit a pull request with your changes

## Version Information

- **API Version**: 1.0.0
- **OpenAPI Version**: 3.1.0  
- **Python Version**: 3.11+
- **Flask Version**: 3.0.0+

For specific version requirements, see [requirements.txt](../requirements.txt).
