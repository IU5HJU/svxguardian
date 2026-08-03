"""
System Monitor

Collects information about the Raspberry Pi operating system.
"""

import socket
from pathlib import Path

import psutil

from ..core.state import NodeState
from .base import BaseMonitor


class SystemMonitor(BaseMonitor):
    """
    Collects system information and updates NodeState.
    """

    def check(self, state: NodeState) -> None:
        """
        Update the current system status.
        """

        state.hostname = socket.gethostname()

        state.cpu_usage = psutil.cpu_percent(interval=0.2)

        state.ram_usage = psutil.virtual_memory().percent

        state.disk_usage = psutil.disk_usage("/").percent

        thermal_file = Path(
            "/sys/class/thermal/thermal_zone0/temp"
        )

        if thermal_file.exists():
            temperature = thermal_file.read_text(
                encoding="utf-8"
            ).strip()

            state.cpu_temp = int(temperature) / 1000
        else:
            state.cpu_temp = 0.0

        uptime_file = Path("/proc/uptime")

        if uptime_file.exists():
            uptime_data = uptime_file.read_text(
                encoding="utf-8"
            ).split()

            uptime_seconds = int(float(uptime_data[0]))
        else:
            uptime_seconds = 0

        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60

        if days > 0:
            state.uptime = f"{days}d {hours}h {minutes}m"
        else:
            state.uptime = f"{hours}h {minutes}m"
