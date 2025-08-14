# Database Schema Documentation

This document describes the MongoDB database schema used by the Drift Watch Backend, including collection structures, field definitions, and relationships between documents.

## Database Overview

**Database Name**: `drifts-data` (configurable via `DATABASE_NAME`)

**Storage Engine**: MongoDB with WiredTiger storage engine

**Schema Philosophy**: Flexible document schema with optional validation rules to support evolution and different use cases.

## Collection Structure

### Overview

```
drifts-data/
├── app.users                    # User profiles and authentication data
├── app.experiments              # Experiment metadata and permissions  
├── app.{experiment_id}          # Individual drift records per experiment
└── app.system_config           # System-wide configuration (future)
```

## Users Collection (`app.users`)

Stores user profile information linked to JWT authentication tokens.

### Document Structure

```json
{
  "_id": "550e8400-e29b-41d4-a716-446655440000",
  "subject": "user123@provider.com", 
  "issuer": "https://auth.provider.com",
  "email": "user@example.com",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `_id` | String (UUID) | Yes | Unique user identifier |
| `subject` | String | Yes | Subject claim from JWT token (sub) |
| `issuer` | String | Yes | Issuer claim from JWT token (iss) |
| `email` | String | Yes | User email address |
| `created_at` | String (ISO8601) | Yes | Account creation timestamp |

### Indexes

```javascript
// Compound index for authentication lookups
db.getCollection("app.users").createIndex(
  { "subject": 1, "issuer": 1 }, 
  { unique: true }
);

// Index for email-based searches (admin operations)
db.getCollection("app.users").createIndex({ "email": 1 });

