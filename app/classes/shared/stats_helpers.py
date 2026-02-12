"""
Stats conversion and formatting utilities
"""
import typing as t


class StatsConverter:
    """Pure functions for stats transformations"""

    @staticmethod
    def bytes_to_gigabytes(bytes_value: int) -> float:
        """
        Convert bytes to GB with 2 decimal precision

        Args:
            bytes_value: Memory in bytes

        Returns:
            float: Memory in GB (e.g., 3.13)
        """
        # Type validation for safety
        if bytes_value is None or not isinstance(bytes_value, (int, float)):
            return 0.0
        if bytes_value <= 0:
            return 0.0
        return round(bytes_value / (1024 ** 3), 2)

    @staticmethod
    def prepare_chart_datasets(
        stats: t.List[t.Dict[str, t.Any]],
        server_type: str = "minecraft-java"
    ) -> t.Dict[str, t.List]:
        """
        Transform raw stats into Chart.js-compatible datasets

        Args:
            stats: List of stat dictionaries from database
            server_type: Type of server (affects player tracking)

        Returns:
            dict: Arrays for players, dates, ram_percent, ram_gb, cpu
        """
        players = []
        dates = []
        ram_percent = []
        ram_gb = []
        cpu = []

        for stat in stats:
            # Track players for Java Edition and Hytale
            if "minecraft-java" in server_type or "hytale" in server_type:
                players.append(stat.get("online", 0))

            # Format date for display
            created = stat.get("created")
            if created:
                dates.append(created.strftime("%Y/%m/%d, %H:%M:%S"))

            # Metrics
            ram_percent.append(stat.get("mem_percent", 0))
            ram_gb.append(StatsConverter.bytes_to_gigabytes(stat.get("mem", 0)))
            cpu.append(stat.get("cpu", 0))

        return {
            "players": players,
            "dates": dates,
            "ram_percent": ram_percent,
            "ram_gb": ram_gb,
            "cpu": cpu,
        }
