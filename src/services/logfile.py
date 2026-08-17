"""
SvxLink logfile services.

Provides both simple logfile access and an incremental,
thread-safe logfile stream suitable for the SVX Guardian
real-time operational log.

The incremental reader does not reread the complete SvxLink
logfile on every request.

It keeps track of:

- logfile inode;
- current byte offset;
- a small content anchor near the current offset;
- incomplete trailing lines;
- a bounded in-memory history;
- monotonically increasing event identifiers.

Log rotation, truncation and in-place logfile rewriting are
detected automatically.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path
from threading import RLock


DEFAULT_LOG_FILE = Path(
    "/var/log/svxlink"
)

DEFAULT_HISTORY_LIMIT = 1000
DEFAULT_INITIAL_LINES = 200

READ_BLOCK_SIZE = 8192
TRACKING_ANCHOR_SIZE = 128


def read_last_lines(
    lines: int = 100,
    log_file: Path | str = DEFAULT_LOG_FILE,
) -> list[str]:
    """
    Return the last lines from the SvxLink logfile.

    The file is read backwards in binary blocks so a large
    logfile is not loaded completely into memory.

    Compatibility note:

    Historically this function returned lines including their
    trailing newline character when present in the logfile.
    That behavior is intentionally preserved.
    """

    if lines <= 0:
        return []

    logfile = Path(
        log_file
    )

    if not logfile.is_file():
        return []

    try:

        return _read_tail_lines(
            logfile,
            lines,
            keep_newline=True,
        )

    except OSError:

        return []


def _read_tail_lines(
    log_file: Path,
    lines: int,
    keep_newline: bool = False,
) -> list[str]:
    """
    Efficiently read the newest lines from a logfile.

    This helper reads backwards from the end of the file until
    enough newline separators have been collected.

    When keep_newline is True, newline characters are preserved
    for compatibility with the historical read_last_lines()
    behavior.
    """

    if lines <= 0:
        return []

    with log_file.open(
        "rb"
    ) as file:

        file.seek(
            0,
            2,
        )

        position = file.tell()

        if position <= 0:
            return []

        buffer = b""

        while (
            position > 0
            and buffer.count(b"\n") <= lines
        ):

            block_size = min(
                READ_BLOCK_SIZE,
                position,
            )

            position -= block_size

            file.seek(
                position
            )

            block = file.read(
                block_size
            )

            buffer = (
                block
                +
                buffer
            )

        decoded = buffer.decode(
            "utf-8",
            errors="ignore",
        )

        if keep_newline:

            result = decoded.splitlines(
                keepends=True
            )

        else:

            result = decoded.splitlines()

        return result[
            -lines:
        ]


class IncrementalLogReader:
    """
    Incrementally follow a logfile.

    The reader keeps a bounded event history in memory.

    Multiple web clients may therefore request events using
    their own cursor without causing repeated full logfile reads.

    Every stored entry has a monotonically increasing numeric ID.

    Example entry:

        {
            "id": 125,
            "line": "Sun Aug 16 16:46:20 2026: ..."
        }

    The reader is thread-safe because Gunicorn may serve multiple
    dashboard requests concurrently.
    """

    def __init__(
        self,
        log_file: Path | str = DEFAULT_LOG_FILE,
        history_limit: int = DEFAULT_HISTORY_LIMIT,
        initial_lines: int = DEFAULT_INITIAL_LINES,
    ) -> None:

        self.log_file = Path(
            log_file
        )

        self.history_limit = max(
            1,
            int(
                history_limit
            ),
        )

        self.initial_lines = max(
            0,
            int(
                initial_lines
            ),
        )

        self._lock = RLock()

        self._history: deque[
            dict[str, object]
        ] = deque(
            maxlen=self.history_limit
        )

        self._inode: int | None = None
        self._offset = 0

        self._tracking_anchor = b""

        self._partial_line = b""

        self._next_id = 1

        self._initialized = False

    def sync(self) -> None:
        """
        Read newly appended logfile data.

        The first synchronization loads only the configured
        number of most recent lines.

        Subsequent synchronizations read only bytes appended
        after the saved offset.

        Log rotation, truncation and in-place rewriting are
        detected automatically.
        """

        with self._lock:

            if not self.log_file.is_file():

                self._reset_file_tracking()
                return

            try:

                log_stat = (
                    self.log_file.stat()
                )

            except OSError:

                return

            current_inode = (
                log_stat.st_ino
            )

            current_size = (
                log_stat.st_size
            )

            if not self._initialized:

                self._initialize_from_file(
                    current_inode,
                    current_size,
                )

                return

            logfile_replaced = (
                self._inode
                != current_inode
            )

            logfile_truncated = (
                current_size
                < self._offset
            )

            if (
                logfile_replaced
                or logfile_truncated
            ):

                self._initialize_from_file(
                    current_inode,
                    current_size,
                )

                return

            #
            # A logfile can be truncated and immediately rewritten
            # with content which is already larger than our saved
            # offset.
            #
            # In that situation current_size < self._offset is not
            # sufficient to detect the rewrite.
            #
            # Verify that the bytes immediately preceding our saved
            # offset are still identical to those observed during the
            # previous synchronization.
            #
            if not self._tracking_anchor_matches():

                self._initialize_from_file(
                    current_inode,
                    current_size,
                )

                return

            if (
                current_size
                == self._offset
            ):
                return

            self._read_appended_bytes(
                current_size
            )

    def get_entries(
        self,
        after_id: int = 0,
        limit: int | None = None,
    ) -> list[dict[str, object]]:
        """
        Return cached entries newer than after_id.

        sync() is executed first so the result includes the latest
        data currently present in the logfile.

        limit optionally restricts the number of returned entries.
        When limiting, the newest matching entries are retained.
        """

        with self._lock:

            self.sync()

            entries = [
                dict(
                    entry
                )
                for entry
                in self._history
                if int(
                    entry["id"]
                ) > after_id
            ]

            if (
                limit is not None
                and limit >= 0
            ):

                entries = entries[
                    -limit:
                ]

            return entries

    def get_latest(
        self,
        limit: int = 100,
    ) -> list[dict[str, object]]:
        """
        Return the newest cached logfile entries.
        """

        with self._lock:

            self.sync()

            if limit <= 0:
                return []

            return [
                dict(
                    entry
                )
                for entry
                in list(
                    self._history
                )[-limit:]
            ]

    def get_latest_id(self) -> int:
        """
        Return the ID of the newest cached entry.

        Zero means that no logfile entry has been stored yet.
        """

        with self._lock:

            self.sync()

            if not self._history:
                return 0

            return int(
                self._history[-1][
                    "id"
                ]
            )

    def clear_history(self) -> None:
        """
        Clear only the in-memory history.

        This does not modify or truncate the real SvxLink logfile.
        """

        with self._lock:

            self._history.clear()

    def _initialize_from_file(
        self,
        inode: int,
        size: int,
    ) -> None:
        """
        Initialize tracking from the current logfile.

        Only the newest configured number of lines are loaded.

        Existing in-memory history is kept when a rotation,
        truncation or rewrite occurs, so recent events remain
        visible while new events begin arriving from the current
        logfile.
        """

        self._inode = inode
        self._offset = size

        self._partial_line = b""

        self._initialized = True

        self._tracking_anchor = (
            self._read_tracking_anchor()
        )

        if self.initial_lines <= 0:
            return

        try:

            initial_lines = (
                _read_tail_lines(
                    self.log_file,
                    self.initial_lines,
                    keep_newline=False,
                )
            )

        except OSError:

            return

        for line in initial_lines:

            normalized = (
                line.rstrip(
                    "\r\n"
                )
            )

            if not normalized:
                continue

            self._append_entry(
                normalized
            )

    def _read_appended_bytes(
        self,
        current_size: int,
    ) -> None:
        """
        Read bytes appended since the previous synchronization.
        """

        try:

            with self.log_file.open(
                "rb"
            ) as file:

                file.seek(
                    self._offset
                )

                data = file.read(
                    current_size
                    - self._offset
                )

        except OSError:

            return

        self._offset = (
            current_size
        )

        if not data:

            self._tracking_anchor = (
                self._read_tracking_anchor()
            )

            return

        buffer = (
            self._partial_line
            +
            data
        )

        parts = buffer.split(
            b"\n"
        )

        if buffer.endswith(
            b"\n"
        ):

            complete_lines = (
                parts[:-1]
            )

            self._partial_line = b""

        else:

            complete_lines = (
                parts[:-1]
            )

            self._partial_line = (
                parts[-1]
            )

        for raw_line in complete_lines:

            line = raw_line.decode(
                "utf-8",
                errors="ignore",
            ).rstrip(
                "\r"
            )

            if not line:
                continue

            self._append_entry(
                line
            )

        self._tracking_anchor = (
            self._read_tracking_anchor()
        )

    def _read_tracking_anchor(
        self,
    ) -> bytes:
        """
        Read a small block immediately preceding the current
        byte offset.

        This block is used to detect an in-place logfile rewrite
        even when the rewritten file has already grown beyond the
        previously stored offset.
        """

        if self._offset <= 0:
            return b""

        anchor_size = min(
            TRACKING_ANCHOR_SIZE,
            self._offset,
        )

        anchor_start = (
            self._offset
            - anchor_size
        )

        try:

            with self.log_file.open(
                "rb"
            ) as file:

                file.seek(
                    anchor_start
                )

                return file.read(
                    anchor_size
                )

        except OSError:

            return b""

    def _tracking_anchor_matches(
        self,
    ) -> bool:
        """
        Return whether the already-read part of the logfile still
        matches the saved tracking anchor.

        False indicates that the file was rewritten in place.
        """

        if self._offset <= 0:
            return True

        if not self._tracking_anchor:
            return True

        current_anchor = (
            self._read_tracking_anchor()
        )

        return (
            current_anchor
            == self._tracking_anchor
        )

    def _append_entry(
        self,
        line: str,
    ) -> None:
        """
        Append one logfile entry to the in-memory history.
        """

        entry = {
            "id":
                self._next_id,

            "line":
                line,
        }

        self._history.append(
            entry
        )

        self._next_id += 1

    def _reset_file_tracking(
        self,
    ) -> None:
        """
        Reset physical logfile tracking.

        Cached history is intentionally retained.

        If the logfile temporarily disappears during rotation,
        previously collected operational events therefore remain
        available to the dashboard.
        """

        self._inode = None
        self._offset = 0

        self._tracking_anchor = b""

        self._partial_line = b""

        self._initialized = False
