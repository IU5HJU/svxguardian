"""
TemperatureLogger unit tests.
"""

from datetime import datetime, timedelta
from pathlib import Path

from src.services.temperature_log import (
    TemperatureLogger,
    TemperatureSample,
)


def make_sample(
    timestamp: datetime,
    cpu_temp: float = 45.0,
) -> TemperatureSample:
    return TemperatureSample(
        timestamp=timestamp,
        cpu_temp=cpu_temp,
        echolink_connection_count=1,
        echolink_transmitting=False,
        reflector_connection_count=2,
        reflector_transmitting=True,
    )


def test_append_and_read_roundtrip(tmp_path) -> None:
    log_file = tmp_path / "temperature_log.csv"

    log = TemperatureLogger(
        log_file=log_file,
    )

    assert log._ensure_log_file() is True

    sample = make_sample(
        datetime(2026, 1, 1, 12, 0, 0)
    )

    log._append(sample)

    samples = log.read_samples()

    assert len(samples) == 1
    assert samples[0].cpu_temp == 45.0
    assert samples[0].echolink_connection_count == 1
    assert samples[0].echolink_transmitting is False
    assert samples[0].reflector_connection_count == 2
    assert samples[0].reflector_transmitting is True


def test_read_samples_filters_by_since(tmp_path) -> None:
    log_file = tmp_path / "temperature_log.csv"

    log = TemperatureLogger(
        log_file=log_file,
    )

    log._ensure_log_file()

    old_sample = make_sample(
        datetime(2026, 1, 1, 0, 0, 0)
    )

    new_sample = make_sample(
        datetime(2026, 1, 2, 0, 0, 0)
    )

    log._append(old_sample)
    log._append(new_sample)

    recent = log.read_samples(
        since=datetime(2026, 1, 1, 12, 0, 0)
    )

    assert len(recent) == 1
    assert recent[0].timestamp == new_sample.timestamp


def test_prune_drops_samples_older_than_retention(tmp_path) -> None:
    log_file = tmp_path / "temperature_log.csv"

    log = TemperatureLogger(
        log_file=log_file,
        retention=timedelta(days=7),
    )

    log._ensure_log_file()

    now = datetime.now()

    old_sample = make_sample(
        now - timedelta(days=10)
    )

    recent_sample = make_sample(
        now - timedelta(hours=1)
    )

    log._append(old_sample)
    log._append(recent_sample)

    log._prune()

    samples = log.read_samples()

    assert len(samples) == 1
    assert samples[0].cpu_temp == recent_sample.cpu_temp


def test_from_row_rejects_malformed_data() -> None:
    assert (
        TemperatureSample.from_row(["not", "enough"])
        is None
    )

    assert (
        TemperatureSample.from_row(
            [
                "not-a-timestamp",
                "x",
                "y",
                "0",
                "z",
                "1",
            ]
        )
        is None
    )


def test_read_samples_returns_empty_list_for_missing_file(
    tmp_path,
) -> None:
    log = TemperatureLogger(
        log_file=tmp_path / "does-not-exist.csv",
    )

    assert log.read_samples() == []


def test_start_disabled_when_log_directory_cannot_be_created(
    monkeypatch,
    tmp_path,
) -> None:
    log = TemperatureLogger(
        log_file=tmp_path / "state" / "temperature_log.csv",
    )

    def failing_mkdir(self, *args, **kwargs):
        raise OSError("permission denied")

    monkeypatch.setattr(
        Path,
        "mkdir",
        failing_mkdir,
    )

    started = log.start(
        lambda: None
    )

    assert started is False
    assert log.available is False


def test_start_enables_logger_and_returns_true(
    tmp_path,
) -> None:
    log = TemperatureLogger(
        log_file=tmp_path / "temperature_log.csv",
        sample_interval=60.0,
    )

    try:
        started = log.start(
            lambda: None
        )

        assert started is True
        assert log.available is True

    finally:
        log.stop()
