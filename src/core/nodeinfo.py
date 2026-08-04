"""
Node information model.

Stores the static identity and configuration data
of the SvxLink node.
"""

from dataclasses import dataclass, field


@dataclass
class NodeInfo:
    """
    Static information describing the SvxLink installation.

    This model contains declared configuration data.
    Dynamic service states belong in NodeState.
    """

    # ---------------------------------------------------------
    # Node identity
    # ---------------------------------------------------------

    callsign: str = ""
    description: str = ""
    node_location: str = ""
    node_class: str = ""
    hidden: bool = False
    sysop: str = ""

    # ---------------------------------------------------------
    # Geographic information
    # ---------------------------------------------------------

    qth: str = ""
    locator: str = ""

    latitude: float | None = None
    longitude: float | None = None

    # ---------------------------------------------------------
    # Receiver configuration
    # ---------------------------------------------------------

    rx_name: str = ""
    rx_frequency: str = ""
    rx_sql_type: str = ""

    rx_ctcss_frequencies: list[str] = field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Transmitter configuration
    # ---------------------------------------------------------

    tx_name: str = ""
    tx_frequency: str = ""
    tx_power: str = ""
    tx_ctcss_frequency: str = ""

    ctcss: str = ""

    # ---------------------------------------------------------
    # EchoLink configuration
    # ---------------------------------------------------------

    echolink_number: str = ""

    # ---------------------------------------------------------
    # Reflector configuration
    # ---------------------------------------------------------

    reflector_configured: bool = False

    reflector_hosts: list[str] = field(
        default_factory=list
    )

    reflector_port: int | None = None
    reflector_default_tg: int | None = None

    reflector_mode: str = "disabled"
    reflector_logic_name: str = ""

    # Temporary human-readable representation.
    # It remains available while the dashboard is migrated
    # to the structured Reflector fields.
    reflector: str = ""

    # ---------------------------------------------------------
    # SvxLink modules and logic
    # ---------------------------------------------------------

    logics: list[str] = field(
        default_factory=list
    )

    modules: list[str] = field(
        default_factory=list
    )

    tone_to_talkgroup: dict[str, int] = field(
        default_factory=dict
    )

    # ---------------------------------------------------------
    # Software information
    # ---------------------------------------------------------

    svxlink_version: str = ""

    # ---------------------------------------------------------
    # Source files
    # ---------------------------------------------------------

    config_file: str = ""
    node_info_file: str = ""
