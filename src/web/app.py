"""
SVX Guardian Web Application.

Provides the web dashboard, authentication interface
and REST API.
"""

from copy import deepcopy
import json
from pathlib import Path
import secrets
from threading import RLock
from typing import Any

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from ..core.exporter import StateExporter
from ..core.guardian import Guardian
from ..core.i18n import TranslationManager
from ..core.node_control import NodeControl
from ..core.settings import SettingsManager
from ..core.state import NodeState
from ..modules.echolink import EchoLinkMonitor
from ..modules.reflector import ReflectorMonitor
from ..modules.svxlink import SvxLinkMonitor
from ..modules.system import SystemMonitor
from ..services.logfile import IncrementalLogReader
from .auth import (
    AUTH_FILE,
    authenticate,
    get_current_user,
    login_user,
    logout_user,
)


app = Flask(__name__)


# ============================================================
# Private runtime configuration
# ============================================================

PRIVATE_CONFIG_DIRECTORY = Path(
    "/etc/svxguardian"
)


SECRET_KEY_FILE = (
    PRIVATE_CONFIG_DIRECTORY
    / "secret.key"
)


def load_secret_key() -> str | None:
    """
    Load the persistent Flask session signing key.

    The key is intentionally stored outside the Git repository.

    If the key is missing, unreadable or clearly invalid,
    authentication remains unavailable instead of creating
    a temporary key.
    """

    if not SECRET_KEY_FILE.is_file():
        return None

    try:
        secret_key = SECRET_KEY_FILE.read_text(
            encoding="utf-8",
        ).strip()

    except OSError:
        return None

    if len(secret_key) < 32:
        return None

    return secret_key


SESSION_SECRET_KEY = load_secret_key()


app.config.update(
    SECRET_KEY=SESSION_SECRET_KEY,

    SESSION_COOKIE_NAME="svxguardian_session",
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)


# ============================================================
# Guardian engine
# ============================================================

guardian = Guardian()
settings_manager = SettingsManager()

guardian.register(
    SystemMonitor()
)

# Lightweight non-blocking sampler used exclusively by the
# live system web endpoint. It does not execute Guardian.run()
# and therefore does not touch SvxLink, EchoLink, Reflector
# or operational log monitoring.
live_system_monitor = SystemMonitor(
    cpu_interval=None
)

guardian.register(
    SvxLinkMonitor()
)

guardian.register(
    EchoLinkMonitor(
        log_file=guardian.config.SVXLINK_LOG_FILE
    )
)

guardian.register(
    ReflectorMonitor(
        log_file=guardian.config.SVXLINK_LOG_FILE
    )
)


guardian_lock = RLock()
operational_log = IncrementalLogReader(
    log_file=guardian.config.SVXLINK_LOG_FILE,
    history_limit=1000,
    initial_lines=200,
)

# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)


LOCALE_DIRECTORY = (
    PROJECT_ROOT
    / "locale"
)


LANGUAGES_FILE = (
    LOCALE_DIRECTORY
    / "languages.json"
)


# ============================================================
# Authentication / CSRF
# ============================================================

CSRF_SESSION_KEY = (
    "svxguardian_csrf_token"
)


CONTROL_RESULT_SESSION_KEY = (
    "svxguardian_control_result"
)


def authentication_available() -> bool:
    """
    Return whether the authentication infrastructure
    is available on this installation.

    Public monitoring continues to work when authentication
    is unavailable.
    """

    if not SESSION_SECRET_KEY:
        return False

    if not AUTH_FILE.is_file():
        return False

    return True


def get_csrf_token() -> str:
    """
    Return the CSRF token associated with the current session.

    A token is generated only when authentication is available.
    """

    if not authentication_available():
        return ""

    token = session.get(
        CSRF_SESSION_KEY
    )

    if isinstance(token, str) and token:
        return token

    token = secrets.token_urlsafe(32)

    session[CSRF_SESSION_KEY] = token

    return token


def validate_csrf_token(
    submitted_token: str,
) -> bool:
    """
    Validate a submitted CSRF token.
    """

    if not authentication_available():
        return False

    stored_token = session.get(
        CSRF_SESSION_KEY
    )

    if not isinstance(
        stored_token,
        str,
    ):
        return False

    if not isinstance(
        submitted_token,
        str,
    ):
        return False

    if not stored_token:
        return False

    if not submitted_token:
        return False

    return secrets.compare_digest(
        stored_token,
        submitted_token,
    )


