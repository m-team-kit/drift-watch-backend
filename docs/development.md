# Development Guide

This guide provides comprehensive information for setting up a development environment and contributing to the Drift Watch Backend project.

## Development Environment Setup

### Prerequisites

- **Python 3.11+**: Modern Python with type hints support
- **MongoDB 6.0+**: Database server for data storage
- **Git**: Version control system
- **Docker** (optional): For containerized development

### Local Development Setup

#### 1. Clone Repository

```bash
git clone https://github.com/m-team-kit/drift-watch-backend.git
cd drift-watch-backend
```

#### 2. Create Python Environment

**Using Conda (Recommended)**:

```bash
conda create --name drift-watch python=3.11
conda activate drift-watch
```

**Using venv**:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

#### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies  
pip install -r requirements-dev.txt

# Install testing dependencies
pip install -r requirements-test.txt
```

#### 4. Database Setup

**Option 1: Docker MongoDB**

```bash
docker run --name drift-database \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  -d mongo:6.0.3
```

**Option 2: Local MongoDB Installation**

```bash
# Ubuntu/Debian
sudo apt-get install mongodb-org

# macOS with Homebrew
brew install mongodb/brew/mongodb-community

# Start MongoDB service
sudo systemctl start mongod  # Linux
brew services start mongodb-community  # macOS
```

#### 5. Environment Configuration

Create `.env` file in the project root:

```bash
# Copy sample configuration
cp .env.sample .env
```

Edit `.env` with your configuration:

```bash
# Database Configuration
APP_DATABASE_HOST=localhost
APP_DATABASE_PORT=27017
APP_DATABASE_USERNAME=admin
APP_DATABASE_PASSWORD=password
APP_DATABASE_NAME=drift-watch-dev

# Authentication Configuration
APP_TRUSTED_OP_LIST=["https://your-oidc-provider.com"]
APP_USERS_ENTITLEMENTS=["platform-access"]
APP_ADMIN_ENTITLEMENTS=["admin"]
APP_ENTITLEMENTS_PATH=realm_access/roles

# Secrets Directory
APP_SECRETS_DIR=secrets

# API Configuration
APP_API_TITLE="Drift Watch API (Development)"
APP_TESTING=false
```

#### 6. Create Secrets Directory

```bash
mkdir -p secrets
echo "password" > secrets/app_database_password
echo '["admin"]' > secrets/app_admin_entitlements
echo '["platform-access"]' > secrets/app_users_entitlements
echo '["https://your-oidc-provider.com"]' > secrets/app_trusted_op_list
```

#### 7. Run Development Server

```bash
# Using Flask development server
export FLASK_APP=autoapp:app
export FLASK_ENV=development
python -m flask run --debug --port 5000

# Or using the application directly
python -m gunicorn autoapp:app --reload --bind 0.0.0.0:5000
```

### VSCode Development Setup

#### Required Extensions

Install the following VSCode extensions:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.pylint", 
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-toolsai.jupyter",
    "mongodb.mongodb-vscode"
  ]
}
```

#### VSCode Settings

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.args": ["--profile", "black"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests",
    "--verbose"
  ]
}
```

#### Debug Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Flask Development",
      "type": "python",
      "request": "launch",
      "module": "flask",
      "args": ["run", "--debug"],
      "env": {
        "FLASK_APP": "autoapp:app",
        "FLASK_ENV": "development"
      },
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    },
    {
      "name": "Run Tests",
      "type": "python", 
      "request": "launch",
      "module": "pytest",
      "args": ["tests", "-v"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

## Code Quality and Standards

### Code Style

The project follows **Black** formatting with these standards:

- **Line Length**: 120 characters
- **String Quotes**: Double quotes preferred
- **Import Organization**: isort with Black profile

#### Format Code

```bash
# Format with Black
black app/ tests/ --line-length 120

# Sort imports
isort app/ tests/ --profile black

# Lint with Pylint
pylint app/ tests/
```

### Type Hints

Use type hints for all function signatures:

```python
from typing import Dict, List, Optional

def create_experiment(
    name: str, 
    description: Optional[str] = None,
    permissions: List[Dict[str, str]] = None
) -> Dict[str, str]:
    """Create a new experiment with the given parameters."""
    # Implementation
    return {"id": "uuid", "name": name}
```

### Documentation Standards

#### Docstring Format

Use Google-style docstrings:

```python
def process_drift_data(
    experiment_id: str, 
    model_name: str, 
    drift_threshold: float = 0.05
) -> Dict[str, bool]:
    """
    Process drift detection data for a specific model.
    
    Analyzes the provided drift data and determines if significant
    drift has been detected based on the configured threshold.
    
    Args:
        experiment_id: Unique identifier for the experiment
        model_name: Name of the model being monitored  
        drift_threshold: Statistical significance threshold (default: 0.05)
        
    Returns:
        Dictionary containing drift analysis results:
        - drift_detected: Boolean indicating if drift was found
        - confidence: Confidence level of the detection
        
    Raises:
        ValueError: If experiment_id is not found
        InvalidModelError: If model_name is invalid
        
    Example:
        result = process_drift_data("exp-123", "classifier_v1", 0.01)
        if result["drift_detected"]:
            print(f"Drift detected with {result['confidence']} confidence")
    """
```

## Testing

### Test Structure

```
tests/
├── conftest.py                 # Pytest configuration and fixtures
├── constants.py               # Test constants and data
├── fixtures/                  # Test data files
│   ├── database.json         # Mock database data
│   └── secrets/              # Test secrets
├── blp_experiment/           # Experiment API tests
│   ├── conftest.py
│   ├── experiment/           # Individual experiment tests
│   └── experiments/          # Experiment list tests
├── blp_user/                 # User API tests
└── blp_entitlement/         # Entitlement API tests
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/blp_experiment/experiments/test_post.py

