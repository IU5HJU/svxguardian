"""
Funzioni per leggere il file di log di SvxLink.
"""

from pathlib import Path


LOGFILE = "/var/log/svxlink"


def read_last_lines(lines=100):
    """
    Restituisce le ultime righe del file di log.
    """

    logfile = Path(LOGFILE)

    if not logfile.exists():
        return []

    with logfile.open("r", encoding="utf-8", errors="ignore") as f:
        return f.readlines()[-lines:]
