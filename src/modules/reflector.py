"""
Reflector monitor.

Reads the SvxLink log and reconstructs the current Reflector
connection state, encryption, connected nodes and talk group.
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

    CONNECTED_NODES_PATTERN = re.compile(
        r"ReflectorLogic: Connected nodes:\s*(?P<nodes>.*)"
    )

    TALKER_PATTERN = re.compile(
        r"ReflectorLogic: Talker "
        r"(?:start|stop) on TG #(?P<talkgroup>\d+): "
        r"(?P<station>[A-Za-z0-9/._-]+)"
    )

    ENCRYPTED_MESSAGE = (
        "ReflectorLogic: Encrypted connection established"
    )

    def check(self, state: NodeState) -> None:
        """
        Update the current Reflector state.
        """

        state.reflector_status = ReflectorStatus.UNKNOWN
        state.reflector_host = ""
        state.reflector_port = 0
        state.reflector_tg = 0
        state.reflector_encrypted = False
        state.reflector_connected_nodes = []
        state.reflector_connection_count = 0
        state.reflector_last_error = ""
        state.reflector_last_disconnect_reason = ""

        connection_state_found = False
        previous_disconnect_found = False

        for line in self._read_lines_reverse():
            if state.reflector_tg == 0:
                talkgroup = self._extract_talkgroup(line)

                if talkgroup is not None:
                    state.reflector_tg = talkgroup

            if not state.reflector_connected_nodes:
                connected_nodes = self._extract_connected_nodes(
                    line
                )

                if connected_nodes is not None:
                    state.reflector_connected_nodes = connected_nodes
                    state.reflector_connection_count = len(
                        connected_nodes
                    )

            if self.ENCRYPTED_MESSAGE in line:
                state.reflector_encrypted = True

            disconnect = self.DISCONNECTED_PATTERN.search(line)

            if disconnect:
                reason = disconnect.group("reason").strip()

                if not connection_state_found:
                    state.reflector_status = (
                        ReflectorStatus.DISCONNECTED
                    )
                    state.reflector_host = disconnect.group("host")
                    state.reflector_port = int(
                        disconnect.group("port")
                    )
                    state.reflector_last_disconnect_reason = reason
                    connection_state_found = True
                    previous_disconnect_found = True
                    break

                if not previous_disconnect_found:
                    state.reflector_last_disconnect_reason = reason
                    previous_disconnect_found = True
                    break

            connected = self.CONNECTED_PATTERN.search(line)

            if connected and not connection_state_found:
                state.reflector_status = ReflectorStatus.CONNECTED
                state.reflector_host = connected.group("host")
                state.reflector_port = int(
                    connected.group("port")
                )
                connection_state_found = True
                continue

            if (
                self.CONNECTING_PATTERN.search(line)
                and not connection_state_found
            ):
                state.reflector_status = ReflectorStatus.CONNECTING
                connection_state_found = True
                break

    @staticmethod
    def _extract_connected_nodes(
        line: str,
    ) -> list[str] | None:
        """
        Extract connected Reflector nodes from a log line.
        """

        match = ReflectorMonitor.CONNECTED_NODES_PATTERN.search(
            line
        )

        if match is None:
            return None

        raw_nodes = match.group("nodes").strip()

        if not raw_nodes:
            return []

        return sorted(
            {
                node.strip().upper()
                for node in raw_nodes.split(",")
                if node.strip()
            }
        )

    @staticmethod
    def _extract_talkgroup(
        line: str,
    ) -> int | None:
        """
        Extract the Talk Group number from a talker event.
        """

        match = ReflectorMonitor.TALKER_PATTERN.search(line)

        if match is None:
            return None

        try:
            return int(match.group("talkgroup"))
        except ValueError:
            return None

    def _read_lines_reverse(self) -> Iterator[str]:
        """
        Read the SvxLink log backwards, one line at a time.
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
