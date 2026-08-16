"""
Tests for the EchoLink recent connection history.

The recent connection history is reconstructed from the
SvxLink log and contains only completed EchoLink sessions.
"""

from datetime import datetime, timedelta
from pathlib import Path

from src.core.state import NodeState
from src.modules.echolink import EchoLinkMonitor


def _write_log(
    log_file: Path,
    lines: list[str],
) -> None:
    """
    Write a synthetic SvxLink log used by the tests.
    """

    log_file.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def _format_log_line(
    timestamp: datetime,
    message: str,
) -> str:
    """
    Return one line using the SvxLink timestamp format.
    """

    return (
        timestamp.strftime(
            "%a %b %d %H:%M:%S %Y"
        )
        + ": "
        + message
    )


def test_recent_connections_reconstructs_completed_session(
    tmp_path: Path,
) -> None:
    """
    A CONNECTED/DISCONNECTED pair must produce one completed
    EchoLink session with station, operator, timestamps and
    duration.
    """

    log_file = tmp_path / "svxlink.log"

    connected_at = datetime(
        2026,
        8,
        16,
        10,
        12,
        44,
    )

    disconnected_at = datetime(
        2026,
        8,
        16,
        10,
        24,
        2,
    )

    _write_log(
        log_file,
        [
            _format_log_line(
                connected_at - timedelta(seconds=1),
                (
                    "Incoming EchoLink connection from "
                    "IU5HJU (MICHELE) at 192.0.2.10"
                ),
            ),
            _format_log_line(
                connected_at,
                (
                    "IU5HJU: EchoLink QSO state changed "
                    "to CONNECTED"
                ),
            ),
            _format_log_line(
                disconnected_at,
                (
                    "IU5HJU: EchoLink QSO state changed "
                    "to DISCONNECTED"
                ),
            ),
        ],
    )

    monitor = EchoLinkMonitor(
        log_file=log_file
    )

    state = NodeState()

    monitor.check(state)

    assert len(
        state.echolink_recent_connections
    ) == 1

    session = (
        state.echolink_recent_connections[0]
    )

    assert session["station"] == "IU5HJU"
    assert session["name"] == "MICHELE"

    assert session["connected_at"] == (
        connected_at.isoformat(
            timespec="seconds"
        )
    )

    assert session["disconnected_at"] == (
        disconnected_at.isoformat(
            timespec="seconds"
        )
    )

    assert session["duration_seconds"] == 678
    assert session["unstable"] is False


def test_recent_connections_excludes_active_session(
    tmp_path: Path,
) -> None:
    """
    A station which has CONNECTED but has not DISCONNECTED
    must not appear in the completed-session history.
    """

    log_file = tmp_path / "svxlink.log"

    first_connected_at = datetime(
        2026,
        8,
        16,
        11,
        0,
        0,
    )

    first_disconnected_at = datetime(
        2026,
        8,
        16,
        11,
        5,
        0,
    )

    active_connected_at = datetime(
        2026,
        8,
        16,
        11,
        10,
        0,
    )

    _write_log(
        log_file,
        [
            _format_log_line(
                first_connected_at - timedelta(seconds=1),
                (
                    "Incoming EchoLink connection from "
                    "IK5AAA (ALFA) at 192.0.2.11"
                ),
            ),
            _format_log_line(
                first_connected_at,
                (
                    "IK5AAA: EchoLink QSO state changed "
                    "to CONNECTED"
                ),
            ),
            _format_log_line(
                first_disconnected_at,
                (
                    "IK5AAA: EchoLink QSO state changed "
                    "to DISCONNECTED"
                ),
            ),
            _format_log_line(
                active_connected_at - timedelta(seconds=1),
                (
                    "Incoming EchoLink connection from "
                    "IK5BBB (BRAVO) at 192.0.2.12"
                ),
            ),
            _format_log_line(
                active_connected_at,
                (
                    "IK5BBB: EchoLink QSO state changed "
                    "to CONNECTED"
                ),
            ),
        ],
    )

    monitor = EchoLinkMonitor(
        log_file=log_file
    )

    state = NodeState()

    monitor.check(state)

    assert len(
        state.echolink_recent_connections
    ) == 1

    session = (
        state.echolink_recent_connections[0]
    )

    assert session["station"] == "IK5AAA"

    assert "IK5BBB" not in {
        item["station"]
        for item
        in state.echolink_recent_connections
    }


