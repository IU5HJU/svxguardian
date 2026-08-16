"""
SVX Guardian configuration manager.

Provides centralized access to application settings and filesystem paths.

SvxLink paths are detected from the local installation rather than inferred
from the CPU architecture. Explicit environment overrides have the highest
priority, followed by the SvxLink systemd defaults file, known installation
layouts and finally the historical Debian/Raspberry Pi OS paths.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ApplicationConfig:
    """
    General application information.
    """

    name: str = "SVX Guardian"
    version: str = "0.2.0-dev"


@dataclass(frozen=True)
class PathConfig:
    """
    Filesystem paths used by SVX Guardian.
    """

    root_directory: Path = Path("/")
    log_directory: Path = Path("/var/log")
    cache_directory: Path = Path("/var/cache/svxguardian")
    runtime_directory: Path = Path("/run/svxguardian")


@dataclass(frozen=True)
class SvxLinkConfig:
    """
    Detected SvxLink filesystem paths.
    """

    directory: Path
    config_file: Path
    node_info_file: Path
    log_file: Path


class ConfigManager:
    """
    Centralized configuration for SVX Guardian.

    SvxLink installation paths are resolved using the following priority:

    1. Explicit SVX Guardian environment variables.
    2. SvxLink systemd defaults files.
    3. Known existing SvxLink installation layouts.
    4. Historical Debian/Raspberry Pi OS paths as fallback.

    This intentionally does not depend on whether the operating system is
    32-bit or 64-bit.
    """

    LEGACY_SVXLINK_DIRECTORY = Path("/etc/svxlink")
    LOCAL_SVXLINK_DIRECTORY = Path("/usr/local/etc/svxlink")

    LEGACY_SVXLINK_CONFIG = (
        LEGACY_SVXLINK_DIRECTORY / "svxlink.conf"
    )

    LOCAL_SVXLINK_CONFIG = (
        LOCAL_SVXLINK_DIRECTORY / "svxlink.conf"
    )

    LEGACY_NODE_INFO_FILE = (
        LEGACY_SVXLINK_DIRECTORY / "node_info.json"
    )

    LEGACY_LOG_FILE = Path("/var/log/svxlink")
    LOCAL_LOG_FILE = Path("/usr/local/var/log/svxlink")

    SVXLINK_DEFAULT_FILES = (
        Path("/etc/default/svxlink"),
        Path("/usr/local/etc/default/svxlink"),
    )

    def __init__(self) -> None:
        """
        Initialize the application configuration.
        """

        self.application = ApplicationConfig()
        self.paths = PathConfig()
        self.svxlink = self._detect_svxlink()

    def _detect_svxlink(self) -> SvxLinkConfig:
        """
        Detect the SvxLink installation layout.
        """

        defaults = self._read_svxlink_defaults()

        config_file = self._resolve_config_file(defaults)
        directory = self._resolve_svxlink_directory(
            config_file
        )

        node_info_file = self._resolve_node_info_file(
            directory
        )

        log_file = self._resolve_log_file(defaults)

        return SvxLinkConfig(
            directory=directory,
            config_file=config_file,
            node_info_file=node_info_file,
            log_file=log_file,
        )

    def _resolve_config_file(
        self,
        defaults: dict[str, str],
    ) -> Path:
        """
        Resolve the active SvxLink configuration file.
        """

        environment_value = os.getenv(
            "SVXGUARDIAN_SVXLINK_CONFIG"
        )

        if environment_value:
            return Path(environment_value)

        default_value = defaults.get("CFGFILE", "")

        if default_value:
            return Path(default_value)

        candidates = (
            self.LEGACY_SVXLINK_CONFIG,
            self.LOCAL_SVXLINK_CONFIG,
        )

        for candidate in candidates:
            if candidate.is_file():
                return candidate

        return self.LEGACY_SVXLINK_CONFIG

    def _resolve_svxlink_directory(
        self,
        config_file: Path,
    ) -> Path:
        """
        Resolve the SvxLink configuration directory.
        """

        environment_value = os.getenv(
            "SVXGUARDIAN_SVXLINK_DIRECTORY"
        )

        if environment_value:
            return Path(environment_value)

        return config_file.parent

    def _resolve_node_info_file(
        self,
        directory: Path,
    ) -> Path:
        """
        Resolve the SvxLink node_info.json path.
        """

        environment_value = os.getenv(
            "SVXGUARDIAN_NODE_INFO_FILE"
        )

        if environment_value:
            return Path(environment_value)

        return directory / "node_info.json"

    def _resolve_log_file(
        self,
        defaults: dict[str, str],
    ) -> Path:
        """
        Resolve the SvxLink logfile path.
        """

        environment_value = os.getenv(
            "SVXGUARDIAN_SVXLINK_LOG"
        )

        if environment_value:
            return Path(environment_value)

        default_value = defaults.get("LOGFILE", "")

        if default_value and default_value != "syslog:":
            return Path(default_value)

        candidates = (
            self.LEGACY_LOG_FILE,
            self.LOCAL_LOG_FILE,
        )

        for candidate in candidates:
            if candidate.is_file():
                return candidate

        return self.LEGACY_LOG_FILE

    def _read_svxlink_defaults(
        self,
    ) -> dict[str, str]:
        """
        Read SvxLink systemd defaults from known locations.
        """

        values: dict[str, str] = {}

        for defaults_file in self.SVXLINK_DEFAULT_FILES:
            if not defaults_file.is_file():
                continue

            try:
                lines = defaults_file.read_text(
                    encoding="utf-8",
                    errors="ignore",
                ).splitlines()
            except OSError:
                continue

            for line in lines:
                stripped = line.strip()

                if not stripped:
                    continue

                if stripped.startswith("#"):
                    continue

                key, separator, value = stripped.partition(
                    "="
                )

                if not separator:
                    continue

                key = key.strip()
                value = (
                    value.strip()
                    .strip('"')
                    .strip("'")
                )

                if key:
                    values[key] = value

        return values

    @property
    def APPLICATION_NAME(self) -> str:
        """
        Return the application name.

        This property preserves compatibility with existing components.
        """

        return self.application.name

    @property
    def APPLICATION_VERSION(self) -> str:
        """
        Return the application version.

        This property preserves compatibility with existing components.
        """

        return self.application.version

    @property
    def ROOT_DIRECTORY(self) -> Path:
        """
        Return the filesystem root directory.
        """

        return self.paths.root_directory

    @property
    def ETC_DIRECTORY(self) -> Path:
        """
        Return the system configuration directory.
        """

        return self.paths.root_directory / "etc"

    @property
    def SVXLINK_DIRECTORY(self) -> Path:
        """
        Return the detected SvxLink configuration directory.
        """

        return self.svxlink.directory

    @property
    def SVXLINK_CONFIG_FILE(self) -> Path:
        """
        Return the detected SvxLink configuration file.
        """

        return self.svxlink.config_file

    @property
    def NODE_INFO_FILE(self) -> Path:
        """
        Return the detected SvxLink node information file.
        """

        return self.svxlink.node_info_file

    @property
    def SVXLINK_LOG_FILE(self) -> Path:
        """
        Return the detected SvxLink logfile.
        """

        return self.svxlink.log_file

    @property
    def LOG_DIRECTORY(self) -> Path:
        """
        Return the generic system log directory.

        Kept for compatibility with existing SVX Guardian components.
        """

        return self.paths.log_directory

    @property
    def CACHE_DIRECTORY(self) -> Path:
        """
        Return the cache directory.
        """

        return self.paths.cache_directory

    @property
    def RUNTIME_DIRECTORY(self) -> Path:
        """
        Return the runtime directory.
        """

        return self.paths.runtime_directory
