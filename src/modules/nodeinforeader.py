"""
SvxLink node information reader.

Reads /etc/svxlink/node_info.json and enriches NodeInfo.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..core.nodeinfo import NodeInfo


DEFAULT_NODE_INFO_FILE = Path(
    "/etc/svxlink/node_info.json"
)


class NodeInfoReader:
    """
    Reads the SvxLink node information JSON file.
    """

    def __init__(
        self,
        node_info_file: Path | str = DEFAULT_NODE_INFO_FILE,
    ) -> None:
        self.node_info_file = Path(node_info_file)

    def enrich(self, node: NodeInfo) -> NodeInfo:
        """
        Enrich an existing NodeInfo object with JSON data.
        """

        node.node_info_file = str(self.node_info_file)

        if not self.node_info_file.is_file():
            return node

        try:
            with self.node_info_file.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)
        except (
            OSError,
            UnicodeDecodeError,
            json.JSONDecodeError,
        ):
            return node

        if not isinstance(data, dict):
            return node

        node.node_location = self._as_string(
            data.get("nodeLocation")
        )

        node.node_class = self._as_string(
            data.get("nodeClass")
        )

        node.hidden = bool(
            data.get("hidden", False)
        )

        node.sysop = self._as_string(
            data.get("sysop")
        )

        node.tone_to_talkgroup = (
            self._read_tone_to_talkgroup(
                data.get("toneToTalkgroup")
            )
        )

        self._read_qth(
            node,
            data.get("qth"),
        )

        return node

    def _read_qth(
        self,
        node: NodeInfo,
        qth_data: Any,
    ) -> None:
        """
        Read the first available QTH entry.
        """

        if not isinstance(qth_data, list):
            return

        if not qth_data:
            return

        first_qth = qth_data[0]

        if not isinstance(first_qth, dict):
            return

        node.qth = self._as_string(
            first_qth.get("name")
        )

        position = first_qth.get("pos")

        if isinstance(position, dict):
            node.latitude = self._as_float(
                position.get("lat")
            )

            node.longitude = self._as_float(
                position.get("long")
            )

            node.locator = self._as_string(
                position.get("loc")
            )

        self._read_receiver(
            node,
            first_qth.get("rx"),
        )

        self._read_transmitter(
            node,
            first_qth.get("tx"),
        )

    def _read_receiver(
        self,
        node: NodeInfo,
        receiver_data: Any,
    ) -> None:
        """
        Read the first available receiver.
        """

        receiver = self._first_mapping_value(
            receiver_data
        )

        if receiver is None:
            return

        node.rx_name = self._as_string(
            receiver.get("name")
        )

        node.rx_frequency = self._format_number(
            receiver.get("freq")
        )

        node.rx_sql_type = self._as_string(
            receiver.get("sqlType")
        )

        ctcss_values = receiver.get("ctcssFreq")

        if isinstance(ctcss_values, list):
            node.rx_ctcss_frequencies = [
                self._format_number(value)
                for value in ctcss_values
                if self._format_number(value)
            ]

        elif ctcss_values is not None:
            ctcss = self._format_number(
                ctcss_values
            )

            if ctcss:
                node.rx_ctcss_frequencies = [ctcss]

    def _read_transmitter(
        self,
        node: NodeInfo,
        transmitter_data: Any,
    ) -> None:
        """
        Read the first available transmitter.
        """

        transmitter = self._first_mapping_value(
            transmitter_data
        )

        if transmitter is None:
            return

        node.tx_name = self._as_string(
            transmitter.get("name")
        )

        node.tx_frequency = self._format_number(
            transmitter.get("freq")
        )

        node.tx_power = self._format_number(
            transmitter.get("pwr")
        )

        node.tx_ctcss_frequency = self._format_number(
            transmitter.get("ctcssFreq")
        )

        node.ctcss = node.tx_ctcss_frequency

        if (
            not node.ctcss
            and node.rx_ctcss_frequencies
        ):
            node.ctcss = node.rx_ctcss_frequencies[0]

    @staticmethod
    def _first_mapping_value(
        data: Any,
    ) -> dict[str, Any] | None:
        """
        Return the first dictionary value from a mapping.
        """

        if not isinstance(data, dict):
            return None

        for value in data.values():
            if isinstance(value, dict):
                return value

        return None

    @staticmethod
    def _read_tone_to_talkgroup(
        data: Any,
    ) -> dict[str, int]:
        """
        Normalize tone-to-talkgroup mappings.
        """

        if not isinstance(data, dict):
            return {}

        result: dict[str, int] = {}

        for tone, talkgroup in data.items():
            try:
                result[str(tone)] = int(talkgroup)
            except (
                TypeError,
                ValueError,
            ):
                continue

        return result

    @staticmethod
    def _as_string(
        value: Any,
    ) -> str:
        """
        Convert a value into a normalized string.
        """

        if value is None:
            return ""

        return str(value).strip()

    @staticmethod
    def _as_float(
        value: Any,
    ) -> float | None:
        """
        Convert a value into a float when possible.
        """

        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ):
            return None

    @staticmethod
    def _format_number(
        value: Any,
    ) -> str:
        """
        Format numeric JSON values without unnecessary zeros.
        """

        if value is None:
            return ""

        if isinstance(value, bool):
            return ""

        if isinstance(value, int):
            return str(value)

        if isinstance(value, float):
            return f"{value:g}"

        text = str(value).strip()

        return text
