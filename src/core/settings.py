"""
SVX Guardian persistent application settings.

Stores Guardian-specific settings outside the Git repository.

The settings file is intentionally separate from SvxLink
configuration and authentication data.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any


DEFAULT_SETTINGS_FILE = Path(
    "/var/lib/svxguardian/settings.json"
)


DEFAULT_SETTINGS: dict[str, Any] = {
    "public_dashboard": {
        "reflector_name": "SvxReflector",
    },
}


class SettingsManager:
    """
    Read and update persistent SVX Guardian settings.

    Unknown sections and keys are preserved so the settings
    structure can grow during future development.
    """

    def __init__(
        self,
        settings_file: Path | str = DEFAULT_SETTINGS_FILE,
    ) -> None:
        self.settings_file = Path(
            settings_file
        )

    def load(self) -> dict[str, Any]:
        """
        Load settings merged with safe defaults.

        Missing, unreadable or invalid settings files fall back
        to the default configuration.
        """

        settings = deepcopy(
            DEFAULT_SETTINGS
        )

        data = self._read_file()

        if not isinstance(
            data,
            dict,
        ):
            return settings

        return self._merge_dicts(
            settings,
            data,
        )

    def update_section(
        self,
        section: str,
        values: dict[str, Any],
    ) -> None:
        """
        Update one settings section while preserving all other
        existing sections and unknown future keys.
        """

        data = self._read_file()

        if not isinstance(
            data,
            dict,
        ):
            data = {}

        current_section = data.get(
            section
        )

        if not isinstance(
            current_section,
            dict,
        ):
            current_section = {}

        current_section.update(
            values
        )

        data[
            section
        ] = current_section

        self._write_file(
            data
        )

    def _read_file(
        self,
    ) -> dict[str, Any]:
        """
        Return raw settings data from disk.
        """

        if not self.settings_file.is_file():
            return {}

        try:
            with self.settings_file.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

        except (
            OSError,
            json.JSONDecodeError,
        ):
            return {}

        if not isinstance(
            data,
            dict,
        ):
            return {}

        return data

    def _write_file(
        self,
        data: dict[str, Any],
    ) -> None:
        """
        Persist settings atomically enough for this small
        local configuration file.
        """

        temporary_file = (
            self.settings_file.with_suffix(
                self.settings_file.suffix
                + ".tmp"
            )
        )

        temporary_file.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=4,
            ) + "\n",
            encoding="utf-8",
        )

        temporary_file.replace(
            self.settings_file
        )

    @classmethod
    def _merge_dicts(
        cls,
        defaults: dict[str, Any],
        values: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Recursively merge user settings over defaults.
        """

        result = deepcopy(
            defaults
        )

        for key, value in values.items():

            if (
                isinstance(
                    value,
                    dict,
                )
                and isinstance(
                    result.get(key),
                    dict,
                )
            ):
                result[
                    key
                ] = cls._merge_dicts(
                    result[key],
                    value,
                )
            else:
                result[
                    key
                ] = deepcopy(
                    value
                )

        return result