def test_recent_connections_are_limited_and_newest_first(
    tmp_path: Path,
) -> None:
    """
    Only the twenty most recent completed sessions must be
    retained and they must be ordered newest first.
    """

    log_file = tmp_path / "svxlink.log"

    start = datetime(
        2026,
        8,
        16,
        12,
        0,
        0,
    )

    lines: list[str] = []

    for index in range(25):

        station = f"TEST{index:02d}"

        connected_at = (
            start
            + timedelta(
                minutes=index * 2
            )
        )

        disconnected_at = (
            connected_at
            + timedelta(
                seconds=30
            )
        )

        lines.extend(
            [
                _format_log_line(
                    connected_at - timedelta(seconds=1),
                    (
                        "Incoming EchoLink connection from "
                        f"{station} (OP{index:02d}) "
                        "at 192.0.2.20"
                    ),
                ),
                _format_log_line(
                    connected_at,
                    (
                        f"{station}: EchoLink QSO state "
                        "changed to CONNECTED"
                    ),
                ),
                _format_log_line(
                    disconnected_at,
                    (
                        f"{station}: EchoLink QSO state "
                        "changed to DISCONNECTED"
                    ),
                ),
            ]
        )

    _write_log(
        log_file,
        lines,
    )

    monitor = EchoLinkMonitor(
        log_file=log_file
    )

    state = NodeState()

    monitor.check(state)

    assert len(
        state.echolink_recent_connections
    ) == 20

    assert (
        state.echolink_recent_connections[0][
            "station"
        ]
        == "TEST24"
    )

    assert (
        state.echolink_recent_connections[-1][
            "station"
        ]
        == "TEST05"
    )

    disconnected_times = [
        session["disconnected_at"]
        for session
        in state.echolink_recent_connections
    ]

    assert disconnected_times == sorted(
        disconnected_times,
        reverse=True,
    )


def test_recent_connections_detects_instability(
    tmp_path: Path,
) -> None:
    """
    Repeated real CONNECTED/DISCONNECTED transitions inside
    the normal EchoLink instability window must mark the
    reconstructed session as unstable.
    """

    log_file = tmp_path / "svxlink.log"

    start = datetime(
        2026,
        8,
        16,
        15,
        0,
        0,
    )

    _write_log(
        log_file,
        [
            _format_log_line(
                start - timedelta(seconds=1),
                (
                    "Incoming EchoLink connection from "
                    "IZ5TEST (TEST) at 192.0.2.30"
                ),
            ),
            _format_log_line(
                start,
                (
                    "IZ5TEST: EchoLink QSO state changed "
                    "to CONNECTED"
                ),
            ),
            _format_log_line(
                start + timedelta(seconds=3),
                (
                    "IZ5TEST: EchoLink QSO state changed "
                    "to DISCONNECTED"
                ),
            ),
            _format_log_line(
                start + timedelta(seconds=6),
                (
                    "Incoming EchoLink connection from "
                    "IZ5TEST (TEST) at 192.0.2.30"
                ),
            ),
            _format_log_line(
                start + timedelta(seconds=7),
                (
                    "IZ5TEST: EchoLink QSO state changed "
                    "to CONNECTED"
                ),
            ),
            _format_log_line(
                start + timedelta(seconds=10),
                (
                    "IZ5TEST: EchoLink QSO state changed "
                    "to DISCONNECTED"
                ),
            ),
        ],
    )

    monitor = EchoLinkMonitor(
        log_file=log_file
    )

    state = NodeState()

    monitor.check(state)

    assert len(
        state.echolink_recent_connections
    ) == 2

    newest_session = (
        state.echolink_recent_connections[0]
    )

    assert newest_session["station"] == "IZ5TEST"
    assert newest_session["duration_seconds"] == 3
    assert newest_session["unstable"] is True