# ============================================================
# Languages
# ============================================================

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

    enabled_languages: dict[
        str,
        dict[str, Any],
    ] = {}

    for (
        language_code,
        metadata,
    ) in data.items():

        if not isinstance(
            language_code,
            str,
        ):
            continue

        if not isinstance(
            metadata,
            dict,
        ):
            continue

        if metadata.get(
            "enabled"
        ) is not True:
            continue

        locale_file = (
            LOCALE_DIRECTORY
            / f"{language_code}.json"
        )

        if not locale_file.is_file():
            continue

        enabled_languages[
            language_code
        ] = metadata

    return (
        enabled_languages
        or fallback_languages
    )


def normalize_language(
    requested_language: str,
    languages: dict[str, dict[str, Any]],
) -> str:
    """
    Validate an interface language code.
    """

    requested_language = (
        requested_language
        .strip()
        .lower()
    )

    if requested_language in languages:
        return requested_language

    if "en" in languages:
        return "en"

    return next(
        iter(languages)
    )


def get_language(
    languages: dict[str, dict[str, Any]],
) -> str:
    """
    Return the requested interface language.
    """

    requested_language = request.args.get(
        "lang",
        "it",
    )

    return normalize_language(
        requested_language,
        languages,
    )


# ============================================================
# Page context
# ============================================================

def build_page_context() -> dict[str, Any]:
    """
    Build an isolated snapshot for rendering a web page.
    """

    with guardian_lock:
        guardian.run()

        state_snapshot = deepcopy(
            guardian.state
        )

        node_snapshot = deepcopy(
            guardian.node_info
        )

    languages = load_languages()

    language = get_language(
        languages
    )

    translator = TranslationManager(
        language
    )

    current_user = (
        get_current_user()
        if authentication_available()
        else None
    )

    settings = settings_manager.load()

    public_dashboard_settings = settings.get(
        "public_dashboard",
        {},
    )

    return {
        "state": state_snapshot,
        "node": node_snapshot,

        "language": language,
        "languages": languages,

        "t": translator.gettext,

        "authentication_available":
            authentication_available(),

        "current_user":
            current_user,

        "authenticated":
            current_user is not None,

        "can_control_node":
            (
                current_user.can_control_node
                if current_user
                else False
            ),

        "public_dashboard_settings":
            public_dashboard_settings,
    }


# ============================================================
# API export helpers
# ============================================================

def export_node_info(
    node: Any,
) -> dict[str, Any]:
    """
    Export static node information as a dictionary.
    """

    return {
        "callsign":
            node.callsign,

        "description":
            node.description,

        "node_location":
            node.node_location,

        "node_class":
            node.node_class,

        "hidden":
            node.hidden,

        "sysop":
            node.sysop,

        "qth":
            node.qth,

        "locator":
            node.locator,

        "latitude":
            node.latitude,

        "longitude":
            node.longitude,

        "rx_name":
            node.rx_name,

        "rx_frequency":
            node.rx_frequency,

        "rx_sql_type":
            node.rx_sql_type,

        "rx_ctcss_frequencies":
            node.rx_ctcss_frequencies,

        "tx_name":
            node.tx_name,

        "tx_frequency":
            node.tx_frequency,

        "tx_power":
            node.tx_power,

        "tx_ctcss_frequency":
            node.tx_ctcss_frequency,

        "ctcss":
            node.ctcss,

        "echolink_number":
            node.echolink_number,

        "reflector_configured":
            node.reflector_configured,

        "reflector_hosts":
            node.reflector_hosts,

        "reflector_port":
            node.reflector_port,

        "reflector_default_tg":
            node.reflector_default_tg,

        "reflector_mode":
            node.reflector_mode,

        "reflector_logic_name":
            node.reflector_logic_name,

        "reflector":
            node.reflector,

        "logics":
            node.logics,

        "modules":
            node.modules,

        "tone_to_talkgroup":
            node.tone_to_talkgroup,

        "svxlink_version":
            node.svxlink_version,

        "config_file":
            node.config_file,

        "node_info_file":
            node.node_info_file,
    }


# ============================================================
# Dashboard routes
# ============================================================

