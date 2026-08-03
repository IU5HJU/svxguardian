"""
SVX Guardian Web Application

Main Flask application.
"""

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


def get_language() -> str:
    """
    Return the requested interface language.

    The language can be selected with:
    ?lang=it
    ?lang=en
    """

    language = request.args.get("lang", "it").lower()

    supported_languages = {
        "en",
        "it",
    }

    if language not in supported_languages:
        return "en"

    return language


@app.route("/")
def dashboard():
    """
    Render the main dashboard.
    """

    guardian.run()

    language = get_language()
    translator = TranslationManager(language)

    return render_template(
        "dashboard/dashboard.html",
        state=guardian.state,
        language=language,
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
