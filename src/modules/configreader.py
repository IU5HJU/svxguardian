"""
SvxLink configuration reader.

Reads the SvxLink configuration and populates a NodeInfo object.
"""

from __future__ import annotations

from configparser import ConfigParser
from ipaddress import ip_address
from pathlib import Path
from socket import gaierror, gethostbyname

from ..core.nodeinfo import NodeInfo


DEFAULT_CONFIG = Path("/etc/svxlink/svxlink.conf")

LOCAL_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
}

LOCAL_IP_ADDRESSES = {
    "127.0.0.1",
    "::1",
}


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

        node.logics = self._get_list(
            parser,
            "GLOBAL",
            "LOGICS",
        )

        primary_logic = self._find_primary_logic(
            parser,
            node.logics,
        )

        reflector_logic = self._find_logic_by_type(
            parser,
            node.logics,
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

        self._read_reflector_configuration(
            node,
            parser,
            reflector_logic,
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

    def _read_reflector_configuration(
        self,
        node: NodeInfo,
        parser: ConfigParser,
        reflector_logic: str,
    ) -> None:
        """
        Read structured Reflector configuration data.

        NODE_INFO_FILE is the current SvxLink configuration
        option used to reference node_info.json.

        O_FILE is also accepted for compatibility with existing
        SvxLink installations that use the historical option name.
        """

        if not reflector_logic:
            node.reflector_configured = False
            node.reflector_mode = "disabled"
            node.reflector = ""
            node.node_info_file = ""
            return

        node.reflector_configured = True
        node.reflector_logic_name = reflector_logic

        node.reflector_hosts = self._get_list(
            parser,
            reflector_logic,
            "HOSTS",
        )

        node.reflector_port = self._get_optional_int(
            parser,
            reflector_logic,
            "HOST_PORT",
        )

        node.reflector_default_tg = self._get_optional_int(
            parser,
            reflector_logic,
            "DEFAULT_TG",
        )

        node.node_info_file = self._get_value(
            parser,
            reflector_logic,
            "NODE_INFO_FILE",
        )

        if not node.node_info_file:
            node.node_info_file = self._get_value(
                parser,
                reflector_logic,
                "O_FILE",
            )

        node.reflector_mode = self._classify_reflector_mode(
            node.reflector_hosts
        )

        node.reflector = self._format_reflector(
            node.reflector_hosts,
            node.reflector_port,
            node.reflector_default_tg,
        )

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
    def _get_optional_int(
        cls,
        parser: ConfigParser,
        section: str,
        option: str,
    ) -> int | None:
        """
        Return an integer configuration value when valid.
        """

        value = cls._get_value(
            parser,
            section,
            option,
        )

        if not value:
            return None

        try:
            return int(value)
        except ValueError:
            return None

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

            if callsign and logic_type.casefold() != "reflector":
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

    @classmethod
    def _classify_reflector_mode(
        cls,
        hosts: list[str],
    ) -> str:
        """
        Classify configured Reflector hosts.

        The classification describes configuration only.
        It does not prove connectivity or service availability.
        """

        if not hosts:
            return "unknown"

        local_count = 0
        remote_count = 0

        for host in hosts:
            if cls._is_local_host(host):
                local_count += 1
            else:
                remote_count += 1

        if local_count and remote_count:
            return "mixed"

        if local_count:
            return "local"

        if remote_count:
            return "remote"

        return "unknown"

    @classmethod
    def _is_local_host(
        cls,
        host: str,
    ) -> bool:
        """
        Return True when a host clearly refers to the local machine.
        """

        normalized = host.strip().casefold()

        if not normalized:
            return False

        if normalized in LOCAL_HOSTNAMES:
            return True

        if normalized in LOCAL_IP_ADDRESSES:
            return True

        try:
            parsed_ip = ip_address(normalized)
        except ValueError:
            parsed_ip = None

        if parsed_ip is not None:
            return parsed_ip.is_loopback

        try:
            resolved_ip = gethostbyname(normalized)
        except gaierror:
            return False

        return resolved_ip in LOCAL_IP_ADDRESSES

    @staticmethod
    def _format_reflector(
        hosts: list[str],
        port: int | None,
        default_tg: int | None,
    ) -> str:
        """
        Build a temporary human-readable Reflector summary.
        """

        host_text = ", ".join(hosts)

        if host_text and port is not None:
            host_text = f"{host_text}:{port}"

        if host_text and default_tg is not None:
            return f"{host_text} - TG {default_tg}"

        if default_tg is not None:
            return f"TG {default_tg}"

        return host_text
