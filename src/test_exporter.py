"""
State Exporter diagnostic script.

This module is intended for manual execution and is not part
of the automated pytest test suite.
"""

import json

from .core.exporter import StateExporter
from .core.guardian import Guardian
from .modules.svxlink import SvxLinkMonitor
from .modules.system import SystemMonitor


# Prevent pytest from treating this diagnostic module as a test container.
__test__ = False


def main() -> None:
    """
    Run Guardian and display NodeState as a JSON dictionary.
    """

    guardian = Guardian()

    guardian.register(SystemMonitor())
    guardian.register(SvxLinkMonitor())

    guardian.run()

    data = StateExporter.to_dict(
        guardian.state
    )

    print("=" * 60)
    print("NodeState exported as dictionary")
    print("=" * 60)

    print(
        json.dumps(
            data,
            indent=4,
        )
    )


if __name__ == "__main__":
    main()
