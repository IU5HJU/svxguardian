"""
SVX Guardian Engine.

Coordinates monitors, loads node information,
and evaluates the overall node health.
"""

from datetime import datetime

from ..modules.configreader import ConfigReader
from ..modules.nodeinforeader import NodeInfoReader
from ..modules.svxlinkversion import SvxLinkVersionDetector
from .config import ConfigManager
from .health import HealthEngine
from .nodeinfo import NodeInfo
from .state import NodeState


class Guardian:
    """
    Main SVX Guardian engine.
    """

    def __init__(self) -> None:
        self.state = NodeState()
        self.node_info = NodeInfo()

        self.monitors = []

        self.health_engine = HealthEngine()
        self.config = ConfigManager()

        self.config_reader = ConfigReader(
            self.config.SVXLINK_CONFIG_FILE
        )

        self.svxlink_version_detector = (
            SvxLinkVersionDetector()
        )

        self.load_node_info()

    def register(self, monitor) -> None:
        """
        Register a monitor.
        """

        self.monitors.append(monitor)

    def load_node_info(self) -> None:
        """
        Load static SvxLink node information.

        The main SvxLink configuration is always read first.

        node_info.json is read only when the active ReflectorLogic
        explicitly declares NODE_INFO_FILE. This prevents SVX Guardian
        from treating the upstream example node_info.json template as
        real node information.

        The installed SvxLink version is detected once while loading
        static node information and is not queried during normal
        monitoring cycles.
        """

        node = self.config_reader.load()

        if node.node_info_file:
            node_info_reader = NodeInfoReader(
                node.node_info_file
            )

            node = node_info_reader.enrich(node)

        node.svxlink_version = (
            self.svxlink_version_detector.detect()
        )

        self.node_info = node

        if self.node_info.callsign:
            self.state.callsign = self.node_info.callsign

    def run(self) -> None:
        """
        Execute all registered monitors and evaluate node health.
        """

        self.state.last_update = datetime.now()

        for monitor in self.monitors:
            monitor.check(self.state)

        if self.node_info.callsign:
            self.state.callsign = self.node_info.callsign

        self.health_engine.evaluate(self.state)
