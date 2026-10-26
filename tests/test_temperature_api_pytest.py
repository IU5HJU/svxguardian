"""
/api/temperature and /temperature integration tests.
"""

from src.web.app import (
    app,
    temperature_logger,
)


def test_api_temperature_does_not_run_full_guardian(
    monkeypatch,
) -> None:
    """
    /api/temperature must only read the already-logged history.

    It must never execute Guardian.run().
    """

    import src.web.app as web_app

    def forbidden_guardian_run() -> None:
        raise AssertionError(
            "Guardian.run() must not be called "
            "by /api/temperature"
        )

    monkeypatch.setattr(
        web_app.guardian,
        "run",
        forbidden_guardian_run,
    )

    with app.test_client() as client:
        response = client.get(
            "/api/temperature"
        )

    assert response.status_code == 200

    data = response.get_json()

    assert "available" in data
    assert "samples" in data
    assert isinstance(data["samples"], list)


def test_temperature_logger_disabled_without_opt_in_env_var() -> None:
    """
    Under tests (no SVXGUARDIAN_ENABLE_TEMPERATURE_LOG set), the
    background sampler must never have started.

    This keeps test runs fully deterministic: no background
    thread competes with tests that monkeypatch Guardian.run().
    """

    assert temperature_logger.available is False


def test_temperature_page_renders_when_unavailable(
    monkeypatch,
) -> None:
    """
    /temperature must render gracefully when the background
    sampler has not started.
    """

    import src.web.app as web_app

    monkeypatch.setattr(
        web_app.guardian,
        "run",
        lambda: None,
    )

    with app.test_client() as client:
        response = client.get(
            "/temperature?lang=it"
        )

    assert response.status_code == 200
