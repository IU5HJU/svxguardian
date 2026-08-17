"""
Tests for the incremental SvxLink logfile reader.
"""

from pathlib import Path

from src.services.logfile import IncrementalLogReader


def _write(
    path: Path,
    text: str,
) -> None:
    """
    Write UTF-8 text to a test logfile.
    """

    path.write_text(
        text,
        encoding="utf-8",
    )


def _append(
    path: Path,
    text: str,
) -> None:
    """
    Append UTF-8 text to a test logfile.
    """

    with path.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            text
        )


def test_incremental_reader_loads_initial_tail(
    tmp_path: Path,
) -> None:
    """
    The first synchronization must load only the configured
    newest lines.
    """

    log_file = tmp_path / "svxlink.log"

    _write(
        log_file,
        (
            "line 1\n"
            "line 2\n"
            "line 3\n"
            "line 4\n"
        ),
    )

    reader = IncrementalLogReader(
        log_file=log_file,
        initial_lines=2,
        history_limit=20,
    )

    entries = reader.get_latest(
        limit=20
    )

    assert [
        entry["line"]
        for entry in entries
    ] == [
        "line 3",
        "line 4",
    ]

    assert [
        entry["id"]
        for entry in entries
    ] == [
        1,
        2,
    ]


def test_incremental_reader_reads_only_appended_lines(
    tmp_path: Path,
) -> None:
    """
    New synchronization must append only new logfile lines.
    """

    log_file = tmp_path / "svxlink.log"

    _write(
        log_file,
        (
            "old 1\n"
            "old 2\n"
        ),
    )

    reader = IncrementalLogReader(
        log_file=log_file,
        initial_lines=2,
        history_limit=20,
    )

    initial_entries = reader.get_latest(
        limit=20
    )

    assert len(
        initial_entries
    ) == 2

    _append(
        log_file,
        (
            "new 1\n"
            "new 2\n"
        ),
    )

    entries = reader.get_entries(
        after_id=2,
    )

    assert [
        entry["line"]
        for entry in entries
    ] == [
        "new 1",
        "new 2",
    ]

    assert [
        entry["id"]
        for entry in entries
    ] == [
        3,
        4,
    ]


def test_incremental_reader_handles_partial_line(
    tmp_path: Path,
) -> None:
    """
    An incomplete trailing line must not be emitted until its
    terminating newline arrives.
    """

    log_file = tmp_path / "svxlink.log"

    _write(
        log_file,
        "initial\n",
    )

    reader = IncrementalLogReader(
        log_file=log_file,
        initial_lines=1,
        history_limit=20,
    )

    reader.get_latest(
        limit=20
    )

    _append(
        log_file,
        "partial"
    )

    assert reader.get_entries(
        after_id=1,
    ) == []

    _append(
        log_file,
        " completed\n"
    )

    entries = reader.get_entries(
        after_id=1,
    )

    assert len(
        entries
    ) == 1

    assert entries[0]["line"] == (
        "partial completed"
    )


def test_incremental_reader_supports_independent_cursors(
    tmp_path: Path,
) -> None:
    """
    Two clients using different after_id values must receive
    independent event ranges from the same cached history.
    """

    log_file = tmp_path / "svxlink.log"

    _write(
        log_file,
        (
            "line 1\n"
            "line 2\n"
            "line 3\n"
            "line 4\n"
        ),
    )

    reader = IncrementalLogReader(
        log_file=log_file,
        initial_lines=4,
        history_limit=20,
    )

    reader.get_latest(
        limit=20
    )

    client_a = reader.get_entries(
        after_id=1,
    )

    client_b = reader.get_entries(
        after_id=3,
    )

    assert [
        entry["line"]
        for entry in client_a
    ] == [
        "line 2",
        "line 3",
        "line 4",
    ]

    assert [
        entry["line"]
        for entry in client_b
    ] == [
        "line 4",
    ]


def test_incremental_reader_respects_history_limit(
    tmp_path: Path,
) -> None:
    """
    In-memory history must remain bounded.
    """

    log_file = tmp_path / "svxlink.log"

    _write(
        log_file,
        (
            "line 1\n"
            "line 2\n"
            "line 3\n"
            "line 4\n"
            "line 5\n"
        ),
    )

    reader = IncrementalLogReader(
        log_file=log_file,
        initial_lines=5,
        history_limit=3,
    )

    entries = reader.get_latest(
        limit=20
    )

    assert [
        entry["line"]
        for entry in entries
    ] == [
        "line 3",
        "line 4",
        "line 5",
    ]


def test_incremental_reader_handles_log_truncation(
    tmp_path: Path,
) -> None:
    """
    Truncating the logfile must not crash the reader.

    Existing cached history remains available and the new logfile
    contents are loaded.
    """

    log_file = tmp_path / "svxlink.log"

    _write(
        log_file,
        (
            "old 1\n"
            "old 2\n"
        ),
    )

    reader = IncrementalLogReader(
        log_file=log_file,
        initial_lines=2,
        history_limit=20,
    )

    reader.get_latest(
        limit=20
    )

    _write(
        log_file,
        "new after truncation\n",
    )

    entries = reader.get_latest(
        limit=20
    )

    lines = [
        entry["line"]
        for entry in entries
    ]

    assert "old 1" in lines
    assert "old 2" in lines
    assert "new after truncation" in lines


def test_incremental_reader_clear_history_does_not_modify_file(
    tmp_path: Path,
) -> None:
    """
    Clearing Guardian's in-memory history must never alter the
    real SvxLink logfile.
    """

    log_file = tmp_path / "svxlink.log"

    original_text = (
        "line 1\n"
        "line 2\n"
    )

    _write(
        log_file,
        original_text,
    )

    reader = IncrementalLogReader(
        log_file=log_file,
        initial_lines=2,
        history_limit=20,
    )

    reader.get_latest(
        limit=20
    )

    reader.clear_history()

    assert reader.get_latest(
        limit=20
    ) == []

    assert log_file.read_text(
        encoding="utf-8",
    ) == original_text
