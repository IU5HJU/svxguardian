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
