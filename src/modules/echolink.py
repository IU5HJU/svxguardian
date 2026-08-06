"""
EchoLink monitor.

Reads the SvxLink log and determines the latest EchoLink
directory registration status and active station connections.
"""

from collections.abc import Iterator
from pathlib import Path
import re

from ..core.state import NodeState
from ..core.status import EchoLinkStatus
from .base import BaseMonitor


class EchoLinkMonitor(BaseMonitor):
    """
    Monitor EchoLink directory registration and active stations.
    """

    LOG_FILE = Path("/var/log/svxlink")
    READ_BLOCK_SIZE = 8192

    DIRECTORY_STATUS_PREFIX = (
        "EchoLink directory status changed to "
    )

    MODULE_START_MESSAGE = (
        "Module EchoLink"
    )

    CONNECTION_PATTERN = re.compile(
        r"(?P<station>[A-Za-z0-9/._-]+): "
        r"EchoLink QSO state changed to "
        r"(?P<status>CONNECTED|DISCONNECTED)"
    )

    DNS_ERROR_MESSAGES = (
        "EchoLink directory server DNS lookup failed",
        "No IP addresses were returned for the EchoLink "
        "directory server DNS query",
        'Could not look up host "servers.echolink.org"',
    )

    def check(self, state: NodeState) -> None:
        """
        Update EchoLink directory and connection information.
        """

        state.echolink_status = EchoLinkStatus.UNKNOWN
        state.echolink_last_error = ""
        state.echolink_connected_stations = []
        state.echolink_connection_count = 0

        self._update_directory_status(state)
        self._update_connected_stations(state)

    def _update_directory_status(
        self,
        state: NodeState,
    ) -> None:
        """
        Update the EchoLink directory registration status.
        """

        for line in self._read_lines_reverse():
            if self._is_dns_error(line):
                state.echolink_status = EchoLinkStatus.DNS_ERROR
                state.echolink_last_error = (
                    "REASON_ECHOLINK_DNS_ERROR"
                )
                return

            directory_status = self._extract_directory_status(
                line
            )

            if directory_status is None:
                continue

            state.echolink_status = self._map_directory_status(
                directory_status
            )

            if state.echolink_status is EchoLinkStatus.ERROR:
                state.echolink_last_error = (
                    "REASON_ECHOLINK_DIRECTORY_ERROR"
                )

            return

    def _update_connected_stations(
        self,
        state: NodeState,
    ) -> None:
        """
        Reconstruct currently connected EchoLink stations.
        """

        station_states: dict[str, bool] = {}

        for line in self._read_lines_reverse():
            if self._is_module_start(line):
                break

            connection_event = self._extract_connection_event(
                line
            )

            if connection_event is None:
                continue

            station, connected = connection_event

            if station in station_states:
                continue

            station_states[station] = connected

        connected_stations = sorted(
            station
            for station, connected in station_states.items()
            if connected
        )

        state.echolink_connected_stations = connected_stations
        state.echolink_connection_count = len(
            connected_stations
        )

    def _read_lines_reverse(self) -> Iterator[str]:
        """
        Read the SvxLink log backwards, one line at a time.

        Binary reading is used because some SvxLink logs may contain
        bytes that cause text tools to classify the file as binary.
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

    def _is_dns_error(self, line: str) -> bool:
        """
        Return whether a log line reports an EchoLink DNS error.
        """

        return any(
            message in line
            for message in self.DNS_ERROR_MESSAGES
        )

    def _is_module_start(self, line: str) -> bool:
        """
        Return whether the line marks an EchoLink module start.
        """

        return (
            self.MODULE_START_MESSAGE in line
            and "starting" in line.lower()
        )

    def _extract_directory_status(
        self,
        line: str,
    ) -> str | None:
        """
        Extract the raw EchoLink directory status from a log line.
        """

        if self.DIRECTORY_STATUS_PREFIX not in line:
            return None

        _, _, status = line.partition(
            self.DIRECTORY_STATUS_PREFIX
        )

        normalized_status = status.strip().upper()

        return normalized_status or None

    def _extract_connection_event(
        self,
        line: str,
    ) -> tuple[str, bool] | None:
        """
        Extract a station connection event from a log line.
        """

        match = self.CONNECTION_PATTERN.search(line)

        if match is None:
            return None

        station = match.group("station").upper()
        connection_status = match.group("status")

        return (
            station,
            connection_status == "CONNECTED",
        )

    @staticmethod
    def _map_directory_status(
        directory_status: str,
    ) -> EchoLinkStatus:
        """
        Convert a SvxLink directory status into an internal status.
        """

        if directory_status == "ON":
            return EchoLinkStatus.ONLINE

        if directory_status == "OFF":
            return EchoLinkStatus.OFFLINE

        if directory_status == "?":
            return EchoLinkStatus.ERROR

        return EchoLinkStatus.UNKNOWN
