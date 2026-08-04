"""
SVX Guardian Engine.

Coordinates monitors, loads node information,
and evaluates the overall node health.
"""

from datetime import datetime

from ..modules.configreader import ConfigReader
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
        self.config_reader = ConfigReader()

        self.load_node_info()

    def register(self, monitor) -> None:
        """
        Register a monitor.
        """

        self.monitors.append(monitor)

    def load_node_info(self) -> None:
        """
        Load the static SvxLink node information.
        """

        self.node_info = self.config_reader.load()

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
