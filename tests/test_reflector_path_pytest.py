from pathlib import Path

from src.modules.reflector import ReflectorMonitor


def test_reflector_monitor_accepts_custom_log_file(tmp_path):
    log_file = tmp_path / "svxlink.log"
    log_file.write_text("", encoding="utf-8")

    monitor = ReflectorMonitor(
        log_file=log_file
    )

    assert monitor.log_file == Path(log_file)
