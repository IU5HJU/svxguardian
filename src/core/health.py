"""
Health Engine

Evaluates the overall health of the node.
"""

from .state import NodeState


class HealthEngine:
    """
    Evaluates the global health of the node.
    """

    def evaluate(self, state: NodeState) -> None:
        """
        Evaluate the current node health.
        """

        state.health = "HEALTHY"
        state.health_reason = "REASON_NONE"

        if state.cpu_temp >= 80:
            state.health = "CRITICAL"
            state.health_reason = "REASON_CPU_TEMP_CRITICAL"
            return

        if state.cpu_temp >= 70:
            state.health = "WARNING"
            state.health_reason = "REASON_CPU_TEMP_HIGH"
            return

        if not state.svxlink_running:
            state.health = "CRITICAL"
            state.health_reason = "REASON_SVXLINK_STOPPED"
