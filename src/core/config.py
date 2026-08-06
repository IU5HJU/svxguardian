"""
SVX Guardian configuration manager.

Provides centralized access to application configuration.
"""

from pathlib import Path


class ConfigManager:
    """
    Centralized configuration for SVX Guardian.
    """

    APPLICATION_NAME = "SVX Guardian"
    APPLICATION_VERSION = "0.2.0-dev"

    ROOT_DIRECTORY = Path("/")

    ETC_DIRECTORY = ROOT_DIRECTORY / "etc"

    SVXLINK_DIRECTORY = ETC_DIRECTORY / "svxlink"

    SVXLINK_CONFIG_FILE = SVXLINK_DIRECTORY / "svxlink.conf"

    NODE_INFO_FILE = SVXLINK_DIRECTORY / "node_info.json"

    LOG_DIRECTORY = Path("/var/log")

    CACHE_DIRECTORY = Path("/var/cache/svxguardian")

    RUNTIME_DIRECTORY = Path("/run/svxguardian")
