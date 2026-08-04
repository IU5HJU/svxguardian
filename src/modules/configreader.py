"""
SvxLink configuration reader.

Reads the SvxLink configuration and populates a NodeInfo object.
"""

from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path

from ..core.nodeinfo import NodeInfo


DEFAULT_CONFIG = Path("/etc/svxlink/svxlink.conf")


class ConfigReader:
    """
    Reads the main SvxLink configuration file.
    """

    def __init__(
        self,
        config_file: Path | str = DEFAULT_CONFIG,
    ) -> None:
        self.config_file = Path(config_file)

    def load(self) -> NodeInfo:
        """
        Read the configuration file and return NodeInfo.
        """

        node = NodeInfo(
            config_file=str(self.config_file),
        )

        if not self.config_file.is_file():
            return node

        parser = ConfigParser(
            interpolation=None,
            strict=False,
        )

        parser.optionxform = str

        try:
            with self.config_file.open(
                "r",
                encoding="utf-8",
            ) as file:
                parser.read_file(file)
        except (
            OSError,
            UnicodeDecodeError,
        ):
            return node

        logic_names = self._get_list(
            parser,
            "GLOBAL",
            "LOGICS",
        )

        primary_logic = self._find_primary_logic(
            parser,
            logic_names,
        )

        reflector_logic = self._find_logic_by_type(
            parser,
            logic_names,
            "Reflector",
        )

        if primary_logic:
            node.callsign = self._get_value(
                parser,
                primary_logic,
                "CALLSIGN",
            )

            node.modules = self._get_list(
                parser,
                primary_logic,
                "MODULES",
            )

        if not node.callsign and reflector_logic:
            node.callsign = self._get_value(
                parser,
                reflector_logic,
                "CALLSIGN",
            )

        if reflector_logic:
            reflector_hosts = self._get_value(
                parser,
                reflector_logic,
                "HOSTS",
            )

            reflector_port = self._get_value(
                parser,
                reflector_logic,
                "HOST_PORT",
            )

            default_tg = self._get_value(
                parser,
                reflector_logic,
                "DEFAULT_TG",
            )

            node.reflector = self._format_reflector(
                reflector_hosts,
                reflector_port,
                default_tg,
            )

        node.qth = self._get_value(
            parser,
            "LOCATION_INFO",
            "QTH_NAME",
        )

        node.locator = self._get_value(
            parser,
            "LOCATION_INFO",
            "GRID_SQUARE",
        )

        node.description = self._get_value(
            parser,
            "IDENTIFICATION",
            "SHORT_IDENT",
        )

        return node

    @staticmethod
    def _get_value(
        parser: ConfigParser,
        section: str,
        option: str,
    ) -> str:
        """
        Return a normalized configuration value.
        """

        if not parser.has_section(section):
            return ""

        value = parser.get(
            section,
            option,
            fallback="",
        )

        return value.strip().strip('"').strip("'")

    @classmethod
    def _get_list(
        cls,
        parser: ConfigParser,
        section: str,
        option: str,
    ) -> list[str]:
        """
        Return a comma-separated configuration value as a list.
        """

        value = cls._get_value(
            parser,
            section,
            option,
        )

        if not value:
            return []

        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

    @classmethod
    def _find_primary_logic(
        cls,
        parser: ConfigParser,
        logic_names: list[str],
    ) -> str:
        """
        Find the first non-reflector logic containing a callsign.
        """

        for logic_name in logic_names:
            logic_type = cls._get_value(
                parser,
                logic_name,
                "TYPE",
            )

            callsign = cls._get_value(
                parser,
                logic_name,
                "CALLSIGN",
            )

            if callsign and logic_type.lower() != "reflector":
                return logic_name

        for logic_name in logic_names:
            callsign = cls._get_value(
                parser,
                logic_name,
                "CALLSIGN",
            )

            if callsign:
                return logic_name

        return ""

    @classmethod
    def _find_logic_by_type(
        cls,
        parser: ConfigParser,
        logic_names: list[str],
        expected_type: str,
    ) -> str:
        """
        Find a logic section by its TYPE value.
        """

        expected = expected_type.casefold()

        for logic_name in logic_names:
            logic_type = cls._get_value(
                parser,
                logic_name,
                "TYPE",
            )

            if logic_type.casefold() == expected:
                return logic_name

        return ""

    @staticmethod
    def _format_reflector(
        hosts: str,
        port: str,
        default_tg: str,
    ) -> str:
        """
        Format the available Reflector connection information.
        """

        connection = hosts

        if connection and port:
            connection = f"{connection}:{port}"

        if connection and default_tg:
            return f"{connection} - TG {default_tg}"

        if default_tg:
            return f"TG {default_tg}"

        return connection
