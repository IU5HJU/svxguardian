"""
SvxLink logfile service tests.
"""

from pathlib import Path

from src.services.logfile import read_last_lines


def test_read_last_lines_accepts_custom_log_file(
    tmp_path,
) -> None:
    """
    The logfile service must read from a custom SvxLink
    logfile path when explicitly provided.
    """

    log_file = tmp_path / "svxlink.log"

    log_file.write_text(
        "line 1\n"
        "line 2\n"
        "line 3\n",
        encoding="utf-8",
    )

    result = read_last_lines(
        lines=2,
        log_file=log_file,
    )

    assert result == [
        "line 2\n",
        "line 3\n",
    ]

    assert Path(log_file).is_file()


def test_read_last_lines_returns_empty_for_missing_file(
    tmp_path,
) -> None:
    """
    A missing logfile must not raise an exception.
    """

    log_file = tmp_path / "missing-svxlink.log"

    result = read_last_lines(
        log_file=log_file,
    )

    assert result == []
