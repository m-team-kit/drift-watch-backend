"""
Utility functions for the Drift Watch Backend application.

This module provides common utility functions used throughout the application
for user management, resource access control, database operations, and HTTP
response formatting. These utilities abstract common patterns and ensure 
consistent behavior across all API endpoints.

Key functionality:
- User authentication and registration validation
- Resource retrieval with proper error handling  
- Permission-based access control system
- Pagination utilities for list endpoints

Permission System:
The application uses a three-tier permission system:
- Read: View resources and their data
- Edit: Modify existing resources and create new items  
- Manage: Full control including deletion and permission management

Access Control:
- Public resources are accessible to all users for read operations
- Private resources require explicit permission grants
- Admin users have full access to all resources
- Permissions can be granted to individual users or groups via entitlements
"""

from functools import reduce

from flask import abort, current_app

from app.tools import authentication


def get_user(user_infos):
    """
    Retrieve a registered user from the database using authentication token information.
    
    Searches for a user record matching the subject (sub) and issuer (iss) claims
    from the JWT token. This links authenticated tokens to registered user accounts
    in the system.
    
    Args:
        user_infos (dict): User information extracted from JWT token containing:
            - sub: Subject identifier (user ID from identity provider)  
            - iss: Issuer URL (identity provider that issued the token)
            
    Returns:
        dict: User record from database with fields:
            - _id: Unique user identifier
            - email: User's email address
            - subject: Subject claim from original token
            - issuer: Issuer claim from original token
            - created_at: Account creation timestamp
            
    Raises:
        403 Forbidden: If no registered user matches the token information
        
    Example:
        user_infos = {"sub": "user123", "iss": "https://auth.example.com"}  
        user = get_user(user_infos)
        # Returns user record or raises 403 if not registered
    """
    collection = current_app.config["db"]["app.users"]
    sub, iss = user_infos["sub"], user_infos["iss"]
    user = collection.find_one({"subject": sub, "issuer": iss})
    return user or abort(403, "User not registered.")


def get_experiment(experiment_id):
    """
    Retrieve an experiment record from the database by its unique identifier.
    
    Experiments are the top-level containers for drift detection runs and contain
    metadata like name, description, permissions, and public visibility settings.
    
    Args:
        experiment_id (str): The unique UUID identifier of the experiment
        
    Returns:
        dict: Experiment record containing:
            - _id: Unique experiment identifier  
            - name: Human-readable experiment name
            - description: Optional experiment description
            - public: Boolean indicating if experiment is publicly accessible
            - permissions: List of permission objects granting access
            - created_at: Experiment creation timestamp
            
    Raises:
        404 Not Found: If no experiment exists with the provided ID
        
    Example:
        experiment = get_experiment("550e8400-e29b-41d4-a716-446655440000")
        # Returns experiment record or raises 404 if not found
    """
    collection = current_app.config["db"]["app.experiments"]
    experiment = collection.find_one({"_id": experiment_id})
    return experiment or abort(404, "Experiment not found.")


def get_drifts(experiment_id, drift_id):
    """
    Retrieve a specific drift detection record from an experiment's collection.
    
    Each experiment has its own MongoDB collection storing drift detection runs.
    This function fetches a specific drift record by ID from the appropriate
    experiment collection.
    
    Args:
        experiment_id (str): UUID of the parent experiment
        drift_id (str): UUID of the specific drift record to retrieve
        
    Returns:
        dict: Drift record containing:
            - _id: Unique drift record identifier
            - job_status: Current status ("Running", "Completed", "Failed")
            - model: Name/identifier of the ML model being monitored  
            - drift_detected: Boolean indicating if drift was detected
            - parameters: Dictionary of drift detection parameters
            - tags: List of metadata tags for categorization
            - schema_version: Version of the drift record schema
            - created_at: Record creation timestamp
            
    Raises:
        404 Not Found: If no drift record exists with the provided ID
        
    Example:
        drift = get_drifts("exp-uuid", "drift-uuid")
        # Returns drift record or raises 404 if not found
    """
    collection = current_app.config["db"][f"app.{experiment_id}"]
    drift = collection.find_one({"_id": drift_id})
    return drift or abort(404, "Drift not found.")


