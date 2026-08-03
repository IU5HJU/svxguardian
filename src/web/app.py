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

    if not LANGUAGES_FILE.exists():
        return {
            "en": {
                "name": "English",
                "native_name": "English",
                "enabled": True,
            }
        }

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
        return {
            "en": {
                "name": "English",
                "native_name": "English",
                "enabled": True,
            }
        }

    if not isinstance(data, dict):
        return {}

    enabled_languages: dict[str, dict[str, Any]] = {}

    for language_code, metadata in data.items():
        if not isinstance(language_code, str):
            continue

        if not isinstance(metadata, dict):
            continue

        if metadata.get("enabled") is not True:
            continue

        locale_file = LOCALE_DIRECTORY / f"{language_code}.json"

        if not locale_file.exists():
            continue

        enabled_languages[language_code] = metadata

    return enabled_languages


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

    if languages:
        return next(iter(languages))

    return "en"


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

    return jsonify(
        StateExporter.to_dict(guardian.state)
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False,
    )
