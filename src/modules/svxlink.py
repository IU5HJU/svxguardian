"""
SvxLink Monitor

Checks the status, process ID and uptime of the SvxLink service.
"""

import subprocess
import time

from ..core.state import NodeState
from .base import BaseMonitor


class SvxLinkMonitor(BaseMonitor):
    """
    Monitor responsible for checking the SvxLink service.
    """

    SERVICE_NAME = "svxlink.service"
    COMMAND_TIMEOUT = 5

    def check(self, state: NodeState) -> None:
        """
        Update the SvxLink service state, PID and uptime.
        """

        state.svxlink_running = False
        state.svxlink_pid = 0
        state.svxlink_uptime = ""

        try:
            result = subprocess.run(
                [
                    "systemctl",
                    "show",
                    self.SERVICE_NAME,
                    "--property=ActiveState",
                    "--property=MainPID",
                    "--property=ActiveEnterTimestampMonotonic",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=self.COMMAND_TIMEOUT,
            )

            if result.returncode != 0:
                return

            properties = self._parse_properties(result.stdout)

            state.svxlink_running = (
                properties.get("ActiveState") == "active"
            )

            if not state.svxlink_running:
                return

            state.svxlink_pid = self._parse_pid(
                properties.get("MainPID", "")
            )

            state.svxlink_uptime = self._calculate_uptime(
                properties.get(
                    "ActiveEnterTimestampMonotonic",
                    "",
                )
            )

        except (
            FileNotFoundError,
            subprocess.SubprocessError,
            OSError,
            ValueError,
        ):
            state.svxlink_running = False
            state.svxlink_pid = 0
            state.svxlink_uptime = ""

    @staticmethod
    def _parse_properties(output: str) -> dict[str, str]:
        """
        Convert systemctl property output into a dictionary.
        """

        properties: dict[str, str] = {}

        for line in output.splitlines():
            key, separator, value = line.partition("=")

            if separator:
                properties[key.strip()] = value.strip()

        return properties

    @staticmethod
    def _parse_pid(value: str) -> int:
        """
        Convert the systemd MainPID value into an integer.
        """

        try:
            pid = int(value)
        except ValueError:
            return 0

        return pid if pid > 0 else 0

    @staticmethod
    def _calculate_uptime(
        active_timestamp_microseconds: str,
    ) -> str:
        """
        Calculate service uptime from the systemd monotonic timestamp.
        """

        try:
            active_seconds = (
                int(active_timestamp_microseconds) / 1_000_000
            )
        except ValueError:
            return ""

        current_seconds = time.clock_gettime(time.CLOCK_BOOTTIME)
        uptime_seconds = max(
            0,
            int(current_seconds - active_seconds),
        )

        days, remainder = divmod(uptime_seconds, 86_400)
        hours, remainder = divmod(remainder, 3_600)
        minutes, seconds = divmod(remainder, 60)

        if days:
            return f"{days}d {hours}h {minutes}m"

        if hours:
            return f"{hours}h {minutes}m {seconds}s"

        if minutes:
            return f"{minutes}m {seconds}s"

        return f"{seconds}s"
