"""
SVX Guardian Engine.

Core orchestration engine for all monitors.
"""

from datetime import datetime

from state import NodeState


class Guardian:
    """
    Main Guardian engine.

    Responsibilities:
    - maintain the current NodeState;
    - register monitors;
    - execute all registered monitors.
    """

    def __init__(self) -> None:
        self.state = NodeState()
        self.monitors = []

    def register(self, monitor) -> None:
        """
        Register a monitor.
        """
        self.monitors.append(monitor)

    def run(self) -> None:
        """
        Execute all registered monitors.
        """

        self.state.last_update = datetime.now()

        for monitor in self.monitors:
            monitor.check(self.state)
