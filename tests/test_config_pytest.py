from pathlib import Path

from src.core.config import ConfigManager


def test_config_manager_preserves_legacy_fallbacks(monkeypatch):
    monkeypatch.delenv(
        "SVXGUARDIAN_SVXLINK_CONFIG",
        raising=False,
    )
    monkeypatch.delenv(
        "SVXGUARDIAN_SVXLINK_DIRECTORY",
        raising=False,
    )
    monkeypatch.delenv(
        "SVXGUARDIAN_NODE_INFO_FILE",
        raising=False,
    )
    monkeypatch.delenv(
        "SVXGUARDIAN_SVXLINK_LOG",
        raising=False,
    )

    monkeypatch.setattr(
        ConfigManager,
        "SVXLINK_DEFAULT_FILES",
        (),
    )

    monkeypatch.setattr(
        ConfigManager,
        "LEGACY_SVXLINK_CONFIG",
        Path("/etc/svxlink/svxlink.conf"),
    )
    monkeypatch.setattr(
        ConfigManager,
        "LOCAL_SVXLINK_CONFIG",
        Path(
            "/path/that/does/not/exist/"
            "svxlink.conf"
        ),
    )

    monkeypatch.setattr(
        ConfigManager,
        "LEGACY_LOG_FILE",
        Path("/var/log/svxlink"),
    )
    monkeypatch.setattr(
        ConfigManager,
        "LOCAL_LOG_FILE",
        Path(
            "/path/that/does/not/exist/"
            "svxlink.log"
        ),
    )

    config = ConfigManager()

    assert (
        str(config.SVXLINK_DIRECTORY)
        == "/etc/svxlink"
    )
    assert (
        str(config.SVXLINK_CONFIG_FILE)
        == "/etc/svxlink/svxlink.conf"
    )
    assert (
        str(config.NODE_INFO_FILE)
        == "/etc/svxlink/node_info.json"
    )
    assert (
        str(config.SVXLINK_LOG_FILE)
        == "/var/log/svxlink"
    )


def test_config_manager_environment_overrides(monkeypatch):
    monkeypatch.setenv(
        "SVXGUARDIAN_SVXLINK_CONFIG",
        "/custom/etc/svxlink/svxlink.conf",
    )
    monkeypatch.setenv(
        "SVXGUARDIAN_SVXLINK_DIRECTORY",
        "/custom/etc/svxlink",
    )
    monkeypatch.setenv(
        "SVXGUARDIAN_NODE_INFO_FILE",
        "/custom/etc/svxlink/node_info.json",
    )
    monkeypatch.setenv(
        "SVXGUARDIAN_SVXLINK_LOG",
        "/custom/var/log/svxlink",
    )

    config = ConfigManager()

    assert (
        str(config.SVXLINK_DIRECTORY)
        == "/custom/etc/svxlink"
    )
    assert (
        str(config.SVXLINK_CONFIG_FILE)
        == "/custom/etc/svxlink/svxlink.conf"
    )
    assert (
        str(config.NODE_INFO_FILE)
        == "/custom/etc/svxlink/node_info.json"
    )
    assert (
        str(config.SVXLINK_LOG_FILE)
        == "/custom/var/log/svxlink"
    )
