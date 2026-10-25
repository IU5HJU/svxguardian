"""
Tests for the bounded backward log scan in ReflectorMonitor.

A neglected or oversized SvxLink logfile (no rotation configured)
must never turn an HTTP request into a multi-second full-file scan.
"""

from src.core.state import NodeState
from src.modules.reflector import ReflectorMonitor


def test_read_lines_reverse_without_bound_reads_whole_file(tmp_path):
    log_file = tmp_path / "svxlink.log"

    log_file.write_text(
        (
            "line one\n"
            "line two\n"
            "line three\n"
        ),
        encoding="utf-8",
    )

    monitor = ReflectorMonitor(
        log_file=log_file
    )

    lines = list(
        monitor._read_lines_reverse()
    )

    assert lines == [
        "line three",
        "line two",
        "line one",
    ]


def test_read_lines_reverse_stops_at_byte_budget(tmp_path):
    log_file = tmp_path / "svxlink.log"

    log_file.write_text(
        (
            "old filler line 01\n"
            "old filler line 02\n"
            "old filler line 03\n"
            "recent line four\n"
            "recent line five\n"
        ),
        encoding="utf-8",
    )

    monitor = ReflectorMonitor(
        log_file=log_file
    )

    lines = list(
        monitor._read_lines_reverse(
            max_bytes=40
        )
    )

    assert lines == [
        "recent line five",
        "recent line four",
    ]

    # The scan stopped before reaching the start of the file: no
    # truncated fragment of an older line is yielded.
    assert "old filler line 03" not in lines
    assert "old filler line 02" not in lines
    assert "old filler line 01" not in lines


def test_read_lines_reverse_yields_leftover_only_at_real_start(tmp_path):
    """
    A tiny budget that stops mid-block must not emit a truncated
    fragment of the oldest line as if it were a complete one.
    """

    log_file = tmp_path / "svxlink.log"

    log_file.write_text(
        "abcdefghij\n" * 5,
        encoding="utf-8",
    )

    monitor = ReflectorMonitor(
        log_file=log_file
    )

    lines = list(
        monitor._read_lines_reverse(
            max_bytes=5
        )
    )

    for line in lines:
        assert line == "abcdefghij"


def test_reflector_monitor_falls_back_to_unknown_beyond_scan_limit(
    tmp_path,
):
    """
    A huge, never-rotated logfile where the only connection marker
    lies far before the scan limit must not block the dashboard for
    as long as a full-file scan would take: the monitor reports
    UNKNOWN instead of scanning the entire file.
    """

    log_file = tmp_path / "svxlink.log"

    filler_line = (
        "Sun 23 Aug 2026 17:54:06 CEST: filler padding line\n"
    )

    with log_file.open("w", encoding="utf-8") as file:
        file.write(
            "Sun 23 Aug 2026 17:54:06 CEST: "
            "NOTICE[ReflectorLogic]: "
            "Connected to 192.168.1.36:5300 (primary)\n"
        )

        for _ in range(200):
            file.write(filler_line)

    monitor = ReflectorMonitor(
        log_file=log_file
    )

    # Force an early cutoff well before the connection marker, as a
    # neglected, oversized production logfile would also do against
    # the real MAX_BACKWARD_SCAN_BYTES default.
    monitor.MAX_BACKWARD_SCAN_BYTES = len(filler_line) * 10

    state = NodeState()

    monitor.check(state)

    assert state.reflector_status.value == "UNKNOWN"


def test_reflector_monitor_still_detects_connection_within_scan_limit(
    tmp_path,
):
    """
    The same scenario, but with the connection marker placed inside
    the (overridden, smaller) scan budget: detection must still work.
    """

    log_file = tmp_path / "svxlink.log"

    filler_line = (
        "Sun 23 Aug 2026 17:54:06 CEST: filler padding line\n"
    )

    with log_file.open("w", encoding="utf-8") as file:
        for _ in range(5):
            file.write(filler_line)

        file.write(
            "Sun 23 Aug 2026 17:54:06 CEST: "
            "NOTICE[ReflectorLogic]: "
            "Connected to 192.168.1.36:5300 (primary)\n"
        )

    monitor = ReflectorMonitor(
        log_file=log_file
    )

    monitor.MAX_BACKWARD_SCAN_BYTES = len(filler_line) * 10

    state = NodeState()

    monitor.check(state)

    assert state.reflector_status.value == "CONNECTED"
    assert state.reflector_host == "192.168.1.36"
    assert state.reflector_port == 5300