# Run with verbose output
pytest tests/ -v

# Run in parallel
pytest tests/ -n auto

# Run only failed tests
pytest tests/ --lf
```

### Writing Tests

#### Test Fixtures

Use pytest fixtures for common test data:

```python
# conftest.py
import pytest
from app import create_app

@pytest.fixture(scope="session")
def app():
    """Create test application."""
    return create_app(TESTING=True)

@pytest.fixture
def client(app):
    """Create test client.""" 
    return app.test_client()

@pytest.fixture
def auth_headers():
    """Create authentication headers."""
    return {
        "Authorization": "Bearer test-jwt-token",
        "Content-Type": "application/json"
    }
```

#### Test Example

```python
import pytest
from flask import url_for

class TestCreateExperiment:
    """Test experiment creation endpoint."""
    
    def test_create_experiment_success(self, client, auth_headers):
        """Test successful experiment creation."""
        data = {
            "name": "Test Experiment",
            "description": "Test description",
            "public": False
        }
        
        response = client.post(
            url_for("Experiments.post"),
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.get_json()
        assert result["name"] == "Test Experiment"
        assert "id" in result
    
    def test_create_experiment_invalid_data(self, client, auth_headers):
        """Test experiment creation with invalid data."""
        data = {"description": "Missing name"}
        
        response = client.post(
            url_for("Experiments.post"),
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
```

### Test Database

Tests use `mongomock` for database mocking:

```python
# conftest.py
import mongomock

@pytest.fixture(scope="session")  
def app():
    """Create test app with mock database."""
    app = create_app(TESTING=True)
    app.config["db_client"] = mongomock.MongoClient()
    return app
```

## API Development

### Adding New Endpoints

#### 1. Define Schema

Add schemas to `app/schemas.py`:

```python
class NewResourceSchema(ma.Schema):
    """Schema for new resource."""
    name = ma.fields.String(required=True)
    value = ma.fields.Integer(validate=validate.Range(min=0))
```

#### 2. Create Blueprint

Create new blueprint file:

```python
# app/blueprints/new_resource.py
from app.config import Blueprint
from app.tools.authentication import Authentication

blp = Blueprint("NewResource", __name__, description="New resource API")
auth = Authentication(blueprint=blp)

@blp.route("")
class NewResource(MethodView):
    """New resource endpoint."""
    
    @auth.access_level("user")
    @blp.arguments(NewResourceSchema)
    @blp.response(201, NewResourceSchema)
    def post(self, json, user_infos):
        """Create new resource."""
        # Implementation
        pass
```

#### 3. Register Blueprint

Add to `app/blueprints/__init__.py`:

```python
from app.blueprints import new_resource as _new_resource
new_resource = _new_resource.blp
```

Register in `app/tools/openapi.py`:

```python
api.register_blueprint(blp.new_resource, url_prefix="/new-resource")
```

### Database Operations

#### Adding New Collection Operations

Add utility functions to `app/utils.py`:

```python
def get_new_resource(resource_id: str) -> Dict[str, Any]:
    """Retrieve new resource by ID."""
    collection = current_app.config["db"]["app.new_resources"]
    resource = collection.find_one({"_id": resource_id})
    if not resource:
        abort(404, "Resource not found")
    return resource
```

## Debugging

### Development Debugging

#### Enable Debug Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python -m flask run
```

#### Using Python Debugger

Add breakpoints in code:

```python
import pdb; pdb.set_trace()  # Simple debugger

# Or use ipdb for enhanced debugging
import ipdb; ipdb.set_trace()
```

#### VSCode Debugging

1. Set breakpoints in VSCode
2. Use "Flask Development" debug configuration
3. Start debugging with F5

### Production Debugging

#### Logging Configuration

```python
import logging

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s %(message)s'
)

logger = logging.getLogger(__name__)
```

#### Database Debugging

```python
# Enable MongoDB query logging
import logging
logging.getLogger('pymongo').setLevel(logging.DEBUG)
```

## Performance Optimization

### Database Query Optimization

#### Use Projections

```python
# Only fetch required fields
users = collection.find(
    {"email": {"$regex": pattern}},
    {"_id": 1, "email": 1, "created_at": 1}
)
```

#### Optimize Indexes

```python
# Create compound indexes for common queries
collection.create_index([
    ("created_at", -1),
    ("status", 1)
])
```

### API Performance

#### Response Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_user_permissions(user_id: str) -> List[str]:
    """Cache expensive permission lookups."""
    # Implementation
    pass
```

#### Pagination

```python
def paginate_results(collection, query, page, page_size):
    """Implement efficient pagination."""
    skip = (page - 1) * page_size
    results = collection.find(query).skip(skip).limit(page_size)
    total = collection.count_documents(query)
    return list(results), total
```

## Git Workflow

### Branch Strategy

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/[name]**: Individual feature development
- **hotfix/[name]**: Critical production fixes

### Commit Messages

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:

```
feat(api): add experiment search functionality

Add MongoDB-style query support for experiment search endpoint
with pagination and sorting capabilities.

Closes #123
```

```
fix(auth): resolve JWT token validation error

Update FLAAT configuration to handle multiple token issuers
properly. Fixes issue with Azure AD tokens.

Fixes #456
```

### Pull Request Process

1. Create feature branch from `develop`
2. Implement feature with tests
3. Ensure all tests pass
4. Update documentation if needed
5. Create pull request to `develop`
6. Request code review
7. Address review feedback
8. Merge after approval

This development guide provides the foundation for contributing effectively to the Drift Watch Backend project while maintaining code quality and consistency.
