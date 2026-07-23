"""
State Exporter

Converts NodeState into a serializable dictionary.
"""

from dataclasses import asdict

from state import NodeState


class StateExporter:
    """
    Export NodeState to Python dictionary.
    """

    @staticmethod
    def to_dict(state: NodeState) -> dict:

        data = asdict(state)

        #
        # datetime is not JSON serializable.
        #

        if state.last_update is not None:
            data["last_update"] = state.last_update.isoformat()

        return data
