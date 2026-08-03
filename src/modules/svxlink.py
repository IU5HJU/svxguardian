"""
SvxLink Monitor

Checks the status of the SvxLink service.
"""

import subprocess

from ..core.state import NodeState
from .base import BaseMonitor


class SvxLinkMonitor(BaseMonitor):
    """
    Monitor responsible for checking the SvxLink service.
    """

    def check(self, state: NodeState) -> None:
        """
        Update the SvxLink service status.
        """

        try:
            result = subprocess.run(
                [
                    "systemctl",
                    "is-active",
                    "svxlink.service",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )

            state.svxlink_running = (
                result.returncode == 0
                and result.stdout.strip() == "active"
            )

        except (
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            state.svxlink_running = False
