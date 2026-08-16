"""
Functions for reading the SvxLink log file.
"""

from pathlib import Path


DEFAULT_LOG_FILE = Path("/var/log/svxlink")


def read_last_lines(
    lines: int = 100,
    log_file: Path | str = DEFAULT_LOG_FILE,
) -> list[str]:
    """
    Return the last lines from the SvxLink log file.
    """

    logfile = Path(log_file)

    if not logfile.is_file():
        return []

    try:
        with logfile.open(
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as file:
            return file.readlines()[-lines:]
    except OSError:
        return []
