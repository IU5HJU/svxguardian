"""
State Exporter test.
"""

import json

from exporter import StateExporter
from guardian import Guardian
from modules.system import SystemMonitor
from modules.svxlink import SvxLinkMonitor


def main() -> None:

    guardian = Guardian()

    guardian.register(SystemMonitor())
    guardian.register(SvxLinkMonitor())

    guardian.run()

    data = StateExporter.to_dict(guardian.state)

    print("=" * 60)
    print("NodeState exported as dictionary")
    print("=" * 60)

    print(json.dumps(data, indent=4))


if __name__ == "__main__":
    main()
