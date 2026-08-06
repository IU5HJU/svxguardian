"""
SVX Guardian health engine.

Evaluates the overall health of the monitored node.
"""

from .state import NodeState
from .status import HealthStatus, ServiceStatus


class HealthEngine:
    """
    Evaluate the overall health of the node.
    """

    def evaluate(self, state: NodeState) -> None:
        """
        Evaluate the current node health.
        """

        state.health = HealthStatus.HEALTHY
        state.health_reason = "REASON_NONE"

        if state.cpu_temp >= 80:
            state.health = HealthStatus.CRITICAL
            state.health_reason = "REASON_CPU_TEMP_CRITICAL"
            return

        if state.cpu_temp >= 70:
            state.health = HealthStatus.WARNING
            state.health_reason = "REASON_CPU_TEMP_HIGH"
            return

        if state.svxlink_status is not ServiceStatus.RUNNING:
            state.health = HealthStatus.CRITICAL
            state.health_reason = "REASON_SVXLINK_STOPPED"
