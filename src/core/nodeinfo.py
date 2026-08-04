"""
Node information model.

Stores the static identity and configuration data of the SvxLink node.
"""

from dataclasses import dataclass, field


@dataclass
class NodeInfo:
    """
    Static information describing the SvxLink node.
    """

    callsign: str = ""
    description: str = ""
    qth: str = ""
    locator: str = ""

    rx_frequency: str = ""
    tx_frequency: str = ""
    ctcss: str = ""

    echolink_number: str = ""
    reflector: str = ""

    modules: list[str] = field(default_factory=list)

    svxlink_version: str = ""
    config_file: str = ""
