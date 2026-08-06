"""
Reflector monitor.

Reads the SvxLink log and reconstructs the current Reflector
connection state.
"""

from collections.abc import Iterator
from pathlib import Path
import re

from ..core.state import NodeState
from ..core.status import ReflectorStatus
from .base import BaseMonitor


class ReflectorMonitor(BaseMonitor):
    """
    Monitor the SvxReflector connection.
    """

    LOG_FILE = Path("/var/log/svxlink")
    READ_BLOCK_SIZE = 8192

    CONNECTING_PATTERN = re.compile(
        r"ReflectorLogic: Connecting to service"
    )

    CONNECTED_PATTERN = re.compile(
        r"ReflectorLogic: Connection established to "
        r"(?P<host>[^:]+):(?P<port>\d+)"
    )

    DISCONNECTED_PATTERN = re.compile(
        r"ReflectorLogic: Disconnected from "
        r"(?P<host>[^:]+):(?P<port>\d+): "
        r"(?P<reason>.+)"
    )

    def check(self, state: NodeState) -> None:
        """
        Update the current Reflector connection state.
        """

        state.reflector_status = ReflectorStatus.UNKNOWN
        state.reflector_host = ""
        state.reflector_port = 0
        state.reflector_last_disconnect_reason = ""
        state.reflector_last_error = ""

        for line in self._read_lines_reverse():

            disconnect = self.DISCONNECTED_PATTERN.search(line)

            if disconnect:

                state.reflector_status = (
                    ReflectorStatus.DISCONNECTED
                )

                state.reflector_host = disconnect.group("host")

                state.reflector_port = int(
                    disconnect.group("port")
                )

                state.reflector_last_disconnect_reason = (
                    disconnect.group("reason").strip()
                )

                return

            connected = self.CONNECTED_PATTERN.search(line)

            if connected:

                state.reflector_status = (
                    ReflectorStatus.CONNECTED
                )

                state.reflector_host = connected.group("host")

                state.reflector_port = int(
                    connected.group("port")
                )

                return

            if self.CONNECTING_PATTERN.search(line):

                state.reflector_status = (
                    ReflectorStatus.CONNECTING
                )

                return

    def _read_lines_reverse(self) -> Iterator[str]:
        """
        Read the SvxLink log backwards.
        """

        if not self.LOG_FILE.is_file():
            return

        try:

            with self.LOG_FILE.open("rb") as log_file:

                log_file.seek(0, 2)

                position = log_file.tell()

                buffer = b""

                while position > 0:

                    block_size = min(
                        self.READ_BLOCK_SIZE,
                        position,
                    )

                    position -= block_size

                    log_file.seek(position)

                    block = log_file.read(block_size)

                    buffer = block + buffer

                    lines = buffer.split(b"\n")

                    buffer = lines[0]

                    for raw_line in reversed(lines[1:]):

                        yield raw_line.decode(
                            "utf-8",
                            errors="ignore",
                        )

                if buffer:

                    yield buffer.decode(
                        "utf-8",
                        errors="ignore",
                    )

        except OSError:
            return
