import logging
from app.classes.web.base_api_handler import BaseApiHandler

logger = logging.getLogger(__name__)


class ApiCraftyLockoutHandler(BaseApiHandler):
    def get(self):
        if self.controller.users.get_id_by_name("anti-lockout-user"):
            return self.finish_json(
                425, {"status": "error", "data": "Lockout recovery already in progress"}
            )
        self.controller.users.start_anti_lockout(self.controller.project_root)
        lockout_msg = (
            "Lockout account has been activated for 1 hour."
            " Please find credentials in confg/anti-lockout.txt"
        )
        return self.finish_json(
            200,
            {
                "status": "ok",
                "data": lockout_msg,
            },
        )