@app.route("/dashboard")
def dashboard():
    """
    Render the Guardian control dashboard.
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


@app.route("/")
@app.route("/dashboard_pubblica")
def public_dashboard_page():
    """
    Render the public Reflector dashboard.
    """

    return render_template(
        "dashboard/dashboard_pubblica.html",
        **build_page_context(),
    )


@app.route("/info")
def info_page():
    """
    Render information about the SVX Guardian project.
    """

    return render_template(
        "dashboard/info.html",
        **build_page_context(),
    )


@app.route("/logs")
def logs_page():
    """
    Render the real-time SvxLink operational log.
    """

    return render_template(
        "dashboard/logs.html",
        **build_page_context(),
    )

# ============================================================
# Configuration
# ============================================================

@app.route("/configuration")
def configuration_page():
    """
    Render the node-control page.

    The page itself is public.

    Operational commands remain available only to an
    authenticated Sysop or Co-Sysop.
    """

    context = build_page_context()

    context["csrf_token"] = (
        get_csrf_token()
        if authentication_available()
        else ""
    )

    control_result = session.pop(
        CONTROL_RESULT_SESSION_KEY,
        None,
    )

    if isinstance(
        control_result,
        dict,
    ):
        context["control_result"] = (
            control_result
        )

    else:
        context["control_result"] = None

    return render_template(
        "dashboard/configuration.html",
        **context,
    )


# ============================================================
# Authentication
# ============================================================

@app.route(
    "/login",
    methods=[
        "GET",
        "POST",
    ],
)
def login():
    """
    Authenticate a Sysop or Co-Sysop.
    """

    context = build_page_context()

    language = context[
        "language"
    ]

    if not authentication_available():

        context["login_error"] = (
            "AUTH_NOT_CONFIGURED"
        )

        context["csrf_token"] = ""

        return render_template(
            "dashboard/login.html",
            **context,
        ), 503

    if request.method == "POST":

        submitted_csrf = (
            request.form.get(
                "csrf_token",
                "",
            )
        )

        if not validate_csrf_token(
            submitted_csrf
        ):

            context["login_error"] = (
                "AUTH_SESSION_INVALID"
            )

            context["csrf_token"] = (
                get_csrf_token()
            )

            return render_template(
                "dashboard/login.html",
                **context,
            ), 400

        username = request.form.get(
            "username",
            "",
        )

        password = request.form.get(
            "password",
            "",
        )

        user = authenticate(
            username,
            password,
        )

        if user is None:

            context["login_error"] = (
                "AUTH_INVALID_CREDENTIALS"
            )

            context["csrf_token"] = (
                get_csrf_token()
            )

            return render_template(
                "dashboard/login.html",
                **context,
            ), 401

        login_user(
            user
        )

        return redirect(
            url_for(
                "configuration_page",
                lang=language,
            )
        )

    context["login_error"] = ""

    context["csrf_token"] = (
        get_csrf_token()
    )

    return render_template(
        "dashboard/login.html",
        **context,
    )


@app.route(
    "/logout",
    methods=[
        "POST",
    ],
)
def logout():
    """
    End the current authenticated session.
    """

    languages = load_languages()

    requested_language = (
        request.form.get(
            "lang",
            "it",
        )
    )

    language = normalize_language(
        requested_language,
        languages,
    )

    if not authentication_available():

        return redirect(
            url_for(
                "configuration_page",
                lang=language,
            )
        )

    submitted_csrf = request.form.get(
        "csrf_token",
        "",
    )

    if not validate_csrf_token(
        submitted_csrf
    ):

        return redirect(
            url_for(
                "configuration_page",
                lang=language,
            )
        )

    logout_user()

    return redirect(
        url_for(
            "configuration_page",
            lang=language,
        )
    )


# ============================================================
# Public dashboard settings
# ============================================================

@app.route(
    "/configuration/public-dashboard",
    methods=[
        "POST",
    ],
)
def update_public_dashboard_settings():
    """
    Update persistent public-dashboard settings.

    The operation is available only to an authenticated
    Sysop or Co-Sysop and requires a valid CSRF token.
    """

    languages = load_languages()

    requested_language = request.form.get(
        "lang",
        "it",
    )

    language = normalize_language(
        requested_language,
        languages,
    )

    if not authentication_available():

        return redirect(
            url_for(
                "configuration_page",
                lang=language,
            )
        )

    current_user = get_current_user()

    if current_user is None:

        return redirect(
            url_for(
                "login",
                lang=language,
            )
        )

    if not current_user.can_control_node:

        return redirect(
            url_for(
                "configuration_page",
                lang=language,
            )
        )

    submitted_csrf = request.form.get(
        "csrf_token",
        "",
    )

    if not validate_csrf_token(
        submitted_csrf
    ):

        return redirect(
            url_for(
                "configuration_page",
                lang=language,
            )
        )

    reflector_name = (
        request.form.get(
            "reflector_name",
            "",
        )
        .strip()
    )

    if not reflector_name:
        reflector_name = "SvxReflector"

    settings_manager.update_section(
        "public_dashboard",
        {
            "reflector_name":
                reflector_name,
        },
    )

    return redirect(
        url_for(
            "configuration_page",
            lang=language,
        )
    )


# ============================================================
# Node control
# ============================================================

@app.route(
    "/control/svxlink/restart",
    methods=[
        "POST",
    ],
)
def restart_svxlink():
    """
    Restart the SvxLink service.

    The operation is available only to an authenticated
    Sysop or Co-Sysop and requires a valid CSRF token.

    The result stored in the session contains only information
    suitable for presentation by the web interface.
    """

    languages = load_languages()

    requested_language = request.form.get(
        "lang",
        "it",
    )

    language = normalize_language(
        requested_language,
        languages,
    )

    if not authentication_available():

        return redirect(
            url_for(
                "configuration_page",
                lang=language,
            )
        )

    current_user = get_current_user()

    if current_user is None:

        return redirect(
            url_for(
                "login",
                lang=language,
            )
        )

    if not current_user.can_control_node:

        return redirect(
            url_for(
                "configuration_page",
                lang=language,
            )
        )

    submitted_csrf = request.form.get(
        "csrf_token",
        "",
    )

    if not validate_csrf_token(
        submitted_csrf
    ):

        session[
            CONTROL_RESULT_SESSION_KEY
        ] = {
            "operation":
                "restart_svxlink",

            "success":
                False,

            "message":
                "invalid_request",
        }

        return redirect(
            url_for(
                "configuration_page",
                lang=language,
            )
        )

    result = (
        NodeControl.restart_svxlink()
    )

    session[
        CONTROL_RESULT_SESSION_KEY
    ] = {
        "operation":
            result.operation,

        "success":
            result.success,

        "message":
            result.message,

        "previous_pid":
            result.previous_pid,

        "current_pid":
            result.current_pid,
    }

    return redirect(
        url_for(
            "configuration_page",
            lang=language,
        )
    )


# ============================================================
# REST API
# ============================================================

@app.route("/api/logs")
def api_logs():
    """
    Return incremental SvxLink logfile entries.

    The optional "after" query parameter acts as a client cursor.
    Only entries with an ID greater than the supplied cursor are
    returned.

    This endpoint does not execute guardian.run(), so frequent
    logfile polling does not trigger the complete monitoring
    cycle.
    """

    after_value = request.args.get(
        "after",
        "0",
    )

    try:
        after_id = max(
            0,
            int(after_value),
        )

    except (
        TypeError,
        ValueError,
    ):
        after_id = 0

    entries = operational_log.get_entries(
        after_id=after_id,
        limit=200,
    )

    latest_id = (
        operational_log.get_latest_id()
    )

    return jsonify(
        {
            "entries": entries,
            "latest_id": latest_id,
        }
    )


@app.route("/api/system")
def api_system():
    """
    Return lightweight live operating-system metrics.

    This endpoint intentionally avoids Guardian.run().
    Only SystemMonitor is executed, preventing unnecessary
    SvxLink, EchoLink, Reflector and logfile processing.
    """

    state_snapshot = NodeState()

    live_system_monitor.check(
        state_snapshot
    )

    return jsonify(
        {
            "hostname":
                state_snapshot.hostname,

            "cpu_temp":
                state_snapshot.cpu_temp,

            "cpu_usage":
                state_snapshot.cpu_usage,

            "ram_usage":
                state_snapshot.ram_usage,

            "disk_usage":
                state_snapshot.disk_usage,

            "uptime":
                state_snapshot.uptime,
        }
    )


@app.route("/api/state")
def api_state():
    """
    Return an isolated current-state snapshot as JSON.
    """

    with guardian_lock:
        guardian.run()

        state_snapshot = deepcopy(
            guardian.state
        )

        node_snapshot = deepcopy(
            guardian.node_info
        )

    data = StateExporter.to_dict(
        state_snapshot
    )

    data["node"] = export_node_info(
        node_snapshot
    )

    return jsonify(
        data
    )


# ============================================================
# Development server
# ============================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False,
    )
