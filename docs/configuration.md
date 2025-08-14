# Configuration Guide

This guide provides comprehensive information about configuring the Drift Watch Backend application for different environments and use cases.

## Configuration Overview

The Drift Watch Backend uses a flexible configuration system based on Pydantic Settings, supporting both environment variables and secret files. Configuration values are loaded in the following priority order:

1. **Explicit parameter values** (highest priority)
2. **Environment variables**
3. **Secret files** in the secrets directory
4. **Default values** (lowest priority)

## Configuration Classes

### Settings Class

The main configuration is managed by the `Settings` class in `app/config.py`:

```python
class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Database Configuration
    database_host: str = "localhost"
    database_port: int = 27017
    database_username: str = ""
    database_password: SecretStr = SecretStr("")
    database_name: str = "drift-watch"
    
    # Authentication Configuration  
    trusted_op_list: List[str] = []
    users_entitlements: List[str] = []
    admin_entitlements: List[str] = []
    entitlements_path: str = "realm_access/roles"
    
    # API Configuration
    api_title: str = "Drift Watch API"
    api_version: str = "1.0.0"
    testing: bool = False
    
    # Secrets Configuration
    secrets_dir: str = "secrets"
```

## Environment Variables

### Database Configuration

Configure MongoDB connection:

```bash
# Basic Database Settings
APP_DATABASE_HOST=localhost
APP_DATABASE_PORT=27017
APP_DATABASE_NAME=drift-watch

# Authentication (use secrets for passwords)
APP_DATABASE_USERNAME=drift_user
# APP_DATABASE_PASSWORD should be in secrets file
```

### Authentication Configuration

Configure JWT authentication and authorization:

```bash
# OpenID Connect Providers (JSON array format)
APP_TRUSTED_OP_LIST='["https://auth.provider.com", "https://login.microsoftonline.com/tenant"]'

# User Permission Configuration (JSON array format)
APP_USERS_ENTITLEMENTS='["drift-watch-user", "platform-access"]'
APP_ADMIN_ENTITLEMENTS='["drift-watch-admin", "platform-admin"]'

# Path to entitlements in JWT token
APP_ENTITLEMENTS_PATH="realm_access/roles"
```

### API Configuration

Configure API metadata and behavior:

```bash
# API Documentation
APP_API_TITLE="Drift Watch API"
APP_API_VERSION="1.2.0"

# Development Settings
APP_TESTING=false

# Secrets Directory
APP_SECRETS_DIR="secrets"
```

## Secrets Management

### Secrets Directory Structure

Create a `secrets/` directory for sensitive configuration:

```
secrets/
├── app_database_password          # Database password
├── app_trusted_op_list            # OIDC providers (JSON)
├── app_users_entitlements        # User permissions (JSON)
├── app_admin_entitlements        # Admin permissions (JSON)
└── custom_secret_file            # Additional secrets
```

### Secret File Formats

#### Text Secrets

Simple string values:

```bash
# secrets/app_database_password
my-secure-database-password
```

#### JSON Secrets

Complex data structures:

```bash
# secrets/app_trusted_op_list
["https://login.microsoftonline.com/tenant-id", "https://auth.example.com"]

# secrets/app_users_entitlements  
["drift-watch-user", "read-access", "write-access"]

# secrets/app_admin_entitlements
["drift-watch-admin", "full-access"]
```

### Docker Secrets

For Docker deployments, mount secrets as files:

```yaml
# docker-compose.yml
services:
  app:
    image: drift-watch-backend
    volumes:
      - ./secrets:/app/secrets:ro
    environment:
      - APP_SECRETS_DIR=/app/secrets
```

## Environment-Specific Configuration

### Development Environment

**Environment Variables (.env.dev)**:

```bash
# Development Database
APP_DATABASE_HOST=localhost
APP_DATABASE_PORT=27017
APP_DATABASE_NAME=drift-watch-dev
APP_DATABASE_USERNAME=dev_user

# Development Authentication
APP_TRUSTED_OP_LIST='["https://dev-auth.example.com"]'
APP_USERS_ENTITLEMENTS='["dev-user"]'
APP_ADMIN_ENTITLEMENTS='["dev-admin"]'

# API Configuration
APP_API_TITLE="Drift Watch API (Development)"
APP_TESTING=false
```

**Secrets (secrets/)**:

```bash
# secrets/app_database_password
dev-password
```

### Testing Environment

**Environment Variables (.env.test)**:

