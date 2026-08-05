"""
SVX Guardian console renderer.

Provides formatted console output for the current node state.
"""

from typing import Any


class ConsoleRenderer:
    """
    Render the SVX Guardian node state in the terminal.
    """

    SEPARATOR_LENGTH = 60

    def show(self, state: Any, monitor_count: int) -> None:
        """
        Display the current node state.

        Args:
            state: Current SVX Guardian node state.
            monitor_count: Number of registered monitors.
        """

        print(f"Hostname      : {state.hostname}")
        print(f"CPU Temp      : {state.cpu_temp:.1f} °C")
        print(f"CPU Usage     : {state.cpu_usage:.1f} %")
        print(f"RAM Usage     : {state.ram_usage:.1f} %")
        print(f"Disk Usage    : {state.disk_usage:.1f} %")
        print(f"Uptime        : {state.uptime}")

        print("-" * self.SEPARATOR_LENGTH)

        print(
            "SvxLink       : "
            f"{'RUNNING' if state.svxlink_running else 'STOPPED'}"
        )

        print(f"Health        : {state.health}")
        print(f"Reason        : {state.health_reason}")

        print("-" * self.SEPARATOR_LENGTH)

        print(f"Monitors      : {monitor_count}")
        print("SVX Guardian ready.")
