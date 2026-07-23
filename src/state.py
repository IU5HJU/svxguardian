from dataclasses import dataclass
from datetime import datetime


@dataclass
class NodeState:
    """
    Stato corrente del nodo SvxLink.
    """

    # Informazioni generali
    hostname: str = ""
    callsign: str = ""
    last_update: datetime | None = None

    # Stato globale del sistema
    health: str = "UNKNOWN"
    health_reason: str = ""

    # Sistema
    cpu_temp: float = 0.0
    cpu_usage: float = 0.0
    ram_usage: float = 0.0
    disk_usage: float = 0.0
    uptime: str = ""

    # SvxLink
    svxlink_running: bool = False

    # EchoLink
    echolink_registered: bool = False

    # Reflector
    reflector_connected: bool = False
    reflector_host: str = ""
    reflector_tg: int = 0
