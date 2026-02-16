from prometheus_client import REGISTRY, Info, Gauge
from app.classes.web.metrics_handler import BaseMetricsHandler
from app.classes.shared.metrics.server import ServerMetrics

CRAFTY_INFO = Info("crafty_controller", "Infos of this Crafty Instance")
SERVER_METRICS = ServerMetrics(REGISTRY)


# Decorate function with metric.
class ApiOpenMetricsIndexHandler(BaseMetricsHandler):
    def get(self):
        auth_data = self.authenticate_user()
        if not auth_data:
            return
        authorized_servers = auth_data[0]

        version = self.helper.get_version_string()
        CRAFTY_INFO.info(
            {"version": version, "docker": f"{self.helper.is_env_docker()}"}
        )
        SERVER_METRICS.clear()

        for server in authorized_servers:
            server_id = server["server_id"]
            instance = self.controller.servers.get_server_instance_by_id(server_id)
            SERVER_METRICS.update(instance)

        self.get_registry()
