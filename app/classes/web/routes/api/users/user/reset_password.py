import logging
import json
from datetime import timedelta

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from app.classes.helpers.helpers import Helpers
from app.classes.models.crafty_permissions import EnumPermissionsCrafty
from app.classes.models.users import HelperUsers
from app.classes.web.base_api_handler import BaseApiHandler

logger = logging.getLogger(__name__)

reset_password_schema = {
    "type": "object",
    "properties": {
        "password": {
            "type": "string",
            "minLength": 8,
        },
        "expires_hours": {
            "type": ["number", "null"],
            "minimum": 0,
        },
    },
    "additionalProperties": False,
}


class ApiUsersUserResetPasswordHandler(BaseApiHandler):
    def post(self, user_id: str):
        auth_data = self.authenticate_user()
        if not auth_data:
            return

        (
            _,
            exec_user_crafty_permissions,
            _,
            superuser,
            user,
            _,
        ) = auth_data

        # Only superusers or users with USER_CONFIG permission can reset
        if not superuser and EnumPermissionsCrafty.USER_CONFIG not in (
            exec_user_crafty_permissions
        ):
            return self.finish_json(
                403,
                {
                    "status": "error",
                    "error": "ACCESS_DENIED",
                    "error_data": "Insufficient permissions",
                },
            )

        # Verify target user exists
        if not self.controller.users.user_id_exists(user_id):
            return self.finish_json(
                404,
                {
                    "status": "error",
                    "error": "USER_NOT_FOUND",
                    "error_data": f"User {user_id} not found",
                },
            )

        # Prevent non-superusers from resetting superuser passwords
        target_user = HelperUsers.get_user(user_id)
        if target_user["superuser"] and not superuser:
            return self.finish_json(
                403,
                {
                    "status": "error",
                    "error": "ACCESS_DENIED",
                    "error_data": self.helper.translation.translate(
                        "validators", "insufficientPerms", auth_data[4]["lang"]
                    ),
                },
            )

        # Parse request body (may be empty)
        try:
            if self.request.body:
                data = json.loads(self.request.body)
                validate(data, reset_password_schema)
            else:
                data = {}
        except (json.JSONDecodeError, ValidationError) as e:
            return self.finish_json(
                400,
                {
                    "status": "error",
                    "error": "INVALID_JSON",
                    "error_data": str(e),
                },
            )

        # Generate or use provided password
        password = data.get("password") or self.helper.create_pass()

        # Calculate expiry if requested
        password_expires = None
        expires_hours = data.get("expires_hours")
        if expires_hours is not None:
            password_expires = Helpers.get_utc_now() + timedelta(hours=expires_hours)

        # Update the user
        HelperUsers.update_user(
            user_id,
            {
                "password": self.helper.encode_pass(password),
                "require_password_change": True,
                "password_expires": password_expires,
                "valid_tokens_from": Helpers.get_utc_now(),
            },
        )

        # Audit log
        expiry_msg = (
            f", expires in {expires_hours}h" if expires_hours else ", no expiry"
        )
        self.controller.management.add_to_audit_log(
            user["user_id"],
            f"reset password for user {target_user['username']}"
            f" (UID: {user_id}{expiry_msg})",
            server_id=None,
            source_ip=self.get_remote_ip(),
        )

        response_data = {"password": password}
        if password_expires:
            response_data["expires"] = password_expires.isoformat()

        return self.finish_json(200, {"status": "ok", "data": response_data})
