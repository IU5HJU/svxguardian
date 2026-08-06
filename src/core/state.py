"""
SVX Guardian node state.

Defines the current dynamic state of the monitored node.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class NodeState:
    """
    Current state of the SvxLink node.
    """

    # General information
    hostname: str = ""
    callsign: str = ""
    last_update: datetime | None = None

    # Overall system health
    health: str = "UNKNOWN"
    health_reason: str = ""

    # Operating system
    cpu_temp: float = 0.0
    cpu_usage: float = 0.0
    ram_usage: float = 0.0
    disk_usage: float = 0.0
    uptime: str = ""

    # SvxLink
    svxlink_running: bool = False
    svxlink_pid: int = 0
    svxlink_uptime: str = ""

    # EchoLink
    echolink_registered: bool = False

    # Reflector
    reflector_connected: bool = False
    reflector_host: str = ""
    reflector_tg: int = 0