// Index for temporal queries
db.getCollection("app.users").createIndex({ "created_at": -1 });
```

### Constraints

- **Uniqueness**: Combination of `subject` and `issuer` must be unique
- **Email Format**: Must be valid email address
- **Immutable Fields**: `subject`, `issuer`, `_id`, `created_at` cannot be modified after creation

## Experiments Collection (`app.experiments`)

Stores experiment metadata, permissions, and configuration.

### Document Structure

```json
{
  "_id": "exp-550e8400-e29b-41d4-a716-446655440000",
  "name": "Production Model Monitoring",
  "description": "Comprehensive drift monitoring for production ML models",
  "public": false,
  "permissions": [
    {
      "entity": "user-550e8400-e29b-41d4-a716-446655440000",
      "level": "Manage"
    },
    {
      "entity": "data-science-team",
      "level": "Edit"
    },
    {
      "entity": "stakeholders-group",
      "level": "Read"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `_id` | String (UUID) | Yes | Unique experiment identifier |
| `name` | String | Yes | Human-readable experiment name |
| `description` | String | No | Detailed experiment description |
| `public` | Boolean | Yes | Public visibility flag (default: false) |
| `permissions` | Array[Permission] | Yes | Access control list |
| `created_at` | String (ISO8601) | Yes | Creation timestamp |

### Permission Object Schema

```json
{
  "entity": "string",     // User ID or group/role name
  "level": "string"       // "Read", "Edit", or "Manage"
}
```

### Indexes

```javascript
// Primary key
db.getCollection("app.experiments").createIndex({ "_id": 1 });

// Name-based searches and uniqueness
db.getCollection("app.experiments").createIndex(
  { "name": 1 }, 
  { unique: true }
);

// Public experiments queries
db.getCollection("app.experiments").createIndex({ "public": 1 });

// Permission-based queries
db.getCollection("app.experiments").createIndex({ "permissions.entity": 1 });

// Temporal sorting
db.getCollection("app.experiments").createIndex({ "created_at": -1 });

// Compound index for filtered searches
db.getCollection("app.experiments").createIndex({
  "public": 1,
  "created_at": -1
});
```

### Constraints

- **Unique Name**: Experiment names must be unique across the system
- **Valid Permission Levels**: Only "Read", "Edit", "Manage" are allowed
- **Creator Permissions**: Experiment creator automatically receives "Manage" permission

### Business Rules

1. **Creator Ownership**: User who creates experiment gets automatic "Manage" permission
2. **Name Conflicts**: Experiment names must be unique (case-sensitive)
3. **Public Read Access**: Public experiments allow read access without authentication
4. **Permission Inheritance**: Higher permission levels include lower level capabilities

## Drift Collections (`app.{experiment_id}`)

Each experiment has its own collection for storing drift detection records. Collection names use the experiment ID as suffix.

### Document Structure

```json
{
  "_id": "drift-550e8400-e29b-41d4-a716-446655440000",
  "job_status": "Completed",
  "model": "recommendation_classifier_v2.3",
  "drift_detected": true,
  "parameters": {
    "threshold": 0.05,
    "method": "kolmogorov_smirnov",
    "p_value": 0.001,
    "test_statistic": 0.23,
    "features_analyzed": ["user_age", "session_duration", "click_rate"],
    "reference_period": "2024-01-01T00:00:00Z to 2024-01-07T23:59:59Z",
    "test_period": "2024-01-08T00:00:00Z to 2024-01-14T23:59:59Z",
    "sample_size": 10000
  },
  "tags": ["production", "weekly-check", "critical"],
  "schema_version": "1.0.0",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `_id` | String (UUID) | Yes | Unique drift record identifier |
| `job_status` | String | Yes | Job execution status |
| `model` | String | Yes | Model name/identifier |
| `drift_detected` | Boolean | Yes | Whether drift was detected |
| `parameters` | Object | No | Drift detection parameters and results |
| `tags` | Array[String] | No | Metadata tags for categorization |
| `schema_version` | String | Yes | Schema version for compatibility |
| `created_at` | String (ISO8601) | Yes | Record creation timestamp |

### Job Status Values

| Status | Description |
|--------|-------------|
| `Running` | Drift detection job is currently executing |
| `Completed` | Job completed successfully |
| `Failed` | Job failed due to error or timeout |

### Parameters Object

The `parameters` field is a flexible JSON object that can contain:

**Common Fields:**

```json
{
  "threshold": 0.05,                    // Significance threshold
  "method": "kolmogorov_smirnov",       // Statistical test method
  "p_value": 0.001,                     // Test p-value
  "test_statistic": 0.23,               // Test statistic value
  "confidence_level": 0.95,             // Confidence level
  "sample_size": 10000,                 // Number of samples analyzed
  "features_analyzed": ["f1", "f2"],    // Features included in analysis
  "reference_period": "ISO8601_range",  // Reference data period
  "test_period": "ISO8601_range"        // Test data period
}
```

**Method-Specific Fields:**

```json
// For Kolmogorov-Smirnov test
{
  "ks_statistic": 0.23,
  "critical_value": 0.15
}

// For Population Stability Index
{
  "psi_value": 0.18,
  "bin_count": 10,
  "bin_edges": [0, 0.1, 0.2, ...]
}

// For Chi-squared test  
{
  "chi2_statistic": 15.67,
  "degrees_of_freedom": 5
}
```

### Indexes

```javascript
// Primary key
db.getCollection("app.{experiment_id}").createIndex({ "_id": 1 });

// Status-based filtering
db.getCollection("app.{experiment_id}").createIndex({ "job_status": 1 });

// Model-based queries
db.getCollection("app.{experiment_id}").createIndex({ "model": 1 });

// Drift detection filtering
db.getCollection("app.{experiment_id}").createIndex({ "drift_detected": 1 });

// Tag-based searches
db.getCollection("app.{experiment_id}").createIndex({ "tags": 1 });

// Temporal sorting (most common query)
db.getCollection("app.{experiment_id}").createIndex({ "created_at": -1 });

// Compound index for common filtered queries
db.getCollection("app.{experiment_id}").createIndex({
  "job_status": 1,
  "drift_detected": 1, 
  "created_at": -1
});

// Model and status combination
db.getCollection("app.{experiment_id}").createIndex({
  "model": 1,
  "job_status": 1,
  "created_at": -1
});
```

### Schema Versioning

The `schema_version` field enables backward compatibility and schema evolution:

**Version 1.0.0 (Current)**

- All fields as documented above
- Basic drift detection parameters

**Future Versions**

- **1.1.0**: Extended parameters for advanced drift methods
- **1.2.0**: Nested result structures for multi-variate drift
- **2.0.0**: Breaking changes with migration support

## Data Relationships

### User to Experiment Relationship

```
Users (1) ←→ (N) Experiments
- Users can create multiple experiments
- Users can have permissions on multiple experiments  
- Experiments can have multiple user permissions
```

### Experiment to Drift Relationship

```
Experiments (1) ←→ (N) Drift Records
- Each experiment has its own drift collection
- Drift records belong to exactly one experiment
- Experiment deletion cascades to drift records
```

### Permission Resolution

```python
# Permission resolution logic
def resolve_user_permission(experiment, user_id, user_entitlements):
    permissions = []
    
    for permission in experiment["permissions"]:
        entity = permission["entity"]
        if entity == user_id or entity in user_entitlements:
            permissions.append(permission["level"])
    
    # Return highest permission level
    level_hierarchy = ["Read", "Edit", "Manage"]
    return max(permissions, key=lambda x: level_hierarchy.index(x))
```

## Data Management Operations

### Collection Lifecycle

**Experiment Creation:**

1. Create document in `app.experiments`
2. Create corresponding `app.{experiment_id}` collection
3. Set up indexes on new drift collection

**Experiment Deletion:**

1. Delete all documents from `app.{experiment_id}` collection
2. Drop the drift collection
3. Remove experiment document from `app.experiments`

### Backup Strategy

**Full Backup:**

```bash
mongodump --uri="mongodb://user:pass@host:port/drifts-data"
```

**Incremental Backup:**

```bash
# Backup recent drift records (last 7 days)
mongoexport --collection="app.experiments" --query='{"created_at":{"$gte":"2024-01-08T00:00:00Z"}}'
```

### Data Retention

**Drift Records:**

- Default retention: Indefinite
- Configurable per experiment (future feature)
- Archive old records to cold storage

**User Data:**

- Retain indefinitely for audit purposes
- Anonymize on user request (GDPR compliance)

## Query Patterns

### Common Queries

**Find User's Experiments:**

```javascript
db.getCollection("app.experiments").find({
  $or: [
    {"permissions.entity": "user-id"},
    {"permissions.entity": {$in: ["group1", "group2"]}},
    {"public": true}
  ]
});
```

**Recent Drift Records:**

```javascript
db.getCollection("app.{experiment_id}").find({
  "created_at": {$gte: "2024-01-01T00:00:00Z"},
  "job_status": "Completed"
}).sort({"created_at": -1});
```

**Drift Detection Summary:**

```javascript
db.getCollection("app.{experiment_id}").aggregate([
  {
    $group: {
      _id: "$drift_detected",
      count: {$sum: 1},
      models: {$addToSet: "$model"}
    }
  }
]);
```

### Performance Considerations

**Query Optimization:**

- Use compound indexes for multi-field queries
- Limit result sets with pagination
- Use projection to reduce document size
- Cache frequently accessed data

**Write Optimization:**

- Batch insert drift records when possible
- Use bulk operations for updates
- Consider write concerns for durability vs performance

This schema provides a flexible foundation for storing drift monitoring data while maintaining performance and supporting future enhancements.
