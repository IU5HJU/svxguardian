"""
SvxLink service monitor.

Reads language-independent systemd properties and updates
the current SvxLink service state.
"""

import subprocess
import time

from ..core.state import NodeState
from ..core.status import ServiceStatus
from .base import BaseMonitor


class SvxLinkMonitor(BaseMonitor):
    """
    Monitor the SvxLink systemd service.
    """

    SERVICE_NAME = "svxlink.service"
    COMMAND_TIMEOUT = 5

    def check(self, state: NodeState) -> None:
        """
        Update SvxLink status, process ID and service uptime.
        """

        state.svxlink_status = ServiceStatus.UNKNOWN
        state.svxlink_pid = 0
        state.svxlink_uptime = ""

        try:
            result = subprocess.run(
                [
                    "systemctl",
                    "show",
                    self.SERVICE_NAME,
                    "--property=ActiveState",
                    "--property=SubState",
                    "--property=MainPID",
                    "--property=ActiveEnterTimestampMonotonic",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=self.COMMAND_TIMEOUT,
            )
        except FileNotFoundError:
            state.svxlink_status = ServiceStatus.ERROR
            return
        except (
            subprocess.SubprocessError,
            OSError,
        ):
            state.svxlink_status = ServiceStatus.ERROR
            return

        if result.returncode != 0:
            state.svxlink_status = ServiceStatus.ERROR
            return

        properties = self._parse_properties(result.stdout)

        active_state = properties.get(
            "ActiveState",
            "",
        ).lower()

        sub_state = properties.get(
            "SubState",
            "",
        ).lower()

        state.svxlink_status = self._map_service_status(
            active_state,
            sub_state,
        )

        if state.svxlink_status is not ServiceStatus.RUNNING:
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
    def _map_service_status(
        active_state: str,
        sub_state: str,
    ) -> ServiceStatus:
        """
        Convert systemd states into an internal service status.
        """

        if active_state == "active":
            return ServiceStatus.RUNNING

        if active_state == "activating":
            return ServiceStatus.STARTING

        if active_state == "deactivating":
            return ServiceStatus.STOPPING

        if active_state == "inactive":
            return ServiceStatus.STOPPED

        if active_state == "failed" or sub_state == "failed":
            return ServiceStatus.ERROR

        return ServiceStatus.UNKNOWN

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
        Calculate uptime from the systemd monotonic timestamp.
        """

        try:
            active_seconds = (
                int(active_timestamp_microseconds) / 1_000_000
            )
        except ValueError:
            return ""

        current_seconds = time.clock_gettime(
            time.CLOCK_BOOTTIME
        )

        uptime_seconds = max(
            0,
            int(current_seconds - active_seconds),
        )

        days, remainder = divmod(
            uptime_seconds,
            86_400,
        )

        hours, remainder = divmod(
            remainder,
            3_600,
        )

        minutes, seconds = divmod(
            remainder,
            60,
        )

        if days:
            return f"{days}d {hours}h {minutes}m"

        if hours:
            return f"{hours}h {minutes}m {seconds}s"

        if minutes:
            return f"{minutes}m {seconds}s"

        return f"{seconds}s"
