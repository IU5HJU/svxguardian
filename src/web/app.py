"""
SVX Guardian Web Application.

Provides the web dashboard and REST API.
"""

from copy import deepcopy
import json
from pathlib import Path
from threading import RLock
from typing import Any

from flask import Flask, jsonify, render_template, request

from ..core.exporter import StateExporter
from ..core.guardian import Guardian
from ..core.i18n import TranslationManager
from ..modules.echolink import EchoLinkMonitor
from ..modules.reflector import ReflectorMonitor
from ..modules.svxlink import SvxLinkMonitor
from ..modules.system import SystemMonitor


app = Flask(__name__)

guardian = Guardian()
guardian.register(SystemMonitor())
guardian.register(SvxLinkMonitor())
guardian.register(EchoLinkMonitor())
guardian.register(ReflectorMonitor())

guardian_lock = RLock()


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCALE_DIRECTORY = PROJECT_ROOT / "locale"
LANGUAGES_FILE = LOCALE_DIRECTORY / "languages.json"


def load_languages() -> dict[str, dict[str, Any]]:
    """
    Load enabled interface languages.
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


def build_page_context() -> dict[str, Any]:
    """
    Build an isolated snapshot for rendering a web page.
    """

    with guardian_lock:
        guardian.run()

        state_snapshot = deepcopy(guardian.state)
        node_snapshot = deepcopy(guardian.node_info)

    languages = load_languages()
    language = get_language(languages)
    translator = TranslationManager(language)

    return {
        "state": state_snapshot,
        "node": node_snapshot,
        "language": language,
        "languages": languages,
        "t": translator.gettext,
    }


def export_node_info(node: Any) -> dict[str, Any]:
    """
    Export static node information as a dictionary.
    """

    return {
        "callsign": node.callsign,
        "description": node.description,
        "node_location": node.node_location,
        "node_class": node.node_class,
        "hidden": node.hidden,
        "sysop": node.sysop,
        "qth": node.qth,
        "locator": node.locator,
        "latitude": node.latitude,
        "longitude": node.longitude,
        "rx_name": node.rx_name,
        "rx_frequency": node.rx_frequency,
        "rx_sql_type": node.rx_sql_type,
        "rx_ctcss_frequencies": node.rx_ctcss_frequencies,
        "tx_name": node.tx_name,
        "tx_frequency": node.tx_frequency,
        "tx_power": node.tx_power,
        "tx_ctcss_frequency": node.tx_ctcss_frequency,
        "ctcss": node.ctcss,
        "echolink_number": node.echolink_number,
        "reflector_configured": node.reflector_configured,
        "reflector_hosts": node.reflector_hosts,
        "reflector_port": node.reflector_port,
        "reflector_default_tg": node.reflector_default_tg,
        "reflector_mode": node.reflector_mode,
        "reflector_logic_name": node.reflector_logic_name,
        "reflector": node.reflector,
        "logics": node.logics,
        "modules": node.modules,
        "tone_to_talkgroup": node.tone_to_talkgroup,
        "svxlink_version": node.svxlink_version,
        "config_file": node.config_file,
        "node_info_file": node.node_info_file,
    }


@app.route("/")
def dashboard():
    """
    Render the general dashboard.
    """

    return render_template(
        "dashboard/dashboard.html",
        **build_page_context(),
    )


@app.route("/monitor")
def operational_monitor():
    """
    Render the simplified mobile operational view.
    """

    return render_template(
        "dashboard/monitor.html",
        **build_page_context(),
    )


@app.route("/system")
def system_page():
    """
    Render detailed operating-system information.
    """

    return render_template(
        "dashboard/system.html",
        **build_page_context(),
    )


@app.route("/svxlink")
def svxlink_page():
    """
    Render detailed SvxLink information.
    """

    return render_template(
        "dashboard/svxlink.html",
        **build_page_context(),
    )


@app.route("/echolink")
def echolink_page():
    """
    Render detailed EchoLink information.
    """

    return render_template(
        "dashboard/echolink.html",
        **build_page_context(),
    )


@app.route("/reflector")
def reflector_page():
    """
    Render detailed Reflector information.
    """

    return render_template(
        "dashboard/reflector.html",
        **build_page_context(),
    )


@app.route("/configuration")
def configuration_page():
    """
    Render the restricted node-control page.

    Operational commands are intentionally not implemented here yet.
    They will be enabled only after authentication and authorization
    for Sysop and Co-Sysop roles are available.
    """

    return render_template(
        "dashboard/configuration.html",
        **build_page_context(),
    )


@app.route("/api/state")
def api_state():
    """
    Return an isolated current-state snapshot as JSON.
    """

    with guardian_lock:
        guardian.run()

        state_snapshot = deepcopy(guardian.state)
        node_snapshot = deepcopy(guardian.node_info)

    data = StateExporter.to_dict(state_snapshot)
    data["node"] = export_node_info(node_snapshot)

    return jsonify(data)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False,
    )
