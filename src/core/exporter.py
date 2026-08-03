"""
State Exporter

Converts NodeState into serializable data.
"""

from dataclasses import asdict

from .state import NodeState


class StateExporter:
    """
    Exports NodeState to a Python dictionary.
    """

    @staticmethod
    def to_dict(state: NodeState) -> dict:
        """
        Convert NodeState into a serializable dictionary.
        """

        data = asdict(state)

        if state.last_update is not None:
            data["last_update"] = state.last_update.isoformat()

        return data
