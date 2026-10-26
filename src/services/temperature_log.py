"""
SVX Guardian temperature and activity logger.

Periodically samples CPU temperature together with the EchoLink and
Reflector activity signals needed to later correlate thermal load
with transmission activity for a future cooling-fan control policy.

This module only collects and persists data. It does not control
any hardware.
"""

from __future__ import annotations

import csv
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from threading import Event, Lock, Thread


logger = logging.getLogger(__name__)


CSV_HEADER = [
    "timestamp",
    "cpu_temp",
    "echolink_connection_count",
    "echolink_transmitting",
    "reflector_connection_count",
    "reflector_transmitting",
]

DEFAULT_SAMPLE_INTERVAL_SECONDS = 15.0
DEFAULT_RETENTION = timedelta(days=7)

# Roughly once a day at the default 15-second sampling interval.
DEFAULT_PRUNE_INTERVAL_SAMPLES = 5760


@dataclass(frozen=True)
class TemperatureSample:
    """
    One point-in-time temperature and activity sample.
    """

    timestamp: datetime
    cpu_temp: float
    echolink_connection_count: int
    echolink_transmitting: bool
    reflector_connection_count: int
    reflector_transmitting: bool

    def to_row(self) -> list[str]:
        """
        Serialize this sample as a CSV row matching CSV_HEADER.
        """

        return [
            self.timestamp.isoformat(
                timespec="seconds"
            ),
            f"{self.cpu_temp:.1f}",
            str(self.echolink_connection_count),
            "1" if self.echolink_transmitting else "0",
            str(self.reflector_connection_count),
            "1" if self.reflector_transmitting else "0",
        ]

    @classmethod
    def from_row(
        cls,
        row: list[str],
    ) -> "TemperatureSample | None":
        """
        Parse a CSV row into a sample.

        Returns None for any malformed row instead of raising, so a
        single corrupted line never breaks reading the rest of the
        log.
        """

        if len(row) < len(CSV_HEADER):
            return None

        try:
            return cls(
                timestamp=datetime.fromisoformat(row[0]),
                cpu_temp=float(row[1]),
                echolink_connection_count=int(row[2]),
                echolink_transmitting=row[3] == "1",
                reflector_connection_count=int(row[4]),
                reflector_transmitting=row[5] == "1",
            )

        except (ValueError, IndexError):
            return None

    def to_dict(self) -> dict[str, object]:
        """
        Export this sample as a JSON-serializable dictionary.
        """

        return {
            "timestamp": self.timestamp.isoformat(
                timespec="seconds"
            ),
            "cpu_temp": self.cpu_temp,
            "echolink_connection_count": (
                self.echolink_connection_count
            ),
            "echolink_transmitting": self.echolink_transmitting,
            "reflector_connection_count": (
                self.reflector_connection_count
            ),
            "reflector_transmitting": self.reflector_transmitting,
        }


SampleProvider = Callable[[], "TemperatureSample | None"]


