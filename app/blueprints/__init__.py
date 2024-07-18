"""Package for all blueprints in the application."""

from app.blueprints import experiment as _experiment
from app.blueprints import user as _user

experiment = _experiment.blp
user = _user.blp
