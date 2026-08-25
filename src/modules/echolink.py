"""
EchoLink monitor.

Reads the SvxLink log and determines the current EchoLink
directory status, active connections, operator names,
connection start times, recent completed connections,
connection instability and the currently transmitting EchoLink station.
"""

from collections.abc import Iterator
from datetime import datetime, timedelta
from pathlib import Path
import re

from ..core.state import NodeState
from ..core.status import EchoLinkStatus
from .base import BaseMonitor


class EchoLinkMonitor(BaseMonitor):
    """
    Monitor EchoLink directory registration, active stations,
    connection start times, recent completed connections,
    connection stability and remote station transmission state.
    """

    LOG_FILE = Path("/var/log/svxlink")
    READ_BLOCK_SIZE = 8192

    DIRECTORY_STATUS_PREFIX = (
        "EchoLink directory status changed to "
    )

    MODULE_START_MESSAGE = "Module EchoLink"

    MODULE_DEACTIVATION_MESSAGE = (
        "Deactivating module EchoLink"
    )

    CONNECTION_PATTERN = re.compile(
        r"(?P<station>[A-Za-z0-9/._-]+): "
        r"EchoLink QSO state changed to "
        r"(?P<status>CONNECTED|DISCONNECTED)"
    )

    INCOMING_CONNECTION_PATTERN = re.compile(
        r"Incoming EchoLink connection from "
        r"(?P<station>[A-Za-z0-9/._-]+)"
        r"(?: \((?P<name>[^)]+)\))? "
        r"at "
    )

    TRANSMISSION_PATTERN = re.compile(
        r"SVXGUARDIAN_ECHOLINK_RX_"
        r"(?P<status>START|STOP) "
        r"(?P<station>[A-Za-z0-9/._-]+)"
    )

    LOG_TIMESTAMP_PATTERN = re.compile(
        r"^(?P<weekday>[A-Za-z]{3})\s+"
        r"(?P<month>[A-Za-z]{3})\s+"
        r"(?P<day>\d{1,2})\s+"
        r"(?P<time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<year>\d{4}):"
    )

    DNS_ERROR_MESSAGES = (
        "EchoLink directory server DNS lookup failed",
        "No IP addresses were returned for the EchoLink "
        "directory server DNS query",
        'Could not look up host "servers.echolink.org"',
    )

    #
    # EchoLink connection stability.
    #
    # WINDOW:
    # observation window used to detect repeated changes
    # between CONNECTED and DISCONNECTED.
    #
    # TRANSITIONS:
    # minimum number of real state changes required to
    # classify a station as unstable.
    #
    # HOLD:
    # minimum time the instability indication remains
    # available after the threshold has been reached.
    #
    INSTABILITY_WINDOW_SECONDS = 30
    INSTABILITY_TRANSITIONS = 3
    INSTABILITY_HOLD_SECONDS = 10

    RECENT_CONNECTION_LIMIT = 20

    RECENT_CONNECTION_EVENT_MARKERS = (
        "EchoLink QSO state changed to ",
        "Incoming EchoLink connection from ",
    )

    def __init__(
        self,
        log_file: Path | str = LOG_FILE,
    ) -> None:
        self.log_file = Path(log_file)

        self._recent_connections_cache: list[
            dict[str, object]
        ] = []

        self._recent_log_inode: int | None = None
        self._recent_log_size = 0

        # Immutable reverse-log snapshot used only during one
        # check() cycle.  It prevents repeated physical reads of
        # the same SvxLink logfile while preserving the existing
        # analysis logic and stopping conditions.
        self._log_lines_snapshot: tuple[str, ...] | None = None

    def check(self, state: NodeState) -> None:
        """
        Update all EchoLink runtime information.
        """

        state.echolink_status = EchoLinkStatus.UNKNOWN
        state.echolink_last_error = ""

        state.echolink_connected_stations = []
        state.echolink_station_names = {}
        state.echolink_connection_started = {}
        state.echolink_unstable_stations = []
        state.echolink_connection_count = 0

        state.echolink_transmitting = False
        state.echolink_transmitting_station = ""
        state.echolink_recent_connections = []

        self._log_lines_snapshot = tuple(
            self._read_lines_reverse_from_file()
        )

        try:
            self._update_directory_status(state)
            self._update_connected_stations(state)
            self._update_recent_connections(state)
            self._update_connection_stability(state)
            self._update_transmission_state(state)

            # A deactivated EchoLink module cannot have active
            # EchoLink stations.  This is the final authoritative
            # consistency rule for the operational state.
            if self._is_module_deactivated():
                state.echolink_connected_stations = []
                state.echolink_station_names = {}
                state.echolink_connection_started = {}
                state.echolink_unstable_stations = []
                state.echolink_connection_count = 0
                state.echolink_transmitting = False
                state.echolink_transmitting_station = ""

        finally:
            self._log_lines_snapshot = None

    def _is_module_deactivated(self) -> bool:
        """
        Return whether the latest relevant EchoLink event indicates
        that the module is currently deactivated.

        A CONNECTED event newer than a module deactivation proves
        that EchoLink became operational again, even when SvxLink
        did not emit a module-start message in between.
        """

        for line in self._read_lines_reverse():

            if self.MODULE_DEACTIVATION_MESSAGE in line:
                return True

            if self._is_module_start(line):
                return False

            connection_event = (
                self._extract_connection_event(line)
            )

            if connection_event is None:
                continue

            _, connected = connection_event

            if connected:
                return False

        return False

    def _update_directory_status(
        self,
        state: NodeState,
    ) -> None:
        """
        Update the EchoLink directory registration status.
        """

        for line in self._read_lines_reverse():

            if self._is_dns_error(line):

                state.echolink_status = (
                    EchoLinkStatus.DNS_ERROR
                )

                state.echolink_last_error = (
                    "REASON_ECHOLINK_DNS_ERROR"
                )

                return

            directory_status = (
                self._extract_directory_status(line)
            )

            if directory_status is None:
                continue

            state.echolink_status = (
                self._map_directory_status(
                    directory_status
                )
            )

            if (
                state.echolink_status
                is EchoLinkStatus.ERROR
            ):

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

        The SvxLink log is scanned backwards.

        The newest CONNECTED or DISCONNECTED event for each
        station determines the current technical connection
        state.

        For every connected station the timestamp of the most
        recent CONNECTED event is retained as the beginning of
        the current EchoLink session.
        """

        station_states: dict[str, bool] = {}
        station_names: dict[str, str] = {}
        connection_started: dict[str, str] = {}

        for line in self._read_lines_reverse():

            if self._is_module_start(line):
                break

            incoming_connection = (
                self._extract_incoming_connection(line)
            )

            if incoming_connection is not None:

                station, name = incoming_connection

                if (
                    name
                    and station not in station_names
                ):

                    station_names[station] = name

            connection_event = (
                self._extract_connection_event(line)
            )

            if connection_event is None:
                continue

            station, connected = connection_event

            if station in station_states:
                continue

            station_states[station] = connected

            if connected:

                timestamp = (
                    self._extract_log_datetime(line)
                )

                if timestamp is not None:

                    connection_started[station] = (
                        timestamp.isoformat(
                            timespec="seconds"
                        )
                    )

        connected_stations = sorted(
            station
            for station, connected
            in station_states.items()
            if connected
        )

        state.echolink_connected_stations = (
            connected_stations
        )

        state.echolink_station_names = {
            station: station_names[station]
            for station in connected_stations
            if station in station_names
        }

        state.echolink_connection_started = {
            station: connection_started[station]
            for station in connected_stations
            if station in connection_started
        }

        state.echolink_connection_count = len(
            connected_stations
        )

    def _update_recent_connections(
        self,
        state: NodeState,
    ) -> None:
        """
        Update the most recent completed EchoLink sessions.

        The history is cached.

        If the logfile has not changed, the cached history is
        reused immediately.

        If the logfile only grew with lines unrelated to EchoLink
        connection lifecycle events, the cached history is also
        reused.

        A full reconstruction is therefore required only on the
        first check, after logfile rotation/truncation or when new
        CONNECTED, DISCONNECTED or incoming-connection information
        has actually been appended.

        Full reconstruction scans the logfile backwards and stops
        as soon as the twenty required sessions, their operator
        names and the instability look-back window are complete.
        """

        if not self.log_file.is_file():

            self._recent_connections_cache = []
            self._recent_log_inode = None
            self._recent_log_size = 0

            state.echolink_recent_connections = []
            return

        try:

            log_stat = self.log_file.stat()

        except OSError:

            state.echolink_recent_connections = list(
                self._recent_connections_cache
            )
            return

        current_inode = log_stat.st_ino
        current_size = log_stat.st_size

        same_logfile = (
            self._recent_log_inode == current_inode
        )

        if (
            same_logfile
            and current_size == self._recent_log_size
        ):

            state.echolink_recent_connections = list(
                self._recent_connections_cache
            )
            return

        rebuild_required = True

        if (
            same_logfile
            and current_size > self._recent_log_size
        ):

            appended_text = (
                self._read_appended_log_text(
                    self._recent_log_size,
                )
            )

            rebuild_required = any(
                marker in appended_text
                for marker
                in self.RECENT_CONNECTION_EVENT_MARKERS
            )

        if rebuild_required:

            self._recent_connections_cache = (
                self._build_recent_connections()
            )

        self._recent_log_inode = current_inode
        self._recent_log_size = current_size

        state.echolink_recent_connections = list(
            self._recent_connections_cache
        )

    def _read_appended_log_text(
        self,
        start_offset: int,
    ) -> str:
        """
        Read logfile data appended after start_offset.
        """

        try:

            with self.log_file.open(
                "rb"
            ) as log_file:

                log_file.seek(
                    start_offset
                )

                return log_file.read().decode(
                    "utf-8",
                    errors="ignore",
                )

        except OSError:

            return ""

    def _build_recent_connections(
        self,
    ) -> list[dict[str, object]]:
        """
        Reconstruct the newest completed EchoLink sessions.

        The logfile is scanned backwards.

        The scan stops once the required twenty completed sessions
        have been reconstructed, their available operator names
        have been collected and enough older connection events have
        been read to evaluate the normal instability window around
        the oldest retained session.
        """

        completed_sessions: list[
            dict[str, object]
        ] = []

        pending_disconnects: dict[
            str,
            list[dict[str, object]],
        ] = {}

        awaiting_names: dict[
            str,
            list[dict[str, object]],
        ] = {}

        connection_events: dict[
            str,
            list[tuple[datetime, bool]],
        ] = {}

        oldest_connected_at: datetime | None = None

        for line in self._read_lines_reverse():

            timestamp = (
                self._extract_log_datetime(line)
            )

            connection_event = (
                self._extract_connection_event(line)
            )

            if (
                connection_event is not None
                and timestamp is not None
            ):

                station, connected = connection_event

                connection_events.setdefault(
                    station,
                    [],
                ).append(
                    (
                        timestamp,
                        connected,
                    )
                )

                if not connected:

                    if (
                        len(completed_sessions)
                        < self.RECENT_CONNECTION_LIMIT
                    ):

                        session: dict[str, object] = {
                            "station": station,
                            "name": "",
                            "connected_at": "",
                            "disconnected_at": (
                                timestamp.isoformat(
                                    timespec="seconds"
                                )
                            ),
                            "duration_seconds": 0,
                            "unstable": False,
                        }

                        pending_disconnects.setdefault(
                            station,
                            [],
                        ).append(
                            session
                        )

                        completed_sessions.append(
                            session
                        )

                else:

                    station_pending = (
                        pending_disconnects.get(
                            station
                        )
                    )

                    if station_pending:

                        session = (
                            station_pending.pop(0)
                        )

                        disconnected_at_text = (
                            session.get(
                                "disconnected_at"
                            )
                        )

                        if isinstance(
                            disconnected_at_text,
                            str,
                        ):

                            try:

                                disconnected_at = (
                                    datetime.fromisoformat(
                                        disconnected_at_text
                                    )
                                )

                            except ValueError:

                                disconnected_at = None

                            if (
                                disconnected_at is not None
                                and timestamp <= disconnected_at
                            ):

                                session[
                                    "connected_at"
                                ] = (
                                    timestamp.isoformat(
                                        timespec="seconds"
                                    )
                                )

                                session[
                                    "duration_seconds"
                                ] = max(
                                    0,
                                    int(
                                        (
                                            disconnected_at
                                            - timestamp
                                        ).total_seconds()
                                    ),
                                )

                                awaiting_names.setdefault(
                                    station,
                                    [],
                                ).append(
                                    session
                                )

                                if (
                                    oldest_connected_at is None
                                    or timestamp
                                    < oldest_connected_at
                                ):

                                    oldest_connected_at = (
                                        timestamp
                                    )

            incoming_connection = (
                self._extract_incoming_connection(
                    line
                )
            )

            if incoming_connection is not None:

                station, name = (
                    incoming_connection
                )

                if name:

                    station_awaiting_names = (
                        awaiting_names.get(
                            station
                        )
                    )

                    if station_awaiting_names:

                        session = (
                            station_awaiting_names.pop(0)
                        )

                        session["name"] = name

            valid_sessions = [
                session
                for session in completed_sessions
                if session.get(
                    "connected_at"
                )
            ]

            enough_sessions = (
                len(valid_sessions)
                >= self.RECENT_CONNECTION_LIMIT
            )

            names_resolved = not any(
                sessions
                for sessions
                in awaiting_names.values()
            )

            instability_history_complete = False

            if (
                enough_sessions
                and oldest_connected_at is not None
                and timestamp is not None
            ):

                instability_history_complete = (
                    timestamp
                    <= (
                        oldest_connected_at
                        - timedelta(
                            seconds=(
                                self.INSTABILITY_WINDOW_SECONDS
                            )
                        )
                    )
                )

            if (
                enough_sessions
                and names_resolved
                and instability_history_complete
            ):

                break

        valid_sessions = [
            session
            for session in completed_sessions
            if session.get(
                "connected_at"
            )
        ]

        for session in valid_sessions:

            station = session.get(
                "station"
            )

            connected_at_text = session.get(
                "connected_at"
            )

            disconnected_at_text = session.get(
                "disconnected_at"
            )

            if not isinstance(
                station,
                str,
            ):
                continue

            if not isinstance(
                connected_at_text,
                str,
            ):
                continue

            if not isinstance(
                disconnected_at_text,
                str,
            ):
                continue

            try:

                connected_at = (
                    datetime.fromisoformat(
                        connected_at_text
                    )
                )

                disconnected_at = (
                    datetime.fromisoformat(
                        disconnected_at_text
                    )
                )

            except ValueError:

                continue

            instability_window_start = (
                connected_at
                - timedelta(
                    seconds=(
                        self.INSTABILITY_WINDOW_SECONDS
                    )
                )
            )

            instability_window_end = (
                disconnected_at
                + timedelta(
                    seconds=(
                        self.INSTABILITY_WINDOW_SECONDS
                    )
                )
            )

            relevant_events = sorted(
                (
                    event
                    for event
                    in connection_events.get(
                        station,
                        []
                    )
                    if (
                        instability_window_start
                        <= event[0]
                        <= instability_window_end
                    )
                ),
                key=lambda event: event[0],
            )

            session["unstable"] = (
                self._count_state_transitions(
                    relevant_events
                )
                >= self.INSTABILITY_TRANSITIONS
            )

        valid_sessions.sort(
            key=lambda session: str(
                session.get(
                    "disconnected_at",
                    ""
                )
            ),
            reverse=True,
        )

        return valid_sessions[
            : self.RECENT_CONNECTION_LIMIT
        ]

    def _update_connection_stability(
        self,
        state: NodeState,
    ) -> None:
        """
        Detect unstable EchoLink connections.

        A station becomes unstable when repeated real changes
        between CONNECTED and DISCONNECTED occur inside the
        configured observation window.

        Once detected, the instability indication is held for
        at least INSTABILITY_HOLD_SECONDS.

        The hold time is not a connection timeout.

        A DISCONNECTED event still means that the station is
        technically disconnected and therefore it disappears
        from the normal connected-station list.

        If it reconnects while the instability condition is
        still valid, it can immediately appear again as
        unstable.

        RX_STOP has operational priority over an older
        instability condition and returns the station to the
        normal green state.

        New connection oscillations occurring after RX_STOP
        are allowed to create a new instability condition.
        """

        now = datetime.now()

        detection_window_start = (
            now
            - timedelta(
                seconds=self.INSTABILITY_WINDOW_SECONDS
            )
        )

        history_window_start = (
            now
            - timedelta(
                seconds=(
                    self.INSTABILITY_WINDOW_SECONDS
                    +
                    self.INSTABILITY_HOLD_SECONDS
                )
            )
        )

        events_by_station: dict[
            str,
            list[tuple[datetime, bool]],
        ] = {}

        for line in self._read_lines_reverse():

            if self._is_module_start(line):
                break

            timestamp = (
                self._extract_log_datetime(line)
            )

            if timestamp is None:
                continue

            if timestamp < history_window_start:
                break

            connection_event = (
                self._extract_connection_event(line)
            )

            if connection_event is None:
                continue

            station, connected = connection_event

            events_by_station.setdefault(
                station,
                [],
            ).append(
                (
                    timestamp,
                    connected,
                )
            )

        unstable_stations: list[str] = []

        instability_trigger_times: dict[
            str,
            datetime,
        ] = {}

        for station, events in events_by_station.items():

            chronological_events = list(
                reversed(events)
            )

            if len(chronological_events) < 2:
                continue

            #
            # Determine whether the station is currently
            # unstable using the normal 30-second window.
            #
            current_window_events = [
                event
                for event in chronological_events
                if event[0] >= detection_window_start
            ]

            current_transitions = (
                self._count_state_transitions(
                    current_window_events
                )
            )

            currently_unstable = (
                current_transitions
                >= self.INSTABILITY_TRANSITIONS
            )

            #
            # Find the most recent event at which the
            # instability threshold became satisfied.
            #
            latest_trigger_time: datetime | None = None

            for index, (
                event_time,
                _,
            ) in enumerate(
                chronological_events
            ):

                event_window_start = (
                    event_time
                    - timedelta(
                        seconds=(
                            self.INSTABILITY_WINDOW_SECONDS
                        )
                    )
                )

                window_events = [
                    candidate
                    for candidate
                    in chronological_events[: index + 1]
                    if candidate[0] >= event_window_start
                ]

                transitions = (
                    self._count_state_transitions(
                        window_events
                    )
                )

                if (
                    transitions
                    >= self.INSTABILITY_TRANSITIONS
                ):

                    latest_trigger_time = (
                        event_time
                    )

            held_unstable = False

            if latest_trigger_time is not None:

                hold_end = (
                    latest_trigger_time
                    + timedelta(
                        seconds=(
                            self.INSTABILITY_HOLD_SECONDS
                        )
                    )
                )

                held_unstable = (
                    now <= hold_end
                )

            if (
                currently_unstable
                or held_unstable
            ):

                unstable_stations.append(
                    station
                )

                if latest_trigger_time is not None:

                    instability_trigger_times[
                        station
                    ] = latest_trigger_time

        #
        # Yellow is displayed only for a station which is
        # currently represented as connected.
        #
        connected_stations = set(
            state.echolink_connected_stations
        )

        state.echolink_unstable_stations = sorted(
            station
            for station in unstable_stations
            if station in connected_stations
        )

        #
        # A recent RX_STOP returns the station to GREEN.
        #
        # An old RX_STOP must never cancel instability that
        # started later.
        #
        for station in list(
            state.echolink_unstable_stations
        ):

            latest_transmission_event = (
                self._find_latest_transmission_event(
                    station
                )
            )

            if latest_transmission_event is None:
                continue

            (
                transmission_timestamp,
                transmitting,
            ) = latest_transmission_event

            #
            # RX_START does not suppress instability here.
            # The transmitting-state function will give RED
            # absolute priority afterwards.
            #
            if transmitting:
                continue

            trigger_time = (
                instability_trigger_times.get(
                    station
                )
            )

            if trigger_time is None:
                continue

            #
            # RX_STOP suppresses yellow only if it occurred
            # after the instability episode which caused the
            # current yellow indication.
            #
            if (
                transmission_timestamp
                >= trigger_time
            ):

                state.echolink_unstable_stations.remove(
                    station
                )

    def _update_transmission_state(
        self,
        state: NodeState,
    ) -> None:
        """
        Determine the currently transmitting EchoLink station.

        Canonical local events:

            SVXGUARDIAN_ECHOLINK_RX_START <CALLSIGN>
            SVXGUARDIAN_ECHOLINK_RX_STOP <CALLSIGN>

        RX_START has absolute operational priority.

        If audio is being received from a station, that station
        is necessarily operationally present even if a recent
        CONNECTED/DISCONNECTED sequence temporarily suggested
        otherwise.

        RX_STOP returns the station to green only when that
        RX_STOP is still relevant to the latest connection
        history.

        A historical RX_STOP must not influence new connection
        events or new instability episodes.
        """

        latest_transmission_event = None

        for line in self._read_lines_reverse():

            if self._is_module_start(line):
                break

            transmission_event = (
                self._extract_transmission_event(line)
            )

            if transmission_event is None:
                continue

            timestamp = (
                self._extract_log_datetime(line)
            )

            if timestamp is None:
                continue

            station, transmitting = (
                transmission_event
            )

            latest_transmission_event = (
                timestamp,
                station,
                transmitting,
            )

            break

        if latest_transmission_event is None:
            return

        (
            transmission_timestamp,
            station,
            transmitting,
        ) = latest_transmission_event

        latest_connection_event = (
            self._find_latest_connection_event(
                station
            )
        )

        #
        # If a CONNECTED or DISCONNECTED event happened after
        # this transmission event, the transmission event is
        # historical and must not modify the current connection
        # state.
        #
        if latest_connection_event is not None:

            (
                connection_timestamp,
                _,
            ) = latest_connection_event

            if (
                connection_timestamp
                > transmission_timestamp
            ):

                return

        #
        # RX_START:
        #
        # direct evidence that the station is transmitting.
        #
        if transmitting:

            state.echolink_transmitting = True

            state.echolink_transmitting_station = (
                station
            )

            #
            # RED always has visual priority over YELLOW.
            #
            if (
                station
                in state.echolink_unstable_stations
            ):

                state.echolink_unstable_stations.remove(
                    station
                )

            self._ensure_operational_station_present(
                state,
                station,
            )

            return

        #
        # RX_STOP:
        #
        # because no newer connection-state event exists,
        # this stop belongs to the current operational episode.
        #
        # The station therefore returns to GREEN.
        #
        self._ensure_operational_station_present(
            state,
            station,
        )

        if (
            station
            in state.echolink_unstable_stations
        ):

            state.echolink_unstable_stations.remove(
                station
            )

    def _ensure_operational_station_present(
        self,
        state: NodeState,
        station: str,
    ) -> None:
        """
        Ensure a station is represented in the operational
        station list.

        Used when RX_START or a relevant RX_STOP provides direct
        evidence of operational presence despite temporary
        mobile-network instability.
        """

        if (
            station
            not in state.echolink_connected_stations
        ):

            state.echolink_connected_stations.append(
                station
            )

            state.echolink_connected_stations.sort()

        if (
            station
            not in state.echolink_station_names
        ):

            name = (
                self._find_latest_station_name(
                    station
                )
            )

            if name:

                state.echolink_station_names[
                    station
                ] = name

        if (
            station
            not in state.echolink_connection_started
        ):

            connection_started = (
                self._find_latest_connection_start(
                    station
                )
            )

            if connection_started is not None:

                state.echolink_connection_started[
                    station
                ] = (
                    connection_started.isoformat(
                        timespec="seconds"
                    )
                )

        state.echolink_connection_count = len(
            state.echolink_connected_stations
        )

    @staticmethod
    def _count_state_transitions(
        events: list[tuple[datetime, bool]],
    ) -> int:
        """
        Count real CONNECTED/DISCONNECTED transitions.

        Repeated events with the same state do not increment
        the transition counter.
        """

        if len(events) < 2:
            return 0

        transitions = 0
        previous_state: bool | None = None

        for _, connected in events:

            if previous_state is None:

                previous_state = connected
                continue

            if connected != previous_state:

                transitions += 1
                previous_state = connected

        return transitions

    def _find_latest_transmission_event(
        self,
        wanted_station: str,
    ) -> tuple[datetime, bool] | None:
        """
        Find the most recent RX_START or RX_STOP event for the
        requested EchoLink station.
        """

        for line in self._read_lines_reverse():

            if self._is_module_start(line):
                break

            transmission_event = (
                self._extract_transmission_event(line)
            )

            if transmission_event is None:
                continue

            station, transmitting = (
                transmission_event
            )

            if station != wanted_station:
                continue

            timestamp = (
                self._extract_log_datetime(line)
            )

            if timestamp is None:
                continue

            return (
                timestamp,
                transmitting,
            )

        return None

    def _find_latest_connection_event(
        self,
        wanted_station: str,
    ) -> tuple[datetime, bool] | None:
        """
        Find the most recent CONNECTED or DISCONNECTED event
        for the requested EchoLink station.
        """

        for line in self._read_lines_reverse():

            if self._is_module_start(line):
                break

            connection_event = (
                self._extract_connection_event(line)
            )

            if connection_event is None:
                continue

            station, connected = (
                connection_event
            )

            if station != wanted_station:
                continue

            timestamp = (
                self._extract_log_datetime(line)
            )

            if timestamp is None:
                continue

            return (
                timestamp,
                connected,
            )

        return None

    def _find_latest_station_name(
        self,
        wanted_station: str,
    ) -> str:
        """
        Find the most recently reported operator name for a
        station.
        """

        for line in self._read_lines_reverse():

            if self._is_module_start(line):
                break

            incoming_connection = (
                self._extract_incoming_connection(line)
            )

            if incoming_connection is None:
                continue

            station, name = incoming_connection

            if (
                station == wanted_station
                and name
            ):

                return name

        return ""

    def _find_latest_connection_start(
        self,
        wanted_station: str,
    ) -> datetime | None:
        """
        Find the most recent CONNECTED timestamp for a station.
        """

        for line in self._read_lines_reverse():

            if self._is_module_start(line):
                break

            connection_event = (
                self._extract_connection_event(line)
            )

            if connection_event is None:
                continue

            station, connected = (
                connection_event
            )

            if station != wanted_station:
                continue

            if not connected:
                continue

            return self._extract_log_datetime(
                line
            )

        return None

    def _read_lines_reverse(
        self,
    ) -> Iterator[str]:
        """
        Read the SvxLink log backwards, one line at a time.

        During check(), reuse the immutable snapshot captured at
        the beginning of the cycle.  Outside check(), read the
        logfile directly as before.
        """

        if self._log_lines_snapshot is not None:
            yield from self._log_lines_snapshot
            return

        yield from self._read_lines_reverse_from_file()

    def _read_lines_reverse_from_file(
        self,
    ) -> Iterator[str]:
        """
        Physically read the SvxLink logfile backwards.
        """

        if not self.log_file.is_file():
            return

        try:

            with self.log_file.open(
                "rb"
            ) as log_file:

                log_file.seek(
                    0,
                    2,
                )

                position = (
                    log_file.tell()
                )

                buffer = b""

                while position > 0:

                    block_size = min(
                        self.READ_BLOCK_SIZE,
                        position,
                    )

                    position -= block_size

                    log_file.seek(
                        position
                    )

                    block = log_file.read(
                        block_size
                    )

                    buffer = (
                        block
                        +
                        buffer
                    )

                    lines = buffer.split(
                        b"\n"
                    )

                    buffer = lines[0]

                    for raw_line in reversed(
                        lines[1:]
                    ):

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

    def _is_dns_error(
        self,
        line: str,
    ) -> bool:
        """
        Return whether a log line reports an EchoLink DNS error.
        """

        return any(
            message in line
            for message
            in self.DNS_ERROR_MESSAGES
        )

    def _is_module_start(
        self,
        line: str,
    ) -> bool:
        """
        Return whether the line marks an EchoLink module start.
        """

        return (
            self.MODULE_START_MESSAGE
            in line
            and
            "starting"
            in line.lower()
        )

    def _extract_directory_status(
        self,
        line: str,
    ) -> str | None:
        """
        Extract the raw EchoLink directory status.
        """

        if (
            self.DIRECTORY_STATUS_PREFIX
            not in line
        ):

            return None

        _, _, status = line.partition(
            self.DIRECTORY_STATUS_PREFIX
        )

        normalized_status = (
            status
            .strip()
            .upper()
        )

        return (
            normalized_status
            or None
        )

    def _extract_connection_event(
        self,
        line: str,
    ) -> tuple[str, bool] | None:
        """
        Extract a station connection event.
        """

        match = (
            self.CONNECTION_PATTERN.search(
                line
            )
        )

        if match is None:
            return None

        station = (
            match.group(
                "station"
            )
            .strip()
            .upper()
        )

        connection_status = (
            match.group(
                "status"
            )
        )

        return (
            station,
            connection_status == "CONNECTED",
        )

    def _extract_incoming_connection(
        self,
        line: str,
    ) -> tuple[str, str] | None:
        """
        Extract station callsign and operator name.
        """

        match = (
            self.INCOMING_CONNECTION_PATTERN.search(
                line
            )
        )

        if match is None:
            return None

        station = (
            match.group(
                "station"
            )
            .strip()
            .upper()
        )

        raw_name = (
            match.group(
                "name"
            )
            or
            ""
        )

        name = (
            raw_name.strip()
        )

        return (
            station,
            name,
        )

    def _extract_transmission_event(
        self,
        line: str,
    ) -> tuple[str, bool] | None:
        """
        Extract a canonical SVX Guardian EchoLink
        transmission event.
        """

        match = (
            self.TRANSMISSION_PATTERN.search(
                line
            )
        )

        if match is None:
            return None

        station = (
            match.group(
                "station"
            )
            .strip()
            .upper()
        )

        transmission_status = (
            match.group(
                "status"
            )
        )

        return (
            station,
            transmission_status == "START",
        )

    def _extract_log_datetime(
        self,
        line: str,
    ) -> datetime | None:
        """
        Extract the datetime at the beginning of a SvxLink
        log line.

        Example:

            Fri Aug  7 07:14:40 2026:
            -> datetime(2026, 8, 7, 7, 14, 40)
        """

        match = (
            self.LOG_TIMESTAMP_PATTERN.search(
                line
            )
        )

        if match is None:
            return None

        timestamp_text = (
            f"{match.group('month')} "
            f"{match.group('day')} "
            f"{match.group('time')} "
            f"{match.group('year')}"
        )

        try:

            return datetime.strptime(
                timestamp_text,
                "%b %d %H:%M:%S %Y",
            )

        except ValueError:

            return None

    def _extract_log_timestamp(
        self,
        line: str,
    ) -> str | None:
        """
        Extract the timestamp at the beginning of a SvxLink
        log line and return it in ISO 8601 local-time format.
        """

        timestamp = (
            self._extract_log_datetime(
                line
            )
        )

        if timestamp is None:
            return None

        return timestamp.isoformat(
            timespec="seconds"
        )

    @staticmethod
    def _map_directory_status(
        directory_status: str,
    ) -> EchoLinkStatus:
        """
        Convert a SvxLink directory status into an
        internal canonical EchoLink status.
        """

        if directory_status == "ON":
            return EchoLinkStatus.ONLINE

        if directory_status == "OFF":
            return EchoLinkStatus.OFFLINE

        if directory_status == "?":
            return EchoLinkStatus.ERROR

        return EchoLinkStatus.UNKNOWN
