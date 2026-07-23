"""
Health Engine

Evaluates the overall health of the node.
"""

from state import NodeState


class HealthEngine:
    """
    Evaluates the global health of the node.
    """

    def evaluate(self, state: NodeState) -> None:

        # Default state
        state.health = "HEALTHY"

        #
        # CPU Temperature
        #

        if state.cpu_temp >= 80:
            state.health = "CRITICAL"
            return

        if state.cpu_temp >= 70:
            state.health = "WARNING"
            return

        #
        # SvxLink
        #

        if not state.svxlink_running:
            state.health = "CRITICAL"
            return
