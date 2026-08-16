"""
Translation Manager diagnostic script.

This module is intended for manual execution and is not part
of the automated pytest test suite.
"""

from .core.i18n import TranslationManager


# Prevent pytest from treating this diagnostic module as a test container.
__test__ = False


def show_language(language: str) -> None:
    """
    Display a basic translation sample for one language.
    """

    translator = TranslationManager(language)

    print("=" * 50)
    print(f"Language: {language}")
    print("=" * 50)

    print(translator.gettext("APP_NAME"))
    print()

    print(translator.gettext("HOSTNAME"))
    print(translator.gettext("CPU_TEMP"))
    print(translator.gettext("CPU_USAGE"))
    print(translator.gettext("RAM_USAGE"))
    print(translator.gettext("DISK_USAGE"))
    print(translator.gettext("UPTIME"))
    print()

    print(
        f"{translator.gettext('SVXLINK')} : "
        f"{translator.gettext('RUNNING')}"
    )

    print(
        f"{translator.gettext('ECHOLINK')} : "
        f"{translator.gettext('NOT_MONITORED')}"
    )

    print(
        f"{translator.gettext('REFLECTOR')} : "
        f"{translator.gettext('NOT_MONITORED')}"
    )

    print()

    print(translator.gettext("STATUS_HEALTHY"))
    print(translator.gettext("REASON_NONE"))
    print()


def main() -> None:
    """
    Display translation samples.
    """

    show_language("en")
    show_language("it")


if __name__ == "__main__":
    main()
