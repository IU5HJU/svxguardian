"""
SVX Guardian

Application entry point.
"""

from .core.bootstrap import BootstrapEngine
from .core.console import ConsoleRenderer
from .core.guardian import Guardian
from .modules.echolink import EchoLinkMonitor
from .modules.svxlink import SvxLinkMonitor
from .modules.system import SystemMonitor


def main() -> None:
    """
    Application entry point.
    """

    BootstrapEngine().run()

    guardian = Guardian()

    guardian.register(SystemMonitor())
    guardian.register(SvxLinkMonitor())
    guardian.register(EchoLinkMonitor())

    guardian.run()

    ConsoleRenderer().show(
        guardian.state,
        len(guardian.monitors),
    )


if __name__ == "__main__":
    main()
