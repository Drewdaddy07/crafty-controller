"""
Stats conversion and formatting utilities
"""

import datetime
import typing as t


class StatsConverter:
    """Pure functions for stats transformations"""

    # Gaps larger than this get filled with zero boundary points
    GAP_THRESHOLD_SECONDS = 120  # 2 minutes

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
        return round(bytes_value / (1024**3), 2)

    @staticmethod
    def _make_zero_stat(dt: datetime.datetime) -> dict:
        """Create a zero-value stat entry at the given time"""
        return {
            "created": dt,
            "online": 0,
            "mem_percent": 0,
            "mem": 0,
            "cpu": 0,
        }

    @classmethod
    def fill_gaps(
        cls,
        stats: t.List[t.Dict[str, t.Any]],
        start_time: datetime.datetime = None,
        end_time: datetime.datetime = None,
    ) -> t.List[t.Dict[str, t.Any]]:
        """
        Fill time gaps in stats with zero-value points.

        Ensures the chart spans the full requested range and shows 0
        during periods with no data (e.g., server offline).

        Args:
            stats: Sorted list of stat dicts (ascending by 'created')
            start_time: Requested range start (adds zero point if data
                        starts later)
            end_time: Requested range end (adds zero point if data
                      ends earlier)

        Returns:
            New list with zero-fill points inserted at gap boundaries
        """
        if not stats:
            # No data at all: return zeros at boundaries
            result = []
            if start_time:
                result.append(cls._make_zero_stat(start_time))
            if end_time and end_time != start_time:
                result.append(cls._make_zero_stat(end_time))
            return result

        threshold = datetime.timedelta(seconds=cls.GAP_THRESHOLD_SECONDS)
        filled = []

        first_time = stats[0].get("created")
        last_time = stats[-1].get("created")

        # Add zero at start of range if data begins later
        if start_time and first_time and first_time - start_time > threshold:
            filled.append(cls._make_zero_stat(start_time))
            # Add another zero just before first real point for sharp edge
            filled.append(
                cls._make_zero_stat(first_time - datetime.timedelta(seconds=1))
            )

        # Walk through data and fill internal gaps
        for i, stat in enumerate(stats):
            filled.append(stat)
            if i < len(stats) - 1:
                curr_time = stat.get("created")
                next_time = stats[i + 1].get("created")
                if curr_time and next_time and next_time - curr_time > threshold:
                    # Insert zero at both edges of the gap for sharp drop/rise
                    filled.append(
                        cls._make_zero_stat(curr_time + datetime.timedelta(seconds=1))
                    )
                    filled.append(
                        cls._make_zero_stat(next_time - datetime.timedelta(seconds=1))
                    )

        # Add zero at end of range if data ends earlier
        if end_time and last_time and end_time - last_time > threshold:
            filled.append(
                cls._make_zero_stat(last_time + datetime.timedelta(seconds=1))
            )
            filled.append(cls._make_zero_stat(end_time))

        return filled

    @staticmethod
    def prepare_chart_datasets(
        stats: t.List[t.Dict[str, t.Any]], server_type: str = "minecraft-java"
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
