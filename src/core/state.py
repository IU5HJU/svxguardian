"""
SVX Guardian node state.

Defines the current dynamic state of the monitored node.
"""

from dataclasses import dataclass, field
from datetime import datetime

from .status import (
    EchoLinkStatus,
    HealthStatus,
    ReflectorStatus,
    ServiceStatus,
)


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
    health: HealthStatus = HealthStatus.UNKNOWN
    health_reason: str = ""

    # Operating system
    cpu_temp: float = 0.0
    cpu_usage: float = 0.0
    ram_usage: float = 0.0
    disk_usage: float = 0.0
    uptime: str = ""

    # SvxLink
    svxlink_status: ServiceStatus = ServiceStatus.UNKNOWN
    svxlink_pid: int = 0
    svxlink_uptime: str = ""

    # EchoLink
    echolink_status: EchoLinkStatus = EchoLinkStatus.UNKNOWN
    echolink_last_error: str = ""

    echolink_connected_stations: list[str] = field(
        default_factory=list
    )

    echolink_station_names: dict[str, str] = field(
        default_factory=dict
    )

    echolink_connection_started: dict[str, str] = field(
        default_factory=dict
    )

    echolink_unstable_stations: list[str] = field(
        default_factory=list
    )

    echolink_connection_count: int = 0

    echolink_transmitting: bool = False
    echolink_transmitting_station: str = ""

    echolink_recent_connections: list[
        dict[str, object]
    ] = field(
        default_factory=list
    )

    # Reflector
    reflector_status: ReflectorStatus = ReflectorStatus.UNKNOWN
    reflector_host: str = ""
    reflector_port: int = 0
    reflector_tg: int = 0
    reflector_encrypted: bool = False

    reflector_connected_nodes: list[str] = field(
        default_factory=list
    )

    reflector_connected_clients: list[str] = field(
        default_factory=list
    )

    reflector_connection_count: int = 0

    reflector_transmitting: bool = False
    reflector_transmitting_station: str = ""

    reflector_last_error: str = ""
    reflector_last_disconnect_reason: str = ""

    @property
    def svxlink_running(self) -> bool:
        """
        Return whether the SvxLink service is running.
        """

        return self.svxlink_status is ServiceStatus.RUNNING

    @property
    def echolink_registered(self) -> bool:
        """
        Return whether EchoLink is registered with the directory.
        """

        return self.echolink_status is EchoLinkStatus.ONLINE

    @property
    def reflector_connected(self) -> bool:
        """
        Return whether the Reflector connection is established.
        """

        return self.reflector_status is ReflectorStatus.CONNECTED