```bash
# Test Database
APP_DATABASE_HOST=localhost
APP_DATABASE_PORT=27017
APP_DATABASE_NAME=drift-watch-test
APP_DATABASE_USERNAME=test_user

# Test Authentication (simplified)
APP_TRUSTED_OP_LIST='["https://test-auth.example.com"]'
APP_USERS_ENTITLEMENTS='["test-user"]'
APP_ADMIN_ENTITLEMENTS='["test-admin"]'

# Testing Configuration
APP_API_TITLE="Drift Watch API (Testing)"
APP_TESTING=true
```

**Secrets (secrets/test/)**:

```bash
# secrets/test/app_database_password  
test-password
```

### Production Environment

**Environment Variables**:

```bash
# Production Database (from orchestrator)
APP_DATABASE_HOST=mongo-cluster.prod.internal
APP_DATABASE_PORT=27017
APP_DATABASE_NAME=drift-watch-prod
APP_DATABASE_USERNAME=drift_service

# Production Authentication
APP_TRUSTED_OP_LIST='["https://auth.company.com", "https://login.microsoftonline.com/tenant-uuid"]'
APP_USERS_ENTITLEMENTS='["drift-watch-users", "ml-platform-access"]'
APP_ADMIN_ENTITLEMENTS='["drift-watch-admins", "ml-platform-admin"]'
APP_ENTITLEMENTS_PATH="resource_access/drift-watch/roles"

# Production API
APP_API_TITLE="Drift Watch API"
APP_API_VERSION="1.0.0"
APP_TESTING=false
```

**Secrets (mounted from orchestrator)**:

```bash
# /run/secrets/database_password
production-secure-password
```

## Advanced Configuration

### Custom Configuration Loading

Extend the Settings class for custom requirements:

```python
class CustomSettings(Settings):
    """Extended settings with custom behavior."""
    
    # Custom fields
    custom_feature_flag: bool = False
    custom_timeout: int = 30
    
    @validator('database_host')
    def validate_database_host(cls, v):
        """Validate database host format."""
        if not v or v.isspace():
            raise ValueError('Database host cannot be empty')
        return v
    
    @validator('trusted_op_list')
    def validate_trusted_ops(cls, v):
        """Validate OIDC provider URLs."""
        for op in v:
            if not op.startswith('https://'):
                raise ValueError(f'Trusted OP must use HTTPS: {op}')
        return v
    
    class Config:
        """Pydantic configuration."""
        # Custom secrets directory
        secrets_dir = Path('/custom/secrets')
        
        # Environment variable prefix
        env_prefix = 'CUSTOM_APP_'
        
        # JSON encoder for complex types
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value() if v else None
        }
```

### Flask Integration

The Settings class integrates with Flask configuration:

```python
def create_app(**config) -> Flask:
    """Create Flask application with custom configuration."""
    app = Flask(__name__)
    
    # Load settings
    settings = Settings(**config)
    
    # Convert to Flask config format
    flask_config = {
        'DATABASE_URI': f"mongodb://{settings.database_username}:{settings.database_password.get_secret_value()}@{settings.database_host}:{settings.database_port}/{settings.database_name}",
        'API_TITLE': settings.api_title,
        'TESTING': settings.testing
    }
    
    app.config.update(flask_config)
    return app
```

### Configuration Validation

#### Runtime Validation

```python
def validate_configuration(settings: Settings) -> None:
    """Validate configuration at startup."""
    
    # Database connectivity check
    try:
        client = MongoClient(
            host=settings.database_host,
            port=settings.database_port,
            username=settings.database_username,
            password=settings.database_password.get_secret_value(),
            serverSelectionTimeoutMS=5000
        )
        client.admin.command('ping')
    except Exception as e:
        raise ConfigurationError(f"Database connection failed: {e}")
    
    # Authentication provider validation
    for provider in settings.trusted_op_list:
        try:
            response = requests.get(f"{provider}/.well-known/openid_configuration", timeout=5)
            response.raise_for_status()
        except Exception as e:
            raise ConfigurationError(f"OIDC provider unreachable: {provider} - {e}")
```

#### Schema Validation

```python
from marshmallow import Schema, fields, validate

class ConfigurationSchema(Schema):
    """Configuration validation schema."""
    
    database_host = fields.String(required=True, validate=validate.Length(min=1))
    database_port = fields.Integer(validate=validate.Range(min=1, max=65535))
    trusted_op_list = fields.List(fields.Url(schemes=['https']))
    users_entitlements = fields.List(fields.String(validate=validate.Length(min=1)))
```

## Configuration Templates

### Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  drift-watch-backend:
    build: .
    environment:
      # Database Configuration
      - APP_DATABASE_HOST=mongodb
      - APP_DATABASE_PORT=27017
      - APP_DATABASE_NAME=drift-watch
      - APP_DATABASE_USERNAME=drift_user
      
      # Authentication Configuration
      - APP_TRUSTED_OP_LIST=["https://auth.example.com"]
      - APP_USERS_ENTITLEMENTS=["drift-watch-user"]
      - APP_ADMIN_ENTITLEMENTS=["drift-watch-admin"]
      
      # API Configuration
      - APP_API_TITLE=Drift Watch API
      - APP_SECRETS_DIR=/app/secrets
      
    volumes:
      - ./secrets:/app/secrets:ro
    ports:
      - "5000:5000"
    depends_on:
      - mongodb

  mongodb:
    image: mongo:6.0.3
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=admin_password
      - MONGO_INITDB_DATABASE=drift-watch
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

volumes:
  mongodb_data:
```

### Kubernetes Configuration

```yaml
# k8s-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: drift-watch-config
data:
  APP_DATABASE_HOST: "mongodb-service"
  APP_DATABASE_PORT: "27017"
  APP_DATABASE_NAME: "drift-watch"
  APP_API_TITLE: "Drift Watch API"
  APP_TRUSTED_OP_LIST: |
    ["https://auth.company.com"]
  APP_USERS_ENTITLEMENTS: |
    ["drift-watch-user", "platform-access"]

---
apiVersion: v1
kind: Secret
metadata:
  name: drift-watch-secrets
type: Opaque
stringData:
  app_database_password: "secure-password"
  app_admin_entitlements: |
    ["drift-watch-admin"]

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: drift-watch-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: drift-watch-backend
  template:
    metadata:
      labels:
        app: drift-watch-backend
    spec:
      containers:
      - name: backend
        image: drift-watch-backend:latest
        envFrom:
        - configMapRef:
            name: drift-watch-config
        env:
        - name: APP_SECRETS_DIR
          value: "/app/secrets"
        volumeMounts:
        - name: secrets-volume
          mountPath: /app/secrets
          readOnly: true
        ports:
        - containerPort: 5000
      volumes:
      - name: secrets-volume
        secret:
          secretName: drift-watch-secrets
```

## Troubleshooting Configuration

### Common Configuration Issues

#### Database Connection Issues

**Problem**: `ServerSelectionTimeoutError` or connection refused

**Solutions**:

```bash
# Check database connectivity
telnet $APP_DATABASE_HOST $APP_DATABASE_PORT

# Verify credentials
mongosh "mongodb://$APP_DATABASE_USERNAME:$PASSWORD@$APP_DATABASE_HOST:$APP_DATABASE_PORT/$APP_DATABASE_NAME"

# Check network policies (Kubernetes)
kubectl exec -it pod-name -- telnet mongodb-service 27017
```

#### Authentication Issues

**Problem**: JWT tokens not validating

**Solutions**:

```bash
# Verify OIDC provider connectivity
curl -v https://your-auth-provider/.well-known/openid_configuration

# Check token structure
echo $JWT_TOKEN | jq -R 'split(".") | .[1] | @base64d | fromjson'

# Validate entitlements path
echo $JWT_TOKEN | jq -R 'split(".") | .[1] | @base64d | fromjson | .realm_access.roles'
```

#### Configuration Loading Issues

**Problem**: Environment variables or secrets not loading

**Debugging**:

```python
# Add debug logging in Settings class
import logging
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    def __init__(self, **values):
        logger.debug(f"Loading configuration with values: {values}")
        super().__init__(**values)
        logger.debug(f"Final configuration: {self.dict(exclude={'database_password'})}")
```

### Configuration Validation Script

Create a validation script for deployment:

```python
#!/usr/bin/env python3
"""Configuration validation script."""

import sys
from app.config import Settings

def validate_config():
    """Validate current configuration."""
    try:
        settings = Settings()
        
        # Print configuration (excluding secrets)
        config_dict = settings.dict(exclude={'database_password'})
        print(f"Configuration loaded successfully: {config_dict}")
        
        # Validate critical settings
        if not settings.database_host:
            raise ValueError("Database host is required")
            
        if not settings.trusted_op_list:
            raise ValueError("At least one trusted OP is required")
            
        if not settings.users_entitlements:
            raise ValueError("User entitlements are required")
            
        print("✅ Configuration validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

if __name__ == "__main__":
    if not validate_config():
        sys.exit(1)
```

This configuration guide provides comprehensive coverage of all configuration aspects for the Drift Watch Backend application, from basic setup to advanced deployment scenarios.
