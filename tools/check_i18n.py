"""
SVX Guardian internationalization audit.

Checks locale consistency, translation usage,
and hardcoded visible strings in HTML templates.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent

LOCALE_DIRECTORY = (
    PROJECT_ROOT
    / "locale"
)

TEMPLATE_DIRECTORY = (
    PROJECT_ROOT
    / "src"
    / "web"
    / "templates"
)

REFERENCE_FILE = (
    LOCALE_DIRECTORY
    / "en.json"
)


EXCLUDED_LOCALE_FILES = {
    "languages.json",
}


ALLOWED_HARDCODED_TERMS = {
    "SvxLink",
    "EchoLink",
    "Reflector",
    "CPU",
    "RAM",
    "RX",
    "TX",
    "CTCSS",
    "COS",
    "TG",
    "API",
    "JSON",
    "NOCALL",
}


#
# Visible text found directly between HTML tags.
#
TEMPLATE_TEXT_PATTERN = re.compile(
    r">([^<>{%]+)<",
    re.MULTILINE,
)


#
# Translation function.
#
# IMPORTANT:
#
# The negative lookbehind prevents JavaScript functions such as:
#
#     createElement("div")
#     request("screen")
#
# from being mistaken for:
#
#     t("div")
#     t("screen")
#
# It also avoids matching object methods such as:
#
#     translator.t("KEY")
#
TRANSLATION_CALL_PATTERN = re.compile(
    r"""(?<![\w.])t\s*\(\s*["']([^"']+)["']\s*\)"""
)


#
# Script and style blocks are masked before searching for
# static HTML text.
#
# This prevents HTML fragments inside JavaScript template
# literals from confusing the visible-text scanner.
#
SCRIPT_STYLE_BLOCK_PATTERN = re.compile(
    r"<(?P<tag>script|style)\b[^>]*>"
    r".*?"
    r"</(?P=tag)\s*>",
    re.IGNORECASE
    | re.DOTALL,
)


#
# Detect simple user-visible JavaScript strings.
#
# Examples:
#
#     element.textContent = "Connected";
#     element.innerText = "Connected";
#
JAVASCRIPT_VISIBLE_TEXT_PATTERN = re.compile(
    r"""
    \.
    (?P<property>
        textContent
        |
        innerText
    )
    \s*
    =
    \s*
    (?P<quote>["'])
    (?P<text>.*?)
    (?P=quote)
    """,
    re.VERBOSE,
)


class DuplicateKeyError(ValueError):
    """
    Raised when a JSON object contains duplicate keys.
    """


def reject_duplicate_keys(
    pairs: list[tuple[str, Any]],
) -> dict[str, Any]:
    """
    Convert JSON pairs into a dictionary and reject duplicates.
    """

    result: dict[str, Any] = {}

    for key, value in pairs:

        if key in result:

            raise DuplicateKeyError(
                f"Duplicate JSON key: {key}"
            )

        result[key] = value

    return result


def load_json_file(
    file_path: Path,
) -> Any:
    """
    Load a UTF-8 JSON file and detect duplicate keys.
    """

    try:

        content = file_path.read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError as error:

        raise ValueError(
            f"{file_path.name}: invalid UTF-8 encoding"
        ) from error

    except OSError as error:

        raise ValueError(
            f"{file_path.name}: cannot be read"
        ) from error

    try:

        return json.loads(
            content,
            object_pairs_hook=reject_duplicate_keys,
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            f"{file_path.name}: invalid JSON at "
            f"line {error.lineno}, "
            f"column {error.colno}"
        ) from error


def load_translation_file(
    file_path: Path,
) -> dict[str, str]:
    """
    Load and validate a translation file.
    """

    data = load_json_file(
        file_path
    )

    if not isinstance(
        data,
        dict,
    ):

        raise ValueError(
            f"{file_path.name}: root must be an object"
        )

    translations: dict[str, str] = {}

    for key, value in data.items():

        if not isinstance(
            key,
            str,
        ):

            raise ValueError(
                f"{file_path.name}: translation keys "
                "must be strings"
            )

        if not isinstance(
            value,
            str,
        ):

            raise ValueError(
                f"{file_path.name}: value for {key} "
                "must be a string"
            )

        if not key.strip():

            raise ValueError(
                f"{file_path.name}: empty translation key"
            )

        if not value.strip():

            raise ValueError(
                f"{file_path.name}: empty translation "
                f"for {key}"
            )

        translations[key] = value

    return translations


def get_locale_files() -> list[Path]:
    """
    Return translation JSON files only.
    """

    return sorted(
        file_path
        for file_path
        in LOCALE_DIRECTORY.glob(
            "*.json"
        )
        if file_path.name
        not in EXCLUDED_LOCALE_FILES
    )


def validate_locale_consistency() -> tuple[
    bool,
    set[str],
]:
    """
    Validate every locale against the English reference.
    """

    if not REFERENCE_FILE.is_file():

        print(
            "[ERROR] English reference file not found"
        )

        return (
            False,
            set(),
        )

    try:

        reference_data = (
            load_translation_file(
                REFERENCE_FILE
            )
        )

    except (
        ValueError,
        DuplicateKeyError,
    ) as error:

        print(
            f"[ERROR] {error}"
        )

        return (
            False,
            set(),
        )

    reference_keys = set(
        reference_data
    )

    valid = True

    for locale_file in get_locale_files():

        try:

            locale_data = (
                load_translation_file(
                    locale_file
                )
            )

        except (
            ValueError,
            DuplicateKeyError,
        ) as error:

            print(
                f"[ERROR] {error}"
            )

            valid = False

            continue

        locale_keys = set(
            locale_data
        )

        missing_keys = sorted(
            reference_keys
            -
            locale_keys
        )

        extra_keys = sorted(
            locale_keys
            -
            reference_keys
        )

        if (
            missing_keys
            or
            extra_keys
        ):

            print(
                f"[ERROR] {locale_file.name}"
            )

            for key in missing_keys:

                print(
                    f"        Missing: {key}"
                )

            for key in extra_keys:

                print(
                    f"        Unexpected: {key}"
                )

            valid = False

            continue

        print(
            f"[OK]    {locale_file.name} "
            f"({len(locale_data)} translations)"
        )

    return (
        valid,
        reference_keys,
    )


def find_used_translation_keys() -> set[str]:
    """
    Return translation keys used by HTML templates.
    """

    used_keys: set[str] = set()

    for template_file in sorted(
        TEMPLATE_DIRECTORY.rglob(
            "*.html"
        )
    ):

        try:

            content = (
                template_file.read_text(
                    encoding="utf-8"
                )
            )

        except OSError:

            continue

        for match in (
            TRANSLATION_CALL_PATTERN.finditer(
                content
            )
        ):

            used_keys.add(
                match.group(1)
            )

    return used_keys


def normalize_visible_text(
    text: str,
) -> str:
    """
    Normalize visible template text.
    """

    return (
        " ".join(
            text.split()
        )
        .strip()
    )


def is_allowed_hardcoded_text(
    text: str,
) -> bool:
    """
    Return True for approved technical terms or symbols.
    """

    if not text:
        return True

    if text in ALLOWED_HARDCODED_TERMS:
        return True

    if not any(
        character.isalpha()
        for character in text
    ):
        return True

    return False


def mask_script_and_style_blocks(
    content: str,
) -> str:
    """
    Replace script/style content with spaces while preserving
    newline positions.

    Preserving newlines keeps reported line numbers aligned
    with the original template file.
    """

    def replacement(
        match: re.Match[str],
    ) -> str:

        block = match.group(0)

        return "".join(
            "\n"
            if character == "\n"
            else " "
            for character in block
        )

    return SCRIPT_STYLE_BLOCK_PATTERN.sub(
        replacement,
        content,
    )


def find_static_html_strings(
    template_file: Path,
    content: str,
) -> list[
    tuple[Path, int, str]
]:
    """
    Locate hardcoded visible strings in static HTML.

    JavaScript and CSS blocks are excluded from this pass.
    """

    findings: list[
        tuple[Path, int, str]
    ] = []

    masked_content = (
        mask_script_and_style_blocks(
            content
        )
    )

    for match in TEMPLATE_TEXT_PATTERN.finditer(
        masked_content
    ):

        raw_text = match.group(1)

        if (
            "{{" in raw_text
            or
            "{%" in raw_text
        ):

            continue

        text = normalize_visible_text(
            raw_text
        )

        if is_allowed_hardcoded_text(
            text
        ):

            continue

        line_number = (
            content.count(
                "\n",
                0,
                match.start(),
            )
            + 1
        )

        findings.append(
            (
                template_file,
                line_number,
                text,
            )
        )

    return findings


def find_javascript_visible_strings(
    template_file: Path,
    content: str,
) -> list[
    tuple[Path, int, str]
]:
    """
    Locate simple hardcoded strings assigned to JavaScript
    textContent or innerText properties.

    Dynamic translated values such as:

        element.textContent =
            operationalTranslations.connected;

    are naturally ignored because they are not quoted literals.
    """

    findings: list[
        tuple[Path, int, str]
    ] = []

    for match in (
        JAVASCRIPT_VISIBLE_TEXT_PATTERN.finditer(
            content
        )
    ):

        raw_text = (
            match.group(
                "text"
            )
        )

        if (
            "{{" in raw_text
            or
            "{%" in raw_text
        ):

            continue

        text = normalize_visible_text(
            raw_text
        )

        if is_allowed_hardcoded_text(
            text
        ):

            continue

        line_number = (
            content.count(
                "\n",
                0,
                match.start(),
            )
            + 1
        )

        findings.append(
            (
                template_file,
                line_number,
                text,
            )
        )

    return findings


def find_hardcoded_template_strings() -> list[
    tuple[Path, int, str]
]:
    """
    Locate visible hardcoded strings in HTML templates.

    Static HTML and simple JavaScript-generated visible text
    are inspected separately to avoid parser false positives.
    """

    findings: list[
        tuple[Path, int, str]
    ] = []

    for template_file in sorted(
        TEMPLATE_DIRECTORY.rglob(
            "*.html"
        )
    ):

        try:

            content = (
                template_file.read_text(
                    encoding="utf-8"
                )
            )

        except OSError:

            continue

        findings.extend(
            find_static_html_strings(
                template_file,
                content,
            )
        )

        findings.extend(
            find_javascript_visible_strings(
                template_file,
                content,
            )
        )

    #
    # Remove duplicate findings while preserving
    # deterministic ordering.
    #
    unique_findings = sorted(
        set(
            findings
        ),
        key=lambda finding: (
            str(
                finding[0]
            ),
            finding[1],
            finding[2],
        ),
    )

    return unique_findings


def validate_python_syntax() -> bool:
    """
    Validate this audit script itself.
    """

    try:

        source = (
            Path(__file__).read_text(
                encoding="utf-8"
            )
        )

        ast.parse(
            source
        )

    except (
        OSError,
        SyntaxError,
    ) as error:

        print(
            f"[ERROR] Audit script syntax: {error}"
        )

        return False

    return True


def main() -> None:
    """
    Run the full internationalization audit.
    """

    print(
        "=" * 60
    )

    print(
        "SVX Guardian I18N Audit"
    )

    print(
        "=" * 60
    )

    all_valid = (
        validate_python_syntax()
    )

    (
        locale_valid,
        reference_keys,
    ) = validate_locale_consistency()

    if not locale_valid:

        all_valid = False

    used_keys = (
        find_used_translation_keys()
    )

    missing_template_keys = sorted(
        used_keys
        -
        reference_keys
    )

    unused_keys = sorted(
        reference_keys
        -
        used_keys
    )

    hardcoded_strings = (
        find_hardcoded_template_strings()
    )

    print(
        "-" * 60
    )

    if missing_template_keys:

        print(
            "[ERROR] Translation keys used but undefined:"
        )

        for key in missing_template_keys:

            print(
                f"        - {key}"
            )

        all_valid = False

    else:

        print(
            "[OK]    All used translation keys exist"
        )

    if unused_keys:

        print(
            "[WARN]  Translation keys currently unused:"
        )

        for key in unused_keys:

            print(
                f"        - {key}"
            )

    else:

        print(
            "[OK]    No unused translation keys"
        )

    if hardcoded_strings:

        print(
            "[ERROR] Hardcoded visible strings:"
        )

        for (
            template_file,
            line_number,
            text,
        ) in hardcoded_strings:

            relative_path = (
                template_file.relative_to(
                    PROJECT_ROOT
                )
            )

            print(
                f"        {relative_path}:"
                f"{line_number}: {text}"
            )

        all_valid = False

    else:

        print(
            "[OK]    No hardcoded visible strings"
        )

    print(
        "-" * 60
    )

    if all_valid:

        print(
            "I18N STATUS: PASSED"
        )

        sys.exit(
            0
        )

    print(
        "I18N STATUS: FAILED"
    )

    sys.exit(
        1
    )


if __name__ == "__main__":
    main()
