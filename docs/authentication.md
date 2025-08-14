# Authentication Guide

This guide explains how authentication and authorization work in the Drift Watch Backend API, including JWT token handling, user registration, and permission management.

## Authentication Overview

The Drift Watch Backend uses **JWT (JSON Web Token) based authentication** with support for OpenID Connect (OIDC) providers. The system is designed to work with various identity providers while maintaining security and flexibility.

### Key Features

- **Stateless Authentication**: No server-side session storage
- **OIDC Compatible**: Works with standard OpenID Connect providers
- **Role-Based Access Control**: Three-tier permission system
- **Multi-Tenant Support**: User isolation and resource sharing
- **Flexible Entitlements**: Configurable role/group mapping

## JWT Token Requirements

### Required Claims

Your JWT token must include the following claims:

```json
{
  "sub": "user-unique-identifier",
  "iss": "https://your-oidc-provider.com",
  "email": "user@example.com", 
  "email_verified": true,
  "aud": "drift-watch-api",
  "exp": 1642665600,
  "iat": 1642662000
}
```

### Entitlements Configuration

The system extracts user roles/groups from a configurable path in the JWT token. By default, it uses the Keycloak format:

```json
{
  "realm_access": {
    "roles": ["platform-access", "data-science-team", "admin"]
  }
}
```

**Configuration**: Set `ENTITLEMENTS_PATH` to customize the claim path (e.g., `"groups"` for simple arrays).

## Obtaining JWT Tokens

### Development with Keycloak

1. **Setup Keycloak Instance**

```bash
docker run -p 8080:8080 \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:latest start-dev
```

2. **Configure Realm and Client**
   - Create a new realm: `drift-watch`
   - Create a client: `drift-watch-api`
   - Configure client settings:
     - Access Type: `public`
     - Valid Redirect URIs: `http://localhost:3000/*`
     - Web Origins: `http://localhost:3000`

3. **Obtain Token**

```bash
curl -X POST "http://localhost:8080/realms/drift-watch/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=drift-watch-api" \
  -d "username=testuser" \
  -d "password=testpass"
```

### Production OIDC Providers

The system works with any OIDC-compliant provider:

**Google Identity Platform**

```javascript
// Frontend token acquisition
const response = await fetch('https://oauth2.googleapis.com/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    grant_type: 'authorization_code',
    client_id: 'your-client-id',
    client_secret: 'your-client-secret',
    code: authorizationCode,
    redirect_uri: 'your-redirect-uri'
  })
});
```

**Azure AD**

```python
# Python example using MSAL
from msal import PublicClientApplication

app = PublicClientApplication(
    "your-client-id",
    authority="https://login.microsoftonline.com/your-tenant-id"
)

result = app.acquire_token_interactive(
    scopes=["api://drift-watch-api/access"]
)
token = result.get("access_token")
```

## User Registration Flow

### First-Time User Setup

1. **Obtain JWT Token**: Get valid token from OIDC provider
2. **Register User**: Call the user registration endpoint
3. **Verify Registration**: Confirm user profile creation

