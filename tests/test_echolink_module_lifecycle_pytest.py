"""
Tests for EchoLink module lifecycle consistency.

The latest meaningful EchoLink event must determine whether
active station state is valid after a module deactivation.
"""

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


def test_deactivation_clears_previous_connected_station(
    tmp_path: Path,
) -> None:
    """
    A module deactivation newer than CONNECTED must invalidate
    the previously connected EchoLink station.
    """

    log_file = tmp_path / "svxlink.log"

    _write_log(
        log_file,
        [
            (
                "Sat Aug 22 12:00:00 2026: "
                "IU5HJU: EchoLink QSO state changed "
                "to CONNECTED"
            ),
            (
                "Sat Aug 22 12:00:05 2026: "
                "Deactivating module EchoLink..."
            ),
        ],
    )

    monitor = EchoLinkMonitor(
        log_file=log_file
    )

    state = NodeState()

    monitor.check(state)

    assert state.echolink_connected_stations == []
    assert state.echolink_connection_count == 0


def test_connected_after_deactivation_restores_active_station(
    tmp_path: Path,
) -> None:
    """
    A real CONNECTED event newer than module deactivation proves
    that EchoLink is operational again and must not be discarded.
    """

    log_file = tmp_path / "svxlink.log"

    _write_log(
        log_file,
        [
            (
                "Sat Aug 22 12:00:00 2026: "
                "Deactivating module EchoLink..."
            ),
            (
                "Sat Aug 22 12:00:05 2026: "
                "IU5HJU: EchoLink QSO state changed "
                "to CONNECTED"
            ),
        ],
    )

    monitor = EchoLinkMonitor(
        log_file=log_file
    )

    state = NodeState()

    monitor.check(state)

    assert state.echolink_connected_stations == [
        "IU5HJU"
    ]
    assert state.echolink_connection_count == 1


def test_rx_start_marks_connected_station_as_transmitting(
    tmp_path: Path,
) -> None:
    """
    RX_START must mark the current EchoLink station as
    transmitting.
    """

    log_file = tmp_path / "svxlink.log"

    _write_log(
        log_file,
        [
            (
                "Sat Aug 22 12:00:00 2026: "
                "IU5HJU: EchoLink QSO state changed "
                "to CONNECTED"
            ),
            (
                "Sat Aug 22 12:00:05 2026: "
                "SVXGUARDIAN_ECHOLINK_RX_START IU5HJU"
            ),
        ],
    )

    monitor = EchoLinkMonitor(
        log_file=log_file
    )

    state = NodeState()

    monitor.check(state)

    assert state.echolink_transmitting is True
    assert (
        state.echolink_transmitting_station
        == "IU5HJU"
    )
    assert "IU5HJU" in state.echolink_connected_stations


def test_rx_stop_returns_station_to_non_transmitting_state(
    tmp_path: Path,
) -> None:
    """
    A relevant RX_STOP must end transmission while preserving
    operational station presence.
    """

    log_file = tmp_path / "svxlink.log"

    _write_log(
        log_file,
        [
            (
                "Sat Aug 22 12:00:00 2026: "
                "IU5HJU: EchoLink QSO state changed "
                "to CONNECTED"
            ),
            (
                "Sat Aug 22 12:00:05 2026: "
                "SVXGUARDIAN_ECHOLINK_RX_START IU5HJU"
            ),
            (
                "Sat Aug 22 12:00:10 2026: "
                "SVXGUARDIAN_ECHOLINK_RX_STOP IU5HJU"
            ),
        ],
    )

    monitor = EchoLinkMonitor(
        log_file=log_file
    )

    state = NodeState()

    monitor.check(state)

    assert state.echolink_transmitting is False
    assert state.echolink_transmitting_station == ""
    assert "IU5HJU" in state.echolink_connected_stations


def test_rx_start_restores_operational_station_after_disconnect(
    tmp_path: Path,
) -> None:
    """
    RX_START is direct evidence of operational presence even
    after a temporary DISCONNECTED state.
    """

    log_file = tmp_path / "svxlink.log"

    _write_log(
        log_file,
        [
            (
                "Sat Aug 22 12:00:00 2026: "
                "IU5HJU: EchoLink QSO state changed "
                "to CONNECTED"
            ),
            (
                "Sat Aug 22 12:00:05 2026: "
                "IU5HJU: EchoLink QSO state changed "
                "to DISCONNECTED"
            ),
            (
                "Sat Aug 22 12:00:10 2026: "
                "SVXGUARDIAN_ECHOLINK_RX_START IU5HJU"
            ),
        ],
    )

    monitor = EchoLinkMonitor(
        log_file=log_file
    )

    state = NodeState()

    monitor.check(state)

    assert state.echolink_transmitting is True
    assert (
        state.echolink_transmitting_station
        == "IU5HJU"
    )
    assert "IU5HJU" in state.echolink_connected_stations


def test_historical_rx_stop_does_not_override_new_connection(
    tmp_path: Path,
) -> None:
    """
    An RX_STOP older than the latest CONNECTED event must not
    affect the new operational episode.
    """

    log_file = tmp_path / "svxlink.log"

    _write_log(
        log_file,
        [
            (
                "Sat Aug 22 12:00:00 2026: "
                "SVXGUARDIAN_ECHOLINK_RX_STOP IU5HJU"
            ),
            (
                "Sat Aug 22 12:00:05 2026: "
                "IU5HJU: EchoLink QSO state changed "
                "to CONNECTED"
            ),
        ],
    )

    monitor = EchoLinkMonitor(
        log_file=log_file
    )

    state = NodeState()

    monitor.check(state)

    assert state.echolink_transmitting is False
    assert state.echolink_transmitting_station == ""
    assert state.echolink_connected_stations == [
        "IU5HJU"
    ]
    assert state.echolink_connection_count == 1
