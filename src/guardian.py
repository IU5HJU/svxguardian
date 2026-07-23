"""
SVX Guardian Engine.
"""

from datetime import datetime

from health import HealthEngine
from state import NodeState


class Guardian:
    """
    Main Guardian engine.
    """

    def __init__(self):
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
        Execute every registered monitor and evaluate system health.
        """

        self.state.last_update = datetime.now()

        # Execute all monitors
        for monitor in self.monitors:
            monitor.check(self.state)

        # Evaluate overall health
        self.health_engine.evaluate(self.state)
