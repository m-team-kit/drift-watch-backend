# Architecture Guide

This document provides a detailed overview of the Drift Watch Backend system architecture, including component relationships, data flow, and design decisions.

## High-Level Architecture

The Drift Watch Backend follows a modern microservices-inspired architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Client Layer                                │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────┤
│   Web Apps      │   Mobile Apps   │   CLI Tools     │   ML Pipelines      │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────┘
                                    │
                                    │
┌───────────────────────────────────▼─────────────────────────────────────┐
│                        Drift Watch Backend API                          │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────┤
│ Authentication  │   Experiments   │     Drifts      │       Users         │
│   & Security    │   Management    │   Management    │    Management       │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────┐
│                            Data Layer                                   │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────┤
│   MongoDB       │     Redis       │   File Storage  │    Monitoring       │
│   (Primary)     │   (Caching)     │   (Optional)    │    & Logging        │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────┘
```

## Core Components

### 1. API Gateway Layer

**Flask Application Factory**

- Implements the factory pattern for flexible app creation
- Supports multiple configurations (dev, test, prod)
- Handles dependency injection and module initialization

**Request Processing Pipeline**

```
Request → Authentication → Authorization → Validation → Business Logic → Response
```

### 2. Authentication & Authorization

**JWT Token Processing (FLAAT)**

```python
# Token validation flow
JWT Token → FLAAT Validator → User Info Extraction → Entitlements Check → Access Grant/Deny
```

**Access Control Matrix**

```
Resource Type    | Everyone | User  | Admin | Owner
─────────────────|----------|-------|-------|--------
Public Experiments | Read   | Read  | All   | All
Private Experiments| None   | Perm* | All   | All
Drift Records    | None     | Perm* | All   | All
User Profiles    | None     | Own   | All   | Own
System Config    | None     | None  | All   | None

* Perm = Based on explicit permissions
```

**Entitlements System**

- **Source**: JWT token claims (configurable path)
- **Format**: Array of role/group strings  
- **Validation**: Intersection with configured allowed entitlements
- **Inheritance**: Groups can inherit permissions from parent groups

### 3. API Layer Architecture

**Flask-SMOREST Integration**

```
Blueprint → Schema Validation → Business Logic → Response Serialization → OpenAPI Docs
```

**Request Validation Pipeline**

1. **Content-Type Validation**: Ensures JSON for POST/PUT
2. **Schema Validation**: Marshmallow schema validation
3. **Custom Validation**: Business rule validation
4. **Permission Check**: Authorization validation
5. **Data Processing**: Core business logic

**Response Format Standardization**

```python
# Success Response Structure
{
  "id": "uuid",
  "created_at": "iso8601", 
  "updated_at": "iso8601",  # if applicable
  // ... resource-specific fields
}

# Error Response Structure  
{
  "code": int,
  "status": "string",
  "message": "string",
  "details": {}  # optional
}
```

### 4. Data Layer Design

**MongoDB Collections Structure**

```
drifts-data/
├── app.users                    # User profiles and authentication
├── app.experiments              # Experiment metadata and permissions
├── app.{experiment_id}          # Individual drift records per experiment
└── app.system                   # System configuration (future)
```

**Document Schema Evolution**

- **Schema Versioning**: Each drift record includes schema_version field
- **Backward Compatibility**: API handles multiple schema versions
- **Migration Strategy**: Lazy migration on read/write operations

**Indexing Strategy**

```javascript
// app.experiments collection
{
  "_id": 1,                    // Primary key
  "name": 1,                   // Name-based queries
  "created_at": -1,            // Time-based sorting
  "permissions.entity": 1       // Permission queries
}

// app.{experiment_id} collections  
{
  "_id": 1,                    // Primary key
  "created_at": -1,            // Time-based sorting
  "job_status": 1,             // Status filtering
  "model": 1,                  // Model-based queries
  "drift_detected": 1,         // Boolean filtering
  "tags": 1                    // Tag-based filtering
}
```

### 5. Security Architecture

**Defense in Depth Strategy**

```
Layer 1: Network Security (TLS, Firewalls)
Layer 2: API Gateway (Rate limiting, IP filtering)
Layer 3: Authentication (JWT validation)
Layer 4: Authorization (Permission checks)
Layer 5: Input Validation (Schema validation)
Layer 6: Data Access Control (MongoDB permissions)
```

**JWT Security Model**

- **Validation**: Signature verification with public key
- **Claims Processing**: Extract user identity and entitlements
- **Token Refresh**: Client-side token refresh handling
- **Revocation**: Stateless tokens with short expiration

## Design Patterns

### 1. Repository Pattern (Implicit)

While not explicitly implemented as repository classes, the data access is centralized in utility functions:

```python
# Centralized data access in utils.py
get_user(user_infos) → User document
get_experiment(experiment_id) → Experiment document  
get_drifts(experiment_id, drift_id) → Drift document
```

### 2. Factory Pattern

Application creation uses the factory pattern for flexibility:

```python
# Different configurations for different environments
dev_app = create_app()
test_app = create_app(TESTING=True)
prod_app = create_app(**production_config)
```

### 3. Decorator Pattern

Authentication and validation use decorator patterns extensively:

```python
@auth.access_level("user")
@blp.arguments(CreateExperiment)
@blp.response(201, Experiment)
def create_experiment(self, json, user_infos):
    # Business logic
