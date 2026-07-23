"""
Internationalization (i18n)

Translation manager for SVX Guardian.
"""

import json
from pathlib import Path


class TranslationManager:
    """
    Loads translations from locale/*.json
    """

    def __init__(self, language: str = "en") -> None:

        self.language = language
        self.translations = {}

        self.load()

    def load(self) -> None:

        locale_file = (
            Path(__file__).parent.parent
            / "locale"
            / f"{self.language}.json"
        )

        if locale_file.exists():

            with open(locale_file, "r", encoding="utf-8") as file:
                self.translations = json.load(file)

    def gettext(self, key: str) -> str:
        """
        Return translated string.
        """

        return self.translations.get(key, key)
