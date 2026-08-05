"""
SVX Guardian bootstrap engine.

Handles the initial application startup sequence.
"""

import logging

from .logger import LoggerManager


class BootstrapEngine:
    """
    Manage the SVX Guardian startup sequence.
    """

    APPLICATION_NAME = "SVX Guardian"
    APPLICATION_VERSION = "0.2.0-dev"

    def __init__(self) -> None:
        """
        Initialize the bootstrap engine.
        """

        self.logger = logging.getLogger(__name__)
        self.logger_manager = LoggerManager()

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
            self.APPLICATION_NAME,
            self.APPLICATION_VERSION,
        )
        self.logger.info("=" * 60)
