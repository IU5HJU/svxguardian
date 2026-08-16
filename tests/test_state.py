"""
NodeState tests.
"""

from src.core.state import NodeState


def test_node_state_accepts_basic_values() -> None:
    """
    NodeState must preserve assigned basic runtime values.
    """

    state = NodeState()

    state.callsign = "IR5UV"
    state.cpu_temp = 47.8

    assert state.callsign == "IR5UV"
    assert state.cpu_temp == 47.8
