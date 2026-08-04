"""
SVX Guardian Web Application

Main Flask application.
"""

import json
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request

from ..core.exporter import StateExporter
from ..core.guardian import Guardian
from ..core.i18n import TranslationManager
from ..modules.svxlink import SvxLinkMonitor
from ..modules.system import SystemMonitor


app = Flask(__name__)

guardian = Guardian()
guardian.register(SystemMonitor())
guardian.register(SvxLinkMonitor())


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCALE_DIRECTORY = PROJECT_ROOT / "locale"
LANGUAGES_FILE = LOCALE_DIRECTORY / "languages.json"


def load_languages() -> dict[str, dict[str, Any]]:
    """
    Load enabled languages from locale/languages.json.
    """

    fallback_languages = {
        "en": {
            "name": "English",
            "native_name": "English",
            "enabled": True,
        }
    }

    if not LANGUAGES_FILE.is_file():
        return fallback_languages

    try:
        with LANGUAGES_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)
    except (
        OSError,
        json.JSONDecodeError,
    ):
        return fallback_languages

    if not isinstance(data, dict):
        return fallback_languages

    enabled_languages: dict[str, dict[str, Any]] = {}

    for language_code, metadata in data.items():
        if not isinstance(language_code, str):
            continue

        if not isinstance(metadata, dict):
            continue

        if metadata.get("enabled") is not True:
            continue

        locale_file = LOCALE_DIRECTORY / f"{language_code}.json"

        if not locale_file.is_file():
            continue

        enabled_languages[language_code] = metadata

    return enabled_languages or fallback_languages


def get_language(
    languages: dict[str, dict[str, Any]],
) -> str:
    """
    Return the requested interface language.
    """

    requested_language = request.args.get(
        "lang",
        "it",
    ).lower()

    if requested_language in languages:
        return requested_language

    if "en" in languages:
        return "en"

    return next(iter(languages))


@app.route("/")
def dashboard():
    """
    Render the main dashboard.
    """

    guardian.run()

    languages = load_languages()
    language = get_language(languages)
    translator = TranslationManager(language)

    return render_template(
        "dashboard/dashboard.html",
        state=guardian.state,
        node=guardian.node_info,
        language=language,
        languages=languages,
        t=translator.gettext,
    )


@app.route("/api/state")
def api_state():
    """
    Return the current node state as JSON.
    """

    guardian.run()

    data = StateExporter.to_dict(guardian.state)

    data["node"] = {
        "callsign": guardian.node_info.callsign,
        "description": guardian.node_info.description,
        "qth": guardian.node_info.qth,
        "locator": guardian.node_info.locator,
        "rx_frequency": guardian.node_info.rx_frequency,
        "tx_frequency": guardian.node_info.tx_frequency,
        "ctcss": guardian.node_info.ctcss,
        "echolink_number": guardian.node_info.echolink_number,
        "reflector": guardian.node_info.reflector,
        "modules": guardian.node_info.modules,
        "svxlink_version": guardian.node_info.svxlink_version,
        "config_file": guardian.node_info.config_file,
    }

    return jsonify(data)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False,
    )