```bash
# Register new user
curl -X POST "https://api.driftwatch.io/user" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**

```json
{
  "id": "user-550e8400-e29b-41d4-a716-446655440000",
  "subject": "user123@provider.com",
  "issuer": "https://auth.provider.com", 
  "email": "user@example.com",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### User Profile Management

```bash
# Get current user profile
curl -X GET "https://api.driftwatch.io/user/self" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Update user profile (email sync)
curl -X PUT "https://api.driftwatch.io/user/self" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Access Control System

### Access Levels

The system implements a three-tier access control model:

#### 1. Everyone (`everyone`)

- **Description**: No authentication required
- **Usage**: Public experiment search, health checks
- **Restrictions**: Read-only access to public resources

#### 2. User (`user`)

- **Description**: Authenticated user with basic entitlements
- **Requirements**:
  - Valid JWT token
  - At least one entitlement from `USERS_ENTITLEMENTS` config
- **Capabilities**:
  - Create and manage own experiments
  - Read public experiments
  - Access based on explicit permissions

#### 3. Admin (`admin`)

- **Description**: Administrative privileges
- **Requirements**:
  - Valid JWT token  
  - At least one entitlement from `ADMIN_ENTITLEMENTS` config
- **Capabilities**:
  - Full access to all resources
  - User management operations
  - System configuration access

### Permission System

Resources use a granular permission system with three levels:

#### Permission Levels

1. **Read**: View resource and its data
2. **Edit**: Modify resource and create sub-resources  
3. **Manage**: Full control including deletion and permission changes

#### Permission Assignment

```json
{
  "permissions": [
    {
      "entity": "user-id-or-group-name",
      "level": "Manage"
    },
    {
      "entity": "data-science-team",
      "level": "Edit"
    },
    {
      "entity": "viewers-group", 
      "level": "Read"
    }
  ]
}
```

#### Permission Resolution

The system determines user permissions through:

1. **Direct Assignment**: User ID matches permission entity
2. **Group Membership**: User's entitlements include permission entity
3. **Highest Wins**: Most permissive level applies when multiple permissions exist
4. **Admin Override**: Admin users bypass permission checks

## API Request Authentication

### Adding Authentication Headers

Include the JWT token in the `Authorization` header:

```http
GET /experiment/search HTTP/1.1
Host: api.driftwatch.io
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### Python Requests Example

```python
import requests

headers = {
    'Authorization': f'Bearer {jwt_token}',
    'Content-Type': 'application/json'
}

response = requests.get(
    'https://api.driftwatch.io/experiment/search',
    headers=headers
)
```

### JavaScript Fetch Example

```javascript
const response = await fetch('https://api.driftwatch.io/experiment/search', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${jwtToken}`,
        'Content-Type': 'application/json'
    }
});
```

## Error Handling

### Authentication Errors

#### 401 Unauthorized

```json
{
  "code": 401,
  "status": "Unauthorized", 
  "message": "Invalid or missing authentication token"
}
```

**Common Causes:**

- Missing `Authorization` header
- Invalid JWT token format  
- Expired token
- Invalid token signature
- Token from untrusted issuer

#### 403 Forbidden  

```json
{
  "code": 403,
  "status": "Forbidden",
  "message": "Insufficient permissions for this operation"
}
```

**Common Causes:**

- User not registered in system
- Missing required entitlements
- Insufficient resource permissions
- Attempting admin operation without admin role

## Configuration

### Environment Variables

```bash
# Entitlement configuration
APP_ENTITLEMENTS_PATH=realm_access/roles
APP_USERS_ENTITLEMENTS=["platform-access", "drift-monitor-user"]
APP_ADMIN_ENTITLEMENTS=["system-admin", "drift-monitor-admin"]

# OIDC provider configuration  
APP_TRUSTED_OP_LIST=["https://auth.provider1.com", "https://auth.provider2.com"]
```

### Multi-Provider Setup

Support multiple OIDC providers by configuring trusted issuer list:

```python
# Configuration example
TRUSTED_OP_LIST = [
    "https://login.microsoftonline.com/your-tenant/v2.0",
    "https://accounts.google.com", 
    "https://your-keycloak.com/realms/drift-watch"
]
```

## Security Best Practices

### Token Handling

1. **Client-Side Storage**: Store tokens securely (HTTP-only cookies recommended)
2. **Token Refresh**: Implement automatic token refresh before expiration
3. **Token Validation**: Verify token format and claims before API calls
4. **Secure Transport**: Always use HTTPS in production

### Permission Management

1. **Principle of Least Privilege**: Grant minimal required permissions
2. **Regular Audits**: Review and audit permission assignments
3. **Group-Based Permissions**: Use groups instead of individual assignments when possible
4. **Owner Permissions**: Creators automatically receive Manage permissions

### Development vs Production

**Development**:

- Use self-signed certificates for local OIDC testing
- Longer token expiration times for convenience
- Debug logging enabled for authentication flow

**Production**:

- Use production OIDC providers with proper certificates
- Short token expiration times (15-30 minutes)
- Comprehensive audit logging
- Rate limiting on authentication endpoints

## Troubleshooting

### Common Issues

**Token Validation Failures**

```bash
# Check token structure
echo "eyJhbGc..." | base64 -d | jq .

# Verify token expiration
python -c "import jwt; print(jwt.decode('token', verify=False))"
```

**Permission Debugging**

```bash  
# Check user entitlements
curl -X GET "https://api.driftwatch.io/entitlement" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Registration Issues**

- Verify email_verified claim is true
- Check required entitlements in token
- Ensure user hasn't already registered

This authentication system provides a secure, flexible foundation for protecting your drift monitoring data while maintaining ease of use for developers and end users.
