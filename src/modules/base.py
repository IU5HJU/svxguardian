"""
Base class for all SVX Guardian monitors.
"""

from abc import ABC, abstractmethod
from state import NodeState


class BaseMonitor(ABC):
    """
    Abstract base class for every monitor.
    """

    @abstractmethod
    def check(self, state: NodeState) -> None:
        """
        Update the current node state.
        """
        pass
