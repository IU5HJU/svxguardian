"""
Public dashboard settings web tests.
"""

from pathlib import Path

from src.web.app import (
    app,
    settings_manager,
)


def test_public_dashboard_settings_require_authentication(
    monkeypatch,
    tmp_path,
) -> None:
    settings_file = tmp_path / "settings.json"

    monkeypatch.setattr(
        settings_manager,
        "settings_file",
        settings_file,
    )

    with app.test_client() as client:
        response = client.post(
            "/configuration/public-dashboard",
            data={
                "lang": "it",
                "csrf_token": "invalid",
                "reflector_name": "Reflector Toscana",
            },
            follow_redirects=False,
        )

    assert response.status_code == 302
    assert not settings_file.exists()


def test_public_dashboard_settings_save_when_authenticated(
    monkeypatch,
    tmp_path,
) -> None:
    settings_file = tmp_path / "settings.json"

    monkeypatch.setattr(
        settings_manager,
        "settings_file",
        settings_file,
    )

    monkeypatch.setattr(
        "src.web.app.authentication_available",
        lambda: True,
    )

    class FakeUser:
        can_control_node = True

    monkeypatch.setattr(
        "src.web.app.get_current_user",
        lambda: FakeUser(),
    )

    monkeypatch.setattr(
        "src.web.app.validate_csrf_token",
        lambda token: token == "valid-token",
    )

    with app.test_client() as client:
        response = client.post(
            "/configuration/public-dashboard",
            data={
                "lang": "it",
                "csrf_token": "valid-token",
                "reflector_name": "Reflector Toscana",
            },
            follow_redirects=False,
        )

    assert response.status_code == 302

    settings = settings_manager.load()

    assert (
        settings["public_dashboard"]["reflector_name"]
        == "Reflector Toscana"
    )


def test_public_dashboard_settings_preserve_future_fields(
    monkeypatch,
    tmp_path,
) -> None:
    settings_file = tmp_path / "settings.json"

    settings_file.write_text(
        """
{
    "public_dashboard": {
        "reflector_name": "Old Name",
        "description": "Future field"
    },
    "notifications": {
        "enabled": true
    }
}
""".strip(),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        settings_manager,
        "settings_file",
        settings_file,
    )

    monkeypatch.setattr(
        "src.web.app.authentication_available",
        lambda: True,
    )

    class FakeUser:
        can_control_node = True

    monkeypatch.setattr(
        "src.web.app.get_current_user",
        lambda: FakeUser(),
    )

    monkeypatch.setattr(
        "src.web.app.validate_csrf_token",
        lambda token: True,
    )

    with app.test_client() as client:
        response = client.post(
            "/configuration/public-dashboard",
            data={
                "lang": "it",
                "csrf_token": "valid-token",
                "reflector_name": "Reflector Toscana",
            },
            follow_redirects=False,
        )

    assert response.status_code == 302

    settings = settings_manager.load()

    assert (
        settings["public_dashboard"]["reflector_name"]
        == "Reflector Toscana"
    )

    assert (
        settings["public_dashboard"]["description"]
        == "Future field"
    )

    assert settings["notifications"] == {
        "enabled": True,
    }
