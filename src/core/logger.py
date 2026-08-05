"""
SVX Guardian logging manager.

Provides centralized logging configuration.
"""

import logging


class LoggerManager:
    """
    Configure the SVX Guardian logging system.
    """

    def __init__(self) -> None:
        """
        Initialize the logger manager.
        """

        self._configured = False

    def configure(self) -> None:
        """
        Configure the application logger.
        """

        if self._configured:
            return

        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
        )

        self._configured = True
