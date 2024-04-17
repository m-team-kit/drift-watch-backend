"""Package for all blueprints in the application."""

from app.blueprints import drift as _drift
from app.blueprints import user as _user

drift = _drift.blp
user = _user.blp