def get_permission(resource, user_id, user_infos):
    """
    Determine the highest permission level a user has for a specific resource.
    
    Analyzes the resource's permission list to find access levels granted to the
    user either directly or through group entitlements. Returns the most permissive
    level found using the permission hierarchy.
    
    Args:
        resource (dict): Resource object containing 'permissions' list
        user_id (str): Unique identifier of the user
        user_infos (dict): User authentication info containing entitlements
        
    Returns:
        str: Highest permission level found:
            - "Manage": Full control (create, read, update, delete, permissions)
            - "Edit": Modify access (create, read, update) 
            - "Read": View-only access
            - None: No permissions found
            
    Permission Resolution:
    1. Checks direct user permissions (entity == user_id)
    2. Checks group permissions via entitlements  
    3. Returns the highest level found in the hierarchy
    
    Example:
        resource = {
            "permissions": [
                {"entity": "user123", "level": "Edit"},
                {"entity": "admin-group", "level": "Manage"}
            ]
        }
        level = get_permission(resource, "user123", user_infos) 
        # Returns "Edit" or "Manage" depending on user's group membership
    """
    titles = authentication.get_entitlements(user_infos).union({user_id})
    permissions = resource.get("permissions", [])
    perms = set(p["level"] for p in permissions if p["entity"] in titles)
    if "Manage" in perms:  # Top level permission
        return "Manage"
    if "Edit" in perms:  # Second level permission
        return "Edit"
    if "Read" in perms:  # Third level permission
        return "Read"
    return None  # No permission found


def check_access(resource, user_id, user_infos, level="Read"):
    """
    Verify that a user has sufficient permissions to perform an operation on a resource.
    
    Enforces the permission-based access control system by checking if the user's
    actual permission level meets or exceeds the required level. Provides special
    handling for public resources and admin users.
    
    Args:
        resource (dict): Resource object with 'permissions' and optional 'public' fields
        user_id (str): Unique identifier of the user (None for anonymous)
        user_infos (dict): User authentication information (None for anonymous)  
        level (str, optional): Required permission level. Defaults to "Read".
        
    Returns:
        bool: True if access is granted (for public read access)
        
    Raises:
        403 Forbidden: If the user lacks sufficient permissions
        
    Access Control Rules:
    - Public resources allow read access to everyone
    - Admin users have full access to all resources
    - Registered users need explicit permissions for private resources
    - Anonymous users can only access public resources for read operations
    
    Permission Hierarchy (from least to most permissive):
    Read < Edit < Manage
    
    Example:
        # Check if user can edit an experiment
        check_access(experiment, user_id, user_infos, level="Edit")
        # Raises 403 if user doesn't have Edit or Manage permissions
        
        # Public resource read access (always succeeds)  
        public_resource = {"public": True}
        check_access(public_resource, None, None, level="Read")
    """
    if resource.get("public", False) and level == "Read":
        return True
    if not user_infos or not authentication.is_user(user_infos):
        return abort(403, "Resource is not public.")
    if authentication.is_admin(user_infos):
        return True
    match get_permission(resource, user_id, user_infos):
        case "Manage":
            return True
        case "Edit" if level in ["Read", "Edit"]:
            return True
        case "Read" if level == "Read":
            return True
    return abort(403, "Insufficient permissions.")


def pagination_header(page, page_size, total):
    """
    Generate pagination metadata for API list responses.
    
    Creates a comprehensive pagination object containing navigation information
    for paginated API endpoints. Includes current page info, total counts, and
    navigation page numbers.
    
    Args:
        page (int): Current page number (1-based)
        page_size (int): Number of items per page  
        total (int): Total number of items across all pages
        
    Returns:
        dict: Pagination metadata containing:
            - total: Total number of items
            - total_pages: Total number of pages
            - first_page: First page number (1) or 0 if no items
            - last_page: Last page number  
            - page: Current page number
            - previous_page: Previous page number or 0 if on first page
            - next_page: Next page number or None if on last page
            
    Calculation Logic:
    - Total pages computed using ceiling division
    - Navigation pages handle edge cases (first/last page)
    - Zero-based numbering for edge cases when no items exist
    
    Example:
        headers = pagination_header(page=2, page_size=10, total=45)
        # Returns:
        # {
        #     "total": 45,
        #     "total_pages": 5, 
        #     "first_page": 1,
        #     "last_page": 5,
        #     "page": 2,
        #     "previous_page": 1, 
        #     "next_page": 3
        # }
    """
    return {
        "total": total,
        "total_pages": (total + page_size - 1) // page_size,
        "first_page": 1 if total > 0 else 0,
        "last_page": (total + page_size - 1) // page_size,
        "page": page,
        "previous_page": page - 1 if page > 1 else 0,
        "next_page": page + 1 if page * page_size < total else None,
    }
