# API Reference

This document provides comprehensive information about all API endpoints, request/response formats, and usage examples for the Drift Watch Backend API.

## Base URL

```
https://api.driftwatch.io/
```

For local development:

```
http://localhost:5000/
```

## Authentication

All protected endpoints require a JWT Bearer token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### Token Requirements

- Valid JWT token from configured OIDC provider
- Token must include required claims: `sub`, `iss`, `email`, `email_verified`
- User must have appropriate entitlements for the requested operation

## Common Response Format

### Success Response

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T10:30:00Z",
  // ... other fields specific to the resource
}
```

### Error Response

```json
{
  "code": 404,
  "status": "Not Found", 
  "message": "The requested experiment was not found"
}
```

### Pagination

List endpoints return paginated results with metadata:

```json
{
  "total": 150,
  "total_pages": 15,
  "first_page": 1,
  "last_page": 15,
  "page": 2,
  "previous_page": 1,
  "next_page": 3
}
```

## Experiments API

Experiments are containers for organizing drift detection runs with access control and metadata management.

### List/Search Experiments

Search for experiments using MongoDB-style queries with sorting and pagination.

```http
POST /experiment/search?page=1&page_size=10&sort_by=created_at&order_by=desc
Content-Type: application/json

{
  "name": {"$regex": "production.*", "$options": "i"},
  "public": true
}
```

**Query Parameters:**

- `page` (integer): Page number (default: 1)  
- `page_size` (integer): Items per page (default: 20, max: 100)
- `sort_by` (string): Sort field (`created_at`, `name`, `public`)
- `order_by` (string): Sort order (`asc`, `desc`)

**Response:**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Production Model Monitoring",
    "description": "Drift monitoring for production ML models",
    "public": false,
    "permissions": [
      {
        "entity": "user123", 
        "level": "Manage"
      }
    ],
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### Create Experiment

Create a new experiment with metadata and permissions.

```http
POST /experiment
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "My ML Experiment",
  "description": "Tracking drift for my model",
  "public": false,
  "permissions": [
    {
      "entity": "data-science-team",
      "level": "Edit"
    }
  ]
}
```

**Response:** `201 Created`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My ML Experiment", 
  "description": "Tracking drift for my model",
  "public": false,
  "permissions": [
    {
      "entity": "user123",
      "level": "Manage"  // Creator automatically gets Manage permission
    },
    {
      "entity": "data-science-team",
      "level": "Edit"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Experiment

Retrieve a specific experiment by ID.

```http
GET /experiment/550e8400-e29b-41d4-a716-446655440000
```

**Response:** `200 OK` (same format as create response)

### Update Experiment

Update experiment metadata and permissions (requires Manage permission).

```http
PUT /experiment/550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Updated Experiment Name",
  "description": "New description",
  "public": true,
  "permissions": [
    {
      "entity": "public-viewers",
      "level": "Read"
    }
  ]
}
```

**Response:** `200 OK` (updated experiment object)

### Delete Experiment

Delete an experiment and all its drift records (requires Manage permission).

```http
DELETE /experiment/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <token>
```

**Response:** `204 No Content`

## Drift Detection API

Manage drift detection runs within experiments.

### Search Drift Records

Search drift records within an experiment using MongoDB-style queries.

```http
POST /experiment/550e8400-e29b-41d4-a716-446655440000/drift/search?sort_by=created_at&order_by=desc
Content-Type: application/json

