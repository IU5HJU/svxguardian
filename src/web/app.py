"""
SVX Guardian Web Application

Main Flask application.
"""

from flask import Flask, jsonify, render_template

from guardian import Guardian
from exporter import StateExporter

from modules.system import SystemMonitor
from modules.svxlink import SvxLinkMonitor


app = Flask(__name__)


# --------------------------------------------------------------------
# Guardian initialization
# --------------------------------------------------------------------

guardian = Guardian()

guardian.register(SystemMonitor())
guardian.register(SvxLinkMonitor())


# --------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------

@app.route("/")
def dashboard():
    """
    Main dashboard.
    """

    guardian.run()

    return render_template(
        "dashboard/dashboard.html",
        state=guardian.state
    )


@app.route("/api/state")
def api_state():
    """
    REST API.

    Returns current node status as JSON.
    """

    guardian.run()

    return jsonify(
        StateExporter.to_dict(
            guardian.state
        )
    )


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False
    )
