"""
SvxLink version detector.

Detects the installed SvxLink software version.
"""

from __future__ import annotations

import subprocess


class SvxLinkVersionDetector:
    """
    Detect the installed SvxLink version.

    Version detection is intended for static node information and
    should therefore be executed only when node information is loaded,
    not during regular monitoring cycles.
    """

    def __init__(
        self,
        command: str = "svxlink",
        timeout: float = 2.0,
    ) -> None:
        self.command = command
        self.timeout = timeout

    def detect(self) -> str:
        """
        Return the installed SvxLink version or an empty string.
        """

        try:
            result = subprocess.run(
                [
                    self.command,
                    "--version",
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )
        except (
            OSError,
            subprocess.SubprocessError,
        ):
            return ""

        output = (
            result.stdout.strip()
            or result.stderr.strip()
        )

        if result.returncode != 0 or not output:
            return ""

        return output.splitlines()[0].strip()
