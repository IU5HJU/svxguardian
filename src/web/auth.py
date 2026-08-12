"""
SVX Guardian authentication support.

Authentication is intentionally independent from SvxLink.

Credentials are stored outside the Git repository in:

    /etc/svxguardian/auth.json

Only password hashes are stored.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from flask import session
from werkzeug.security import check_password_hash


AUTH_FILE = Path("/etc/svxguardian/auth.json")

ALLOWED_ROLES = {
    "sysop",
    "cosysop",
}

SESSION_USER_KEY = "svxguardian_user"
SESSION_ROLE_KEY = "svxguardian_role"


@dataclass(frozen=True)
class AuthenticatedUser:
    """
    Authenticated SVX Guardian user.
    """

    username: str
    role: str

    @property
    def can_control_node(self) -> bool:
        """
        Return whether the user may execute node-control commands.
        """

        return self.role in ALLOWED_ROLES


def _load_auth_data() -> dict[str, Any]:
    """
    Load authentication data from the private configuration file.

    Invalid or unavailable authentication data results in an empty
    user database. Authentication therefore fails closed.
    """

    if not AUTH_FILE.is_file():
        return {}

    try:
        with AUTH_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return {}

    if not isinstance(data, dict):
        return {}

    return data


def authenticate(
    username: str,
    password: str,
) -> AuthenticatedUser | None:
    """
    Validate username and password.

    Return an AuthenticatedUser on success, otherwise None.
    """

    username = username.strip()

    if not username or not password:
        return None

    data = _load_auth_data()

    users = data.get("users")

    if not isinstance(users, dict):
        return None

    user_data = users.get(username)

    if not isinstance(user_data, dict):
        return None

    role = user_data.get("role")
    password_hash = user_data.get("password_hash")

    if role not in ALLOWED_ROLES:
        return None

    if not isinstance(password_hash, str):
        return None

    if not password_hash:
        return None

    try:
        password_valid = check_password_hash(
            password_hash,
            password,
        )
    except (ValueError, TypeError):
        return None

    if not password_valid:
        return None

    return AuthenticatedUser(
        username=username,
        role=role,
    )


def login_user(
    user: AuthenticatedUser,
) -> None:
    """
    Store the authenticated identity in the Flask session.
    """

    session.clear()

    session[SESSION_USER_KEY] = user.username
    session[SESSION_ROLE_KEY] = user.role


def logout_user() -> None:
    """
    Remove the authenticated identity from the Flask session.
    """

    session.clear()


def get_current_user() -> AuthenticatedUser | None:
    """
    Return the currently authenticated user from the Flask session.

    Invalid session data is rejected.
    """

    username = session.get(SESSION_USER_KEY)
    role = session.get(SESSION_ROLE_KEY)

    if not isinstance(username, str):
        return None

    if not username:
        return None

    if role not in ALLOWED_ROLES:
        return None

    return AuthenticatedUser(
        username=username,
        role=role,
    )


def is_authenticated() -> bool:
    """
    Return whether the current request has an authenticated user.
    """

    return get_current_user() is not None


def can_control_node() -> bool:
    """
    Return whether the current authenticated user may control the node.
    """

    user = get_current_user()

    if user is None:
        return False

    return user.can_control_node
