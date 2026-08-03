"""
Internationalization manager.

Loads translations from the locale directory.
"""

import json
from pathlib import Path


class TranslationManager:
    """
    Loads and provides translated strings.
    """

    def __init__(
        self,
        language: str = "en",
        fallback_language: str = "en",
    ) -> None:
        self.language = language
        self.fallback_language = fallback_language
        self.translations: dict[str, str] = {}
        self.fallback_translations: dict[str, str] = {}

        self._load_translations()

    @staticmethod
    def _locale_directory() -> Path:
        """
        Return the project locale directory.
        """

        return Path(__file__).resolve().parents[2] / "locale"

    def _load_file(self, language: str) -> dict[str, str]:
        """
        Load a language file.
        """

        locale_file = self._locale_directory() / f"{language}.json"

        if not locale_file.exists():
            return {}

        with locale_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                f"Invalid translation file format: {locale_file}"
            )

        return {
            str(key): str(value)
            for key, value in data.items()
        }

    def _load_translations(self) -> None:
        """
        Load selected and fallback languages.
        """

        self.translations = self._load_file(self.language)
        self.fallback_translations = self._load_file(
            self.fallback_language
        )

    def gettext(self, key: str) -> str:
        """
        Return the translated string for a key.
        """

        if key in self.translations:
            return self.translations[key]

        if key in self.fallback_translations:
            return self.fallback_translations[key]

        return key
