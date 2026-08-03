"""
SVX Guardian Web Application

Main Flask application.
"""

from flask import Flask, jsonify, render_template

from ..core.exporter import StateExporter
from ..core.guardian import Guardian
from ..modules.svxlink import SvxLinkMonitor
from ..modules.system import SystemMonitor


app = Flask(__name__)

guardian = Guardian()
guardian.register(SystemMonitor())
guardian.register(SvxLinkMonitor())


@app.route("/")
def dashboard():
    """
    Render the main dashboard.
    """

    guardian.run()

    return render_template(
        "dashboard/dashboard.html",
        state=guardian.state,
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
