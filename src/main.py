"""
SVX Guardian

Application entry point.
"""

from .core.guardian import Guardian
from .modules.svxlink import SvxLinkMonitor
from .modules.system import SystemMonitor


def main() -> None:
    """
    Application entry point.
    """

    guardian = Guardian()

    guardian.register(SystemMonitor())
    guardian.register(SvxLinkMonitor())

    guardian.run()

    state = guardian.state

    print("=" * 60)
    print("SVX Guardian v0.2.0-dev")
    print("=" * 60)

    print(f"Hostname      : {state.hostname}")
    print(f"CPU Temp      : {state.cpu_temp:.1f} °C")
    print(f"CPU Usage     : {state.cpu_usage:.1f} %")
    print(f"RAM Usage     : {state.ram_usage:.1f} %")
    print(f"Disk Usage    : {state.disk_usage:.1f} %")
    print(f"Uptime        : {state.uptime}")

    print("-" * 60)

    print(
        f"SvxLink       : "
        f"{'RUNNING' if state.svxlink_running else 'STOPPED'}"
    )

    print(f"Health        : {state.health}")
    print(f"Reason        : {state.health_reason}")

    print("-" * 60)

    print(f"Monitors      : {len(guardian.monitors)}")
    print("SVX Guardian ready.")


if __name__ == "__main__":
    main()
