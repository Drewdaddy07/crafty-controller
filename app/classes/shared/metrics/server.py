from prometheus_client import CollectorRegistry, Gauge, Info

from app.classes.shared.metrics.unchecked_counter import UncheckedCounter
from app.classes.shared.server import ServerInstance
from datetime import datetime
from psutil import Process


class ServerMetrics:
    registry: CollectorRegistry

    def __init__(self, registry: CollectorRegistry = None):
        self.registry = registry or CollectorRegistry()

        self._pr_server_info = Info(
            name="crafty_server",
            documentation="The version of the minecraft of this server",
            labelnames=["server_id", "server_name"],
            registry=self.registry,
        )
        self._pr_running_time = UncheckedCounter(
            name="crafty_server_running_seconds",
            documentation="Server's running time in seconds since its start",
            labelnames=["server_id", "server_name"],
            registry=self.registry,
        )
        self._pr_cpu_time = UncheckedCounter(
            name="crafty_server_cpu_seconds",
            documentation="The CPU usage of the server",
            labelnames=["server_id", "server_name", "mode"],
            registry=self.registry,
        )
        self._pr_resident_memory = Gauge(
            name="crafty_server_resident_memory",
            documentation="The resident memory usage of the server",
            labelnames=["server_id", "server_name"],
            registry=self.registry,
        )
        self._pr_virtual_memory = Gauge(
            name="crafty_server_virtual_memory",
            documentation="The virtual memory usage of the server",
            labelnames=["server_id", "server_name"],
            registry=self.registry,
        )
        self._pr_online_players = Gauge(
            name="crafty_server_online_players",
            documentation="The number of players online for a server",
            labelnames=["server_id", "server_name"],
            registry=self.registry,
        )
        self._pr_max_players = Gauge(
            name="crafty_server_max_players",
            documentation="The maximum number of online players",
            labelnames=["server_id", "server_name"],
            registry=self.registry,
        )
        self._pr_server_size = Gauge(
            name="crafty_server_size",
            documentation="The size of the server directory in bytes",
            labelnames=["server_id", "server_name"],
            registry=self.registry,
        )

    def _proxy(self, instance: ServerInstance):
        return MetricProxy(self, instance)

    def clear(self):
        self._pr_server_info.clear()
        self._pr_running_time.clear()
        self._pr_cpu_time.clear()
        self._pr_resident_memory.clear()
        self._pr_virtual_memory.clear()
        self._pr_online_players.clear()
        self._pr_max_players.clear()
        self._pr_server_size.clear()

    def update(self, instance: ServerInstance):
        proxy = self._proxy(instance)

        server_stats = instance.get_servers_stats()
        if server_stats["version"] and server_stats["desc"]:
            proxy.m_server_info.info(
                {
                    "version": server_stats["version"],
                    "description": server_stats["desc"],
                }
            )
        else:
            proxy.m_server_info.clear()
        proxy.m_online_players.set(server_stats["online"] or 0)
        proxy.m_max_players.set(server_stats["max"] or 0)
        proxy.m_server_size.set(instance.server_size)

        if instance.check_running():
            start_time = datetime.fromisoformat(instance.start_time)
            time_running = (datetime.utcnow() - start_time).total_seconds()

            proxy.m_running_time.set(time_running)

            process = Process(instance.get_pid())
            cpuinfo = process.cpu_times()

            proxy.m_cpu_time("user").set(cpuinfo.user)
            proxy.m_cpu_time("system").set(cpuinfo.system)
            proxy.m_cpu_time("children_user").set(cpuinfo.children_user)
            proxy.m_cpu_time("children_system").set(cpuinfo.children_system)

            meminfo = process.memory_info()

            proxy.m_resident_memory.set(meminfo.rss)
            proxy.m_virtual_memory.set(meminfo.vms)
        else:
            proxy.m_running_time.set(0)
            proxy.m_resident_memory.set(0)
            proxy.m_virtual_memory.set(0)
            proxy.m_cpu_time("user").set(0)
            proxy.m_cpu_time("system").set(0)
            proxy.m_cpu_time("children_user").set(0)
            proxy.m_cpu_time("children_system").set(0)

class MetricProxy:
    m_running_time: UncheckedCounter
    m_resident_memory: Gauge
    m_virtual_memory: Gauge
    m_server_info: Info
    m_online_players: Gauge
    m_max_players: Gauge
    m_server_size: Gauge

    def __init__(self, metrics: ServerMetrics, instance: ServerInstance):
        self._metrics = metrics
        self._instance = instance

    def _labels(self):
        return (self._instance.server_id, self._instance.server_object.server_name)

    def m_cpu_time(self, mode: str) -> UncheckedCounter:
        return self._metrics._pr_cpu_time.labels(*self._labels(), mode)

    def __getattr__(self, name: str):
        if not name.startswith("m_"):
            return None
        internal_name = name.replace("m_", "_pr_")
        prop = getattr(self._metrics, internal_name)
        return prop.labels(*self._labels())
