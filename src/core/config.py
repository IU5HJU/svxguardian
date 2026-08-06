"""
SVX Guardian configuration manager.

Provides centralized access to application settings and filesystem paths.
"""

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
    SvxLink configuration paths.
    """

    directory: Path = Path("/etc/svxlink")
    config_file: Path = Path("/etc/svxlink/svxlink.conf")
    node_info_file: Path = Path("/etc/svxlink/node_info.json")


class ConfigManager:
    """
    Centralized configuration for SVX Guardian.
    """

    def __init__(self) -> None:
        """
        Initialize the application configuration.
        """

        self.application = ApplicationConfig()
        self.paths = PathConfig()
        self.svxlink = SvxLinkConfig()

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
        Return the SvxLink configuration directory.
        """

        return self.svxlink.directory

    @property
    def SVXLINK_CONFIG_FILE(self) -> Path:
        """
        Return the main SvxLink configuration file.
        """

        return self.svxlink.config_file

    @property
    def NODE_INFO_FILE(self) -> Path:
        """
        Return the SvxLink node information file.
        """

        return self.svxlink.node_info_file

    @property
    def LOG_DIRECTORY(self) -> Path:
        """
        Return the log directory.
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
