"""
Controllo dello stato EchoLink.
"""

from logfile import read_last_lines


def is_registered():

    lines = read_last_lines()

    for line in reversed(lines):

        if "EchoLink directory status changed to ON" in line:
            return True

    return False