class TemperatureLogger:
    """
    Samples node temperature/activity on a fixed interval and
    appends it to a retention-bounded CSV log.

    The logger degrades gracefully: if the log directory cannot be
    created or written to (for example during local development or
    tests, where the SVX Guardian systemd state directory does not
    exist), logging is simply disabled instead of raising.

    Because the log is retention-bounded by construction, reading it
    back in full is always cheap, unlike the externally-growing
    SvxLink logfile.
    """

    def __init__(
        self,
        log_file: Path | str,
        sample_interval: float = DEFAULT_SAMPLE_INTERVAL_SECONDS,
        retention: timedelta = DEFAULT_RETENTION,
        prune_interval_samples: int = (
            DEFAULT_PRUNE_INTERVAL_SAMPLES
        ),
    ) -> None:
        self.log_file = Path(log_file)
        self.sample_interval = max(
            1.0,
            float(sample_interval),
        )
        self.retention = retention
        self.prune_interval_samples = max(
            1,
            int(prune_interval_samples),
        )

        self.available = False

        self._write_lock = Lock()
        self._stop_event = Event()
        self._thread: Thread | None = None
        self._sample_count = 0
        self._sample_provider: SampleProvider | None = None

    def start(
        self,
        sample_provider: SampleProvider,
    ) -> bool:
        """
        Start the background sampling thread.

        Returns whether the logger was actually started.
        """

        if self._thread is not None:
            return self.available

        if not self._ensure_log_file():

            logger.warning(
                "Temperature log disabled: cannot write to %s",
                self.log_file,
            )

            return False

        self.available = True
        self._sample_provider = sample_provider

        self._thread = Thread(
            target=self._run,
            name="svxguardian-temperature-logger",
            daemon=True,
        )

        self._thread.start()

        return True

    def stop(self) -> None:
        """
        Signal the background sampling thread to stop.
        """

        self._stop_event.set()

    def _ensure_log_file(self) -> bool:
        """
        Ensure the log directory and header row exist.
        """

        try:
            self.log_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            if not self.log_file.is_file():

                with self.log_file.open(
                    "w",
                    newline="",
                    encoding="utf-8",
                ) as file:

                    csv.writer(file).writerow(
                        CSV_HEADER
                    )

        except OSError:
            return False

        return True

    def _run(self) -> None:
        """
        Background sampling loop.
        """

        while not self._stop_event.wait(
            self.sample_interval
        ):

            if self._sample_provider is None:
                continue

            try:
                sample = self._sample_provider()

            except Exception:

                logger.exception(
                    "Temperature sampling failed"
                )

                continue

            if sample is None:
                continue

            self._append(sample)

    def _append(
        self,
        sample: TemperatureSample,
    ) -> None:
        """
        Append one sample to the log, pruning periodically.
        """

        with self._write_lock:

            try:
                with self.log_file.open(
                    "a",
                    newline="",
                    encoding="utf-8",
                ) as file:

                    csv.writer(file).writerow(
                        sample.to_row()
                    )

            except OSError:

                logger.warning(
                    "Could not append temperature sample to %s",
                    self.log_file,
                )

                return

            self._sample_count += 1

            if (
                self._sample_count
                % self.prune_interval_samples
                == 0
            ):

                self._prune()

    def _prune(self) -> None:
        """
        Drop rows older than the retention window.

        The file is rewritten atomically (temp file + replace) so a
        crash or power loss mid-prune never leaves a corrupt log.
        """

        cutoff = (
            datetime.now()
            - self.retention
        )

        try:
            kept_rows: list[list[str]] = []

            with self.log_file.open(
                "r",
                newline="",
                encoding="utf-8",
            ) as file:

                reader = csv.reader(file)
                next(reader, None)

                for row in reader:

                    sample = (
                        TemperatureSample.from_row(row)
                    )

                    if sample is None:
                        continue

                    if sample.timestamp >= cutoff:
                        kept_rows.append(row)

            temp_file = self.log_file.with_suffix(
                self.log_file.suffix + ".tmp"
            )

            with temp_file.open(
                "w",
                newline="",
                encoding="utf-8",
            ) as file:

                writer = csv.writer(file)
                writer.writerow(CSV_HEADER)
                writer.writerows(kept_rows)

            temp_file.replace(
                self.log_file
            )

        except OSError:

            logger.warning(
                "Could not prune temperature log %s",
                self.log_file,
            )

    def read_samples(
        self,
        since: datetime | None = None,
    ) -> list[TemperatureSample]:
        """
        Read all stored samples, optionally filtered to those at
        or after `since`.
        """

        if not self.log_file.is_file():
            return []

        samples: list[TemperatureSample] = []

        try:
            with self.log_file.open(
                "r",
                newline="",
                encoding="utf-8",
            ) as file:

                reader = csv.reader(file)
                next(reader, None)

                for row in reader:

                    sample = (
                        TemperatureSample.from_row(row)
                    )

                    if sample is None:
                        continue

                    if (
                        since is not None
                        and sample.timestamp < since
                    ):
                        continue

                    samples.append(sample)

        except OSError:
            return []

        return samples
