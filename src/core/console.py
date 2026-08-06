"""
SVX Guardian console renderer.

Provides formatted console output for the current node state.
"""

from typing import Any

from .config import ConfigManager
from .status import (
    HealthStatus,
    ServiceStatus,
)


class ConsoleRenderer:
    """
    Render the SVX Guardian node state in the terminal.
    """

    SEPARATOR_LENGTH = 60

    def __init__(self) -> None:
        self.config = ConfigManager()

    def show(self, state: Any, monitor_count: int) -> None:

        print(f"Hostname      : {state.hostname}")
        print(f"CPU Temp      : {state.cpu_temp:.1f} °C")
        print(f"CPU Usage     : {state.cpu_usage:.1f} %")
        print(f"RAM Usage     : {state.ram_usage:.1f} %")
        print(f"Disk Usage    : {state.disk_usage:.1f} %")
        print(f"Uptime        : {state.uptime}")

        print("-" * self.SEPARATOR_LENGTH)

        print(
            f"SvxLink       : {state.svxlink_status.value}"
        )

        if state.svxlink_status is ServiceStatus.RUNNING:
            print(f"PID           : {state.svxlink_pid}")
            print(f"Service Up    : {state.svxlink_uptime}")

        print(
            f"Health        : {state.health.value}"
            if isinstance(state.health, HealthStatus)
            else f"Health        : {state.health}"
        )

        print(f"Reason        : {state.health_reason}")

        print("-" * self.SEPARATOR_LENGTH)

        print(f"Monitors      : {monitor_count}")
        print(f"{self.config.application.name} ready.")
