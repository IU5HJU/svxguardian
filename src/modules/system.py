"""
System Monitor

Collects information about the Raspberry Pi operating system.
"""

import socket
from pathlib import Path

import psutil

from modules.base import BaseMonitor
from state import NodeState


class SystemMonitor(BaseMonitor):
    """
    Collects system information and updates NodeState.
    """

    def check(self, state: NodeState) -> None:
        """
        Update the current system status.
        """

        # Hostname
        state.hostname = socket.gethostname()

        # CPU usage
        state.cpu_usage = psutil.cpu_percent(interval=0.2)

        # RAM usage
        state.ram_usage = psutil.virtual_memory().percent

        # Disk usage
        state.disk_usage = psutil.disk_usage("/").percent

        # CPU temperature
        thermal = Path("/sys/class/thermal/thermal_zone0/temp")

        if thermal.exists():
            state.cpu_temp = int(thermal.read_text().strip()) / 1000
        else:
            state.cpu_temp = 0.0

        # System uptime
        uptime_file = Path("/proc/uptime")

        if uptime_file.exists():
            uptime_seconds = int(float(uptime_file.read_text().split()[0]))
        else:
            uptime_seconds = 0

        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60

        if days > 0:
            state.uptime = f"{days}d {hours}h {minutes}m"
        else:
            state.uptime = f"{hours}h {minutes}m"
