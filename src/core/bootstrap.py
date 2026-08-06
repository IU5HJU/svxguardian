"""
SVX Guardian bootstrap engine.

Handles the initial application startup sequence.
"""

import logging

from .config import ConfigManager
from .logger import LoggerManager


class BootstrapEngine:
    """
    Manage the SVX Guardian startup sequence.
    """

    def __init__(self) -> None:
        """
        Initialize the bootstrap engine.
        """

        self.config = ConfigManager()
        self.logger_manager = LoggerManager()
        self.logger = logging.getLogger(__name__)

    def run(self) -> None:
        """
        Execute the bootstrap sequence.
        """

        self.logger_manager.configure()
        self.show_startup_banner()

    def show_startup_banner(self) -> None:
        """
        Write the application startup banner to the log.
        """

        self.logger.info("=" * 60)
        self.logger.info(
            "%s v%s",
            self.config.application.name,
            self.config.application.version,
        )
        self.logger.info("=" * 60)
