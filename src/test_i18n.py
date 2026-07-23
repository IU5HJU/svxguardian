"""
Translation Manager test.
"""

from i18n import TranslationManager


def show_language(language: str) -> None:
    t = TranslationManager(language)

    print("=" * 50)
    print(f"Language: {language}")
    print("=" * 50)

    print(t.gettext("APP_NAME"))
    print()

    print(f"{t.gettext('HOSTNAME')}")
    print(f"{t.gettext('CPU_TEMP')}")
    print(f"{t.gettext('CPU_USAGE')}")
    print(f"{t.gettext('RAM_USAGE')}")
    print(f"{t.gettext('DISK_USAGE')}")
    print(f"{t.gettext('UPTIME')}")
    print()

    print(f"{t.gettext('SVXLINK')} : {t.gettext('RUNNING')}")
    print(f"{t.gettext('ECHOLINK')} : {t.gettext('NOT_MONITORED')}")
    print(f"{t.gettext('REFLECTOR')} : {t.gettext('NOT_MONITORED')}")
    print()

    print(t.gettext("STATUS_HEALTHY"))
    print(t.gettext("REASON_NONE"))
    print()


def main():

    show_language("en")
    show_language("it")


if __name__ == "__main__":
    main()
