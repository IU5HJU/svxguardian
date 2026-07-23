"""
SvxLink Monitor

Checks the status of the SvxLink service.
"""

import subprocess

from modules.base import BaseMonitor
from state import NodeState


class SvxLinkMonitor(BaseMonitor):
    """
    Monitor responsible for checking the SvxLink service.
    """

    def check(self, state: NodeState) -> None:
        """
        Update SvxLink status.
        """

        try:
            result = subprocess.run(
                ["systemctl", "is-active", "svxlink"],
                capture_output=True,
                text=True,
                check=False,
            )

            state.svxlink_running = (
                result.stdout.strip() == "active"
            )

        except Exception:
            state.svxlink_running = False
