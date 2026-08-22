"""
Lightweight live system API tests.
"""

from src.web.app import (
    app,
    guardian,
    live_system_monitor,
)


def test_api_system_does_not_run_full_guardian(
    monkeypatch,
) -> None:
    """
    /api/system must collect only operating-system metrics.

    The endpoint must never execute Guardian.run(), because
    doing so would also execute SvxLink, EchoLink, Reflector
    and logfile monitoring.
    """

    def forbidden_guardian_run() -> None:
        raise AssertionError(
            "Guardian.run() must not be called "
            "by /api/system"
        )

    def fake_system_check(state) -> None:
        state.hostname = "svx-test"
        state.cpu_temp = 42.5
        state.cpu_usage = 12.3
        state.ram_usage = 34.5
        state.disk_usage = 56.7
        state.uptime = "1d 2h 3m"

    monkeypatch.setattr(
        guardian,
        "run",
        forbidden_guardian_run,
    )

    monkeypatch.setattr(
        live_system_monitor,
        "check",
        fake_system_check,
    )

    with app.test_client() as client:
        response = client.get(
            "/api/system"
        )

    assert response.status_code == 200

    assert response.get_json() == {
        "hostname": "svx-test",
        "cpu_temp": 42.5,
        "cpu_usage": 12.3,
        "ram_usage": 34.5,
        "disk_usage": 56.7,
        "uptime": "1d 2h 3m",
    }
