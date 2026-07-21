"""
Stato del nodo monitorato da SVX Guardian.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class NodeState:
    """
    Contiene lo stato completo del nodo.
    """

    # Servizi
    svxlink_online: bool = False
    reflector_online: bool = False
    echolink_online: bool = False

    # Sistema
    cpu_temp: float = 0.0
    cpu_usage: float = 0.0
    ram_usage: float = 0.0
    disk_usage: float = 0.0

    # Aggiornamento
    last_update: datetime | None = None