```

### 4. Strategy Pattern

Permission checking implements strategy pattern for different access levels:

```python
# Different strategies for different access levels
def check_access(resource, user_id, user_infos, level="Read"):
    if resource.get("public") and level == "Read":
        return  # Public read strategy
    if authentication.is_admin(user_infos):
        return  # Admin access strategy  
    # Permission-based strategy
    user_level = get_permission(resource, user_id, user_infos)
    # ...
```

## Data Flow Patterns

### 1. Request Processing Flow

```
HTTP Request
    │
    ▼
Flask Request Handler
    │
    ▼  
Authentication Middleware (FLAAT)
    │
    ▼
Request Validation (Marshmallow)
    │
    ▼
Authorization Check (Permission System)
    │
    ▼
Business Logic (Blueprint Methods)
    │
    ▼
Database Operations (MongoDB)
    │
    ▼
Response Serialization (Marshmallow)
    │
    ▼
HTTP Response
```

### 2. Authentication Flow

```
Client Request with JWT
    │
    ▼
FLAAT Token Validation
    │
    ├─ Valid Token ─────────────────┐
    │                               ▼
    └─ Invalid Token ──→ 401 Error  Extract User Info
                                    │
                                    ▼
                              Check Entitlements
                                    │
                                    ├─ Has Required Role ──→ Continue
                                    │
                                    └─ Missing Role ───────→ 403 Error
```

### 3. Permission Resolution Flow

```
Resource Access Request
    │
    ▼
Check if Public Resource ──→ Yes ──→ Allow Read Access
    │
    No
    ▼
Extract User ID & Entitlements  
    │
    ▼
Query Resource Permissions
    │
    ▼
Match User/Groups to Permissions
    │
    ▼
Calculate Highest Permission Level
    │
    ▼
Compare Required vs. Actual Level
    │
    ├─ Sufficient ──→ Allow Access
    │
    └─ Insufficient ──→ 403 Forbidden
```

## Scalability Considerations

### 1. Horizontal Scaling

**Stateless Design**

- No session storage in application servers
- JWT tokens carry all necessary user context
- Database handles state management

### 2. Database Scaling

**Collection Sharding Strategy**

```
Experiment Collections: Shard by experiment_id
User Collection: Shard by user geographical region
System Collections: Replicate across all shards
```

**Connection Management**

- Connection pooling with configurable pool size
- Automatic connection retry with exponential backoff
- Connection health monitoring

### 3. Caching Strategy

**Application-Level Caching**

```python
# Future implementation
@cached(ttl=300)  # 5 minute TTL
def get_user_permissions(user_id):
    # Expensive permission calculation
```

**Database Query Optimization**

- Index-based query optimization
- Aggregation pipeline optimization for complex queries
- Query result pagination to limit memory usage

### 4. Performance Monitoring

**Metrics Collection**

- Request latency percentiles (P50, P95, P99)
- Error rates by endpoint and error type
- Database query performance metrics
- Memory and CPU utilization

**Health Checks**

```python
# Implemented health check
GET / → 204 No Content  # Basic connectivity
GET /health → 200 OK     # Future: Detailed health status
```

## Deployment Architecture

### 1. Container Strategy

**Docker Multi-Stage Build**

```dockerfile
# Build stage: Install dependencies
FROM python:3.11 AS build
# ... dependency installation

# Production stage: Minimal runtime
FROM python:3.11-slim AS production  
# ... runtime configuration
```

**Environment Configuration**

- Environment-specific configurations via environment variables
- Secrets management via mounted volumes
- Configuration validation on startup

### 2. Production Deployment

**WSGI Server Configuration**

```bash
gunicorn \
  --workers 4 \
  --worker-class gevent \
  --bind 0.0.0.0:5000 \
  autoapp:app
```

**Process Management**

- Multi-worker deployment for CPU-bound operations
- Gevent worker class for I/O-bound operations
- Graceful shutdown handling
- Health check integration

### 3. Monitoring & Observability

**Structured Logging**

```python
# Future implementation
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO", 
  "user_id": "user123",
  "request_id": "req_456",
  "endpoint": "/experiment/search",
  "duration_ms": 150,
  "status_code": 200
}
```

**Error Tracking**

- Centralized error aggregation (future: Sentry integration)
- Error rate monitoring and alerting
- Performance regression detection

This architecture provides a solid foundation for a scalable, maintainable drift monitoring system while maintaining flexibility for future enhancements and integrations.
