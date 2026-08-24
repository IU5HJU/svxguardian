"""
SVX Guardian persistent settings tests.
"""

import json

from src.core.settings import SettingsManager


def test_settings_defaults_when_file_is_missing(
    tmp_path,
) -> None:
    """
    Missing settings.json must not break Guardian.

    Public dashboard settings must fall back to
    safe neutral defaults.
    """

    settings_file = (
        tmp_path
        / "settings.json"
    )

    manager = SettingsManager(
        settings_file=settings_file
    )

    settings = manager.load()

    assert settings["public_dashboard"] == {
        "reflector_name": "SvxReflector",
    }


def test_settings_loads_public_dashboard_name(
    tmp_path,
) -> None:
    settings_file = (
        tmp_path
        / "settings.json"
    )

    settings_file.write_text(
        json.dumps(
            {
                "public_dashboard": {
                    "reflector_name":
                        "Reflector Toscana",
                }
            }
        ),
        encoding="utf-8",
    )

    manager = SettingsManager(
        settings_file=settings_file
    )

    settings = manager.load()

    assert (
        settings[
            "public_dashboard"
        ][
            "reflector_name"
        ]
        == "Reflector Toscana"
    )


def test_settings_save_preserves_future_sections(
    tmp_path,
) -> None:
    """
    Saving one public-dashboard field must not destroy
    unrelated settings added in the future.
    """

    settings_file = (
        tmp_path
        / "settings.json"
    )

    settings_file.write_text(
        json.dumps(
            {
                "public_dashboard": {
                    "reflector_name":
                        "Old Reflector",
                },
                "notifications": {
                    "enabled": True,
                },
                "monitoring": {
                    "interval": 10,
                },
            }
        ),
        encoding="utf-8",
    )

    manager = SettingsManager(
        settings_file=settings_file
    )

    manager.update_section(
        "public_dashboard",
        {
            "reflector_name":
                "Reflector Toscana",
        },
    )

    saved = json.loads(
        settings_file.read_text(
            encoding="utf-8"
        )
    )

    assert saved[
        "public_dashboard"
    ][
        "reflector_name"
    ] == "Reflector Toscana"

    assert saved[
        "notifications"
    ] == {
        "enabled": True,
    }

    assert saved[
        "monitoring"
    ] == {
        "interval": 10,
    }
