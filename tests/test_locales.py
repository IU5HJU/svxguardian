"""
SVX Guardian locale validator.

Validates translation JSON files against the English reference file.
Metadata files, such as languages.json, are validated separately.
"""

import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCALE_DIRECTORY = PROJECT_ROOT / "locale"
REFERENCE_FILE = LOCALE_DIRECTORY / "en.json"
LANGUAGES_FILE = LOCALE_DIRECTORY / "languages.json"

EXCLUDED_TRANSLATION_FILES = {
    "languages.json",
}


class DuplicateKeyError(ValueError):
    """
    Raised when a JSON file contains duplicate keys.
    """


def reject_duplicate_keys(
    pairs: list[tuple[str, Any]],
) -> dict[str, Any]:
    """
    Convert JSON key-value pairs into a dictionary.

    Raise an error when the same key appears more than once.
    """

    result: dict[str, Any] = {}

    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(
                f"Duplicate JSON key: {key}"
            )

        result[key] = value

    return result


def load_json_file(file_path: Path) -> Any:
    """
    Load a UTF-8 JSON file and detect duplicate keys.
    """

    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(
            f"{file_path.name}: invalid UTF-8 encoding"
        ) from error

    try:
        return json.loads(
            content,
            object_pairs_hook=reject_duplicate_keys,
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            f"{file_path.name}: invalid JSON "
            f"at line {error.lineno}, column {error.colno}"
        ) from error


def load_locale_file(file_path: Path) -> dict[str, str]:
    """
    Load and validate a translation file.
    """

    data = load_json_file(file_path)

    if not isinstance(data, dict):
        raise ValueError(
            f"{file_path.name}: the root element must be an object"
        )

    translations: dict[str, str] = {}

    for key, value in data.items():
        if not isinstance(key, str):
            raise ValueError(
                f"{file_path.name}: every key must be a string"
            )

        if not isinstance(value, str):
            raise ValueError(
                f"{file_path.name}: value for {key} must be a string"
            )

        if not key.strip():
            raise ValueError(
                f"{file_path.name}: empty translation key"
            )

        if not value.strip():
            raise ValueError(
                f"{file_path.name}: empty translation for {key}"
            )

        translations[key] = value

    return translations


def validate_languages_file() -> bool:
    """
    Validate locale/languages.json.
    """

    if not LANGUAGES_FILE.exists():
        print("[ERROR] languages.json not found")
        return False

    try:
        data = load_json_file(LANGUAGES_FILE)
    except (ValueError, DuplicateKeyError) as error:
        print(f"[ERROR] {error}")
        return False

    if not isinstance(data, dict):
        print("[ERROR] languages.json: root must be an object")
        return False

    valid = True

    for language_code, metadata in data.items():
        if not isinstance(language_code, str):
            print(
                "[ERROR] languages.json: "
                "language codes must be strings"
            )
            valid = False
            continue

        if not isinstance(metadata, dict):
            print(
                f"[ERROR] languages.json: "
                f"value for {language_code} must be an object"
            )
            valid = False
            continue

        required_fields = {
            "name",
            "native_name",
            "enabled",
        }

        missing_fields = required_fields - set(metadata)

        if missing_fields:
            print(
                f"[ERROR] languages.json: "
                f"{language_code} missing fields: "
                f"{', '.join(sorted(missing_fields))}"
            )
            valid = False
            continue

        if not isinstance(metadata["name"], str):
            print(
                f"[ERROR] languages.json: "
                f"{language_code}.name must be a string"
            )
            valid = False

        if not isinstance(metadata["native_name"], str):
            print(
                f"[ERROR] languages.json: "
                f"{language_code}.native_name must be a string"
            )
            valid = False

        if not isinstance(metadata["enabled"], bool):
            print(
                f"[ERROR] languages.json: "
                f"{language_code}.enabled must be a boolean"
            )
            valid = False

        locale_file = LOCALE_DIRECTORY / f"{language_code}.json"

        if metadata["enabled"] and not locale_file.exists():
            print(
                f"[ERROR] languages.json: "
                f"{language_code} is enabled but "
                f"{locale_file.name} does not exist"
            )
            valid = False

    if valid:
        print(
            f"[OK]    languages.json "
            f"({len(data)} languages)"
        )

    return valid


def validate_locales() -> bool:
    """
    Validate every translation file against the English reference.
    """

    if not REFERENCE_FILE.exists():
        print(
            f"ERROR: reference file not found: {REFERENCE_FILE}"
        )
        return False

    try:
        reference_data = load_locale_file(REFERENCE_FILE)
    except (ValueError, DuplicateKeyError) as error:
        print(f"ERROR: {error}")
        return False

    reference_keys = set(reference_data)

    locale_files = sorted(
        file_path
        for file_path in LOCALE_DIRECTORY.glob("*.json")
        if file_path.name not in EXCLUDED_TRANSLATION_FILES
    )

    if not locale_files:
        print("ERROR: no locale files found")
        return False

    all_valid = True

    print("=" * 60)
    print("SVX Guardian locale validation")
    print("=" * 60)

    for locale_file in locale_files:
        try:
            locale_data = load_locale_file(locale_file)
        except (ValueError, DuplicateKeyError) as error:
            print(f"[ERROR] {error}")
            all_valid = False
            continue

        locale_keys = set(locale_data)

        missing_keys = sorted(reference_keys - locale_keys)
        extra_keys = sorted(locale_keys - reference_keys)

        if missing_keys or extra_keys:
            print(f"[ERROR] {locale_file.name}")

            if missing_keys:
                print("        Missing keys:")

                for key in missing_keys:
                    print(f"        - {key}")

            if extra_keys:
                print("        Unexpected keys:")

                for key in extra_keys:
                    print(f"        - {key}")

            all_valid = False
            continue

        print(
            f"[OK]    {locale_file.name} "
            f"({len(locale_data)} translations)"
        )

    languages_valid = validate_languages_file()

    if not languages_valid:
        all_valid = False

    print("-" * 60)

    if all_valid:
        print("All locale files are valid.")
    else:
        print("Locale validation failed.")

    return all_valid


def main() -> None:
    """
    Application entry point.
    """

    success = validate_locales()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
