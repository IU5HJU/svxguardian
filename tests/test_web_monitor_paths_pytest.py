"""
Web monitor path integration tests.
"""

from src.modules.echolink import EchoLinkMonitor
from src.modules.reflector import ReflectorMonitor
from src.web.app import guardian


def test_web_monitors_use_guardian_detected_log_file() -> None:
    """
    EchoLink and Reflector monitors used by the web application
    must use the logfile path detected by Guardian.
    """

    expected_log_file = (
        guardian.config.SVXLINK_LOG_FILE
    )

    echolink_monitor = next(
        monitor
        for monitor in guardian.monitors
        if isinstance(
            monitor,
            EchoLinkMonitor,
        )
    )

    reflector_monitor = next(
        monitor
        for monitor in guardian.monitors
        if isinstance(
            monitor,
            ReflectorMonitor,
        )
    )

    assert (
        echolink_monitor.log_file
        == expected_log_file
    )

    assert (
        reflector_monitor.log_file
        == expected_log_file
    )