{
  "job_status": "Completed",
  "drift_detected": true,
  "model": {"$regex": "classifier.*"}
}
```

**Query Parameters:**

- `sort_by` (string): Sort field (`created_at`, `job_status`, `model`, `drift_detected`, `schema_version`)
- `order_by` (string): Sort order (`asc`, `desc`)

**Response:**

```json
[
  {
    "id": "drift-550e8400-e29b-41d4-a716-446655440000",
    "job_status": "Completed",
    "model": "classifier_v2.1",
    "drift_detected": true,
    "parameters": {
      "threshold": 0.05,
      "method": "kolmogorov_smirnov",
      "features": ["feature1", "feature2"]
    },
    "tags": ["production", "weekly-check"],
    "schema_version": "1.0.0",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### Create Drift Record

Create a new drift detection record within an experiment.

```http
POST /experiment/550e8400-e29b-41d4-a716-446655440000/drift
Content-Type: application/json
Authorization: Bearer <token>

{
  "job_status": "Completed",
  "model": "classifier_v2.1", 
  "drift_detected": true,
  "parameters": {
    "threshold": 0.05,
    "method": "kolmogorov_smirnov",
    "p_value": 0.001,
    "features_analyzed": ["age", "income", "location"]
  },
  "tags": ["production", "scheduled"]
}
```

**Response:** `201 Created`

```json
{
  "id": "drift-550e8400-e29b-41d4-a716-446655440000",
  "job_status": "Completed",
  "model": "classifier_v2.1",
  "drift_detected": true, 
  "parameters": {
    "threshold": 0.05,
    "method": "kolmogorov_smirnov",
    "p_value": 0.001,
    "features_analyzed": ["age", "income", "location"]
  },
  "tags": ["production", "scheduled"],
  "schema_version": "1.0.0",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Drift Record

Retrieve a specific drift record by ID.

```http
GET /experiment/550e8400-e29b-41d4-a716-446655440000/drift/drift-550e8400-e29b-41d4-a716-446655440000
```

**Response:** `200 OK` (same format as create response)

### Update Drift Record

Update drift detection record (requires Edit permission).

```http
PUT /experiment/550e8400-e29b-41d4-a716-446655440000/drift/drift-550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json
Authorization: Bearer <token>

{
  "job_status": "Completed",
  "drift_detected": false,
  "parameters": {
    "threshold": 0.05,
    "method": "kolmogorov_smirnov", 
    "p_value": 0.15,
    "result": "no_drift_detected"
  }
}
```

**Response:** `200 OK` (updated drift record)

### Delete Drift Record

Delete a drift detection record (requires Edit permission).

```http
DELETE /experiment/550e8400-e29b-41d4-a716-446655440000/drift/drift-550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <token>
```

**Response:** `204 No Content`

## Users API

Manage user registration and profile information.

### Register User

Register the token holder as a new user in the system.

```http
POST /user
Authorization: Bearer <token>
```

**Response:** `201 Created`

```json
{
  "id": "user-550e8400-e29b-41d4-a716-446655440000",
  "subject": "user123@provider.com",
  "issuer": "https://auth.provider.com",
  "email": "user@example.com",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get User Profile

Get the current user's profile information.

```http
GET /user/self
Authorization: Bearer <token>
```

**Response:** `200 OK` (same format as register response)

### Update User Profile

Update the current user's profile information.

```http
PUT /user/self
Authorization: Bearer <token>
```

**Response:** `200 OK` (updated user profile)

### Search Users (Admin Only)

Search for users in the system (requires admin privileges).

```http
POST /user/search?sort_by=created_at&order_by=desc
Content-Type: application/json
Authorization: Bearer <admin-token>

{
  "email": {"$regex": ".*@company.com"}
}
```

**Response:**

```json
[
  {
    "id": "user-550e8400-e29b-41d4-a716-446655440000",
    "subject": "user123@provider.com", 
    "issuer": "https://auth.provider.com",
    "email": "user@company.com",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

## Entitlements API

Retrieve user role and permission information.

### Get User Entitlements

Get the current user's entitlements (roles/groups).

```http
GET /entitlement
Authorization: Bearer <token>
```

**Response:** `200 OK`

```json
{
  "items": [
    "platform-access",
    "data-science-team", 
    "ml-engineers"
  ]
}
```

## Error Codes

### 400 Bad Request

- Invalid request format or parameters
- Missing required fields
- Invalid data types

### 401 Unauthorized  

- Missing or invalid JWT token
- Token expired or malformed
- Invalid token signature

### 403 Forbidden

- Insufficient permissions for the requested operation
- User not registered in the system
- Access denied to private resource

### 404 Not Found

- Requested resource does not exist
- Invalid experiment or drift ID
- User not found

### 409 Conflict

- Resource with same name already exists
- Duplicate user registration attempt
- Conflicting resource state

### 422 Unprocessable Entity

- Request validation failed
- Invalid schema or data format
- Required fields missing or invalid

### 500 Internal Server Error

- Database connection failures
- Unexpected server errors
- System configuration issues

## Rate Limits

- **Authentication**: 100 requests per minute per IP
- **API Operations**: 1000 requests per minute per authenticated user
- **Search Operations**: 100 requests per minute per user
- **Bulk Operations**: 10 requests per minute per user

Rate limit headers are included in responses:

- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Requests remaining in current window  
- `X-RateLimit-Reset`: Time when the rate limit resets

## SDK Examples

### Python Client Example

```python
import requests
import json

class DriftWatchClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def create_experiment(self, name, description, public=False):
        data = {
            'name': name,
            'description': description, 
            'public': public
        }
        response = requests.post(
            f'{self.base_url}/experiment',
            headers=self.headers,
            json=data
        )
        return response.json()
    
    def log_drift_result(self, experiment_id, model, drift_detected, parameters=None):
        data = {
            'job_status': 'Completed',
            'model': model,
            'drift_detected': drift_detected,
            'parameters': parameters or {}
        }
        response = requests.post(
            f'{self.base_url}/experiment/{experiment_id}/drift',
            headers=self.headers,
            json=data
        )
        return response.json()

# Usage
client = DriftWatchClient('https://api.driftwatch.io', 'your-jwt-token')
experiment = client.create_experiment('Production Monitor', 'Main production monitoring')
result = client.log_drift_result(experiment['id'], 'classifier_v1', True, {'threshold': 0.05})
```
