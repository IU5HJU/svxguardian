"""
SVX Guardian Web API

First REST API implementation.
"""

from flask import Flask, jsonify

from guardian import Guardian
from exporter import StateExporter
from modules.system import SystemMonitor
from modules.svxlink import SvxLinkMonitor

app = Flask(__name__)

guardian = Guardian()

guardian.register(SystemMonitor())
guardian.register(SvxLinkMonitor())


@app.route("/")
def home():
    """
    Simple welcome page.
    """
    return "<h1>SVX Guardian Web API</h1>"


@app.route("/api/state")
def api_state():
    """
    Returns current node state as JSON.
    """

    guardian.run()

    return jsonify(
        StateExporter.to_dict(guardian.state)
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False
    )
