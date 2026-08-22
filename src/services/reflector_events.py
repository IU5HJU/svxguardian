"""
Incremental SvxReflector event tracking.

Tracks runtime Reflector client and talker events without rescanning
the complete SvxLink logfile.

Only events observed after tracker initialization are considered.
Historical logfile lines are intentionally ignored because they cannot
reliably reconstruct the current connected-client state.
"""

from __future__ import annotations

import re
from pathlib import Path

from .logfile import DEFAULT_LOG_FILE, IncrementalLogReader


NODE_JOINED_RE = re.compile(
    r"ReflectorLogic:\s+Node joined:\s+(\S+)\s*$"
)

NODE_LEFT_RE = re.compile(
    r"ReflectorLogic:\s+Node left:\s+(\S+)\s*$"
)

TALKER_START_RE = re.compile(
    r"ReflectorLogic:\s+Talker start on TG #(\d+):\s+(\S+)\s*$"
)

TALKER_STOP_RE = re.compile(
    r"ReflectorLogic:\s+Talker stop on TG #(\d+):\s+(\S+)\s*$"
)


class ReflectorEventTracker:
    """
    Track live Reflector client and talker state.

    The tracker follows only newly appended logfile lines.

    Connected clients are reconstructed from Node joined / Node left
    events observed while SVX Guardian is running.

    The active talker is reconstructed from Talker start / Talker stop
    events.
    """

    def __init__(
        self,
        log_file: Path | str = DEFAULT_LOG_FILE,
    ) -> None:
        self.log_file = Path(log_file)

        self.reader = IncrementalLogReader(
            log_file=self.log_file,
            history_limit=1000,
            initial_lines=0,
        )

        self.connected_clients: list[str] = []

        self.transmitting = False
        self.transmitting_station = ""
        self.transmitting_tg: int | None = None

        self._last_event_id = 0

    def sync(self) -> None:
        """
        Process Reflector events appended since the previous sync.
        """

        entries = self.reader.get_entries(
            after_id=self._last_event_id
        )

        for entry in entries:
            event_id = int(entry["id"])
            line = str(entry["line"])

            self._process_line(line)

            self._last_event_id = max(
                self._last_event_id,
                event_id,
            )

    def _process_line(
        self,
        line: str,
    ) -> None:
        """
        Update runtime state from one SvxLink logfile line.
        """

        match = NODE_JOINED_RE.search(line)

        if match:
            callsign = match.group(1)

            if callsign not in self.connected_clients:
                self.connected_clients.append(callsign)

            return

        match = NODE_LEFT_RE.search(line)

        if match:
            callsign = match.group(1)

            if callsign in self.connected_clients:
                self.connected_clients.remove(callsign)

            if self.transmitting_station == callsign:
                self._clear_talker()

            return

        match = TALKER_START_RE.search(line)

        if match:
            self.transmitting = True
            self.transmitting_tg = int(
                match.group(1)
            )
            self.transmitting_station = match.group(2)

            return

        match = TALKER_STOP_RE.search(line)

        if match:
            callsign = match.group(2)

            if self.transmitting_station == callsign:
                self._clear_talker()

    def _clear_talker(self) -> None:
        """
        Clear the current Reflector talker state.
        """

        self.transmitting = False
        self.transmitting_station = ""
        self.transmitting_tg = None
