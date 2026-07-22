"""
SVX Guardian

Application entry point.
"""

from guardian import Guardian
from modules.system import SystemMonitor


def main() -> None:
    """
    Application entry point.
    """

    guardian = Guardian()

    # Register monitors
    guardian.register(SystemMonitor())

    # Execute monitors
    guardian.run()

    state = guardian.state

    print("=" * 60)
    print("SVX Guardian v0.1.0")
    print("=" * 60)

    print(f"Hostname      : {state.hostname}")
    print(f"CPU Temp      : {state.cpu_temp:.1f} °C")
    print(f"CPU Usage     : {state.cpu_usage:.1f} %")
    print(f"RAM Usage     : {state.ram_usage:.1f} %")
    print(f"Disk Usage    : {state.disk_usage:.1f} %")
    print(f"Uptime        : {state.uptime}")

    print("-" * 60)
    print(f"Monitors      : {len(guardian.monitors)}")
    print("SVX Guardian ready.")


if __name__ == "__main__":
    main()
