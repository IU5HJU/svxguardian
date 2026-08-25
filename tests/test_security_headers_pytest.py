"""
HTTP security header tests.
"""

from src.web.app import (
    app,
    live_system_monitor,
)


def test_security_headers_are_present(
    monkeypatch,
) -> None:
    """
    Every application response must include the baseline
    HTTP security headers.
    """

    def fake_system_check(state) -> None:
        pass

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

    assert (
        response.headers["X-Frame-Options"]
        == "SAMEORIGIN"
    )

    assert (
        response.headers["X-Content-Type-Options"]
        == "nosniff"
    )
    assert (
        response.headers["Referrer-Policy"]
        == "same-origin"
    )

    assert (
        response.headers["Permissions-Policy"]
        == "camera=(), microphone=(), geolocation=()"
    )
