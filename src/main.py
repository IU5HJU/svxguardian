#!/usr/bin/env python3

"""
SVX Guardian
"""

import platform
from datetime import datetime

from config import SvxConfig

VERSION = "0.3.0"


def main():

    cfg = SvxConfig()
    cfg.load()

    print("=" * 60)
    print(f"SVX Guardian {VERSION}")
    print("=" * 60)

    print("Hostname :", platform.node())
    print("Date     :", datetime.now())

    print()
    print("===== SvxLink configuration =====")

    print("Callsign :", cfg.get("ReflectorLogic", "CALLSIGN"))
    print("Host     :", cfg.get("ReflectorLogic", "HOSTS"))
    print("TG       :", cfg.get("ReflectorLogic", "DEFAULT_TG"))
    print("Language :", cfg.get("ReflectorLogic", "DEFAULT_LANG"))

    print("=" * 60)


if __name__ == "__main__":
    main()
