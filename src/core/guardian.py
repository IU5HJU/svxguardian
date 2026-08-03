"""
SVX Guardian Engine.

Coordinates monitors and evaluates the overall node health.
"""

from datetime import datetime

from .health import HealthEngine
from .state import NodeState


class Guardian:
    """
    Main SVX Guardian engine.
    """

    def __init__(self) -> None:
        self.state = NodeState()
        self.monitors = []
        self.health_engine = HealthEngine()

    def register(self, monitor) -> None:
        """
        Register a monitor.
        """

        self.monitors.append(monitor)

    def run(self) -> None:
        """
        Execute all registered monitors and evaluate node health.
        """

        self.state.last_update = datetime.now()

        for monitor in self.monitors:
            monitor.check(self.state)

        self.health_engine.evaluate(self.state)
