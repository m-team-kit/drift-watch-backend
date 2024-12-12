"""
## API Methods to list, entitlements.
"""

from flask import current_app
from flask.views import MethodView

from app import schemas, utils
from app.config import Blueprint
from app.tools.authentication import Authentication

blp = Blueprint("Entitlements", __name__, description=__doc__)
auth = Authentication(blueprint=blp)


@blp.route("")
class Entitlements(MethodView):
    """Entitlements API."""

    @auth.access_level("user")
    @auth.inject_user_infos()
    @blp.response(200, schemas.Entitlements)
    def get(self, user_infos):
        """Return list of entitlements based on the provided OIDC token.
        ---
        Internal comment not meant to be exposed.

        Args:
            json: A JSON object representing the query parameters.
            user_infos (dict): User information obtained from the
            authentication token.

        Returns:
            401: If the user is not authenticated or registered.
            403: If the user does not have the required permissions.
        """
        # Search for users based on the provided JSON query.
        _user = utils.get_user(user_infos)

        # Return the paginated list of users.
        entitlements_key = current_app.config["ENTITLEMENTS_FIELD"]
        return {"items": user_infos.user_info.get(entitlements_key, [])}
