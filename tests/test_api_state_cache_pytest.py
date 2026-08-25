"""
Shared /api/state snapshot cache tests.
"""

from src.web.app import (
    app,
    guardian,
)


def test_api_state_reuses_recent_guardian_snapshot(
    monkeypatch,
) -> None:
    """
    Consecutive /api/state requests inside the cache window
    must share one Guardian monitoring cycle.
    """

    run_count = 0

    def fake_guardian_run() -> None:
        nonlocal run_count
        run_count += 1

    monkeypatch.setattr(
        guardian,
        "run",
        fake_guardian_run,
    )

    with app.test_client() as client:
        first_response = client.get(
            "/api/state"
        )

        second_response = client.get(
            "/api/state"
        )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    assert run_count == 1


def test_api_state_refreshes_expired_snapshot(
    monkeypatch,
) -> None:
    """
    An expired /api/state snapshot must execute a new Guardian
    monitoring cycle.
    """

    import src.web.app as web_app

    run_count = 0

    def fake_guardian_run() -> None:
        nonlocal run_count
        run_count += 1

    monkeypatch.setattr(
        guardian,
        "run",
        fake_guardian_run,
    )

    monkeypatch.setattr(
        web_app,
        "API_STATE_CACHE_SECONDS",
        0.0,
    )

    with app.test_client() as client:
        first_response = client.get(
            "/api/state"
        )

        second_response = client.get(
            "/api/state"
        )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    assert run_count == 2
