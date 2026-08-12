"""
SVX Guardian privileged node control.

Provides a restricted interface for operational commands that require
elevated system privileges.

This module must never execute arbitrary commands supplied by a user.
Every supported operation is explicitly defined in the source code.
"""

from dataclasses import dataclass
import subprocess
import time


SYSTEMCTL_PATH = "/usr/bin/systemctl"
SUDO_PATH = "/usr/bin/sudo"

SVXLINK_SERVICE = "svxlink.service"

COMMAND_TIMEOUT = 15

VERIFY_TIMEOUT = 10.0
VERIFY_INTERVAL = 0.5


@dataclass(frozen=True)
class ControlResult:
    """
    Result of a privileged node-control operation.
    """

    success: bool
    operation: str
    return_code: int
    message: str

    previous_pid: int = 0
    current_pid: int = 0


@dataclass(frozen=True)
class ServiceState:
    """
    Minimal systemd service state used for command verification.
    """

    active_state: str = ""
    sub_state: str = ""
    main_pid: int = 0

    @property
    def running(self) -> bool:
        """
        Return whether the service is active and running.
        """

        return (
            self.active_state == "active"
            and self.sub_state == "running"
            and self.main_pid > 0
        )


class NodeControl:
    """
    Execute explicitly allowed node-control operations.
    """

    @staticmethod
    def _get_svxlink_state() -> ServiceState:
        """
        Read the current systemd state of SvxLink.

        Reading service state does not require elevated privileges.
        """

        command = [
            SYSTEMCTL_PATH,
            "show",
            SVXLINK_SERVICE,
            "--property=ActiveState",
            "--property=SubState",
            "--property=MainPID",
            "--no-pager",
        ]

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

        except (
            subprocess.TimeoutExpired,
            OSError,
        ):
            return ServiceState()

        if completed.returncode != 0:
            return ServiceState()

        values: dict[str, str] = {}

        for line in completed.stdout.splitlines():
            if "=" not in line:
                continue

            key, value = line.split(
                "=",
                1,
            )

            values[key.strip()] = value.strip()

        try:
            main_pid = int(
                values.get(
                    "MainPID",
                    "0",
                )
            )

        except ValueError:
            main_pid = 0

        return ServiceState(
            active_state=values.get(
                "ActiveState",
                "",
            ),
            sub_state=values.get(
                "SubState",
                "",
            ),
            main_pid=main_pid,
        )

    @staticmethod
    def _verify_svxlink_restart(
        previous_pid: int,
    ) -> ServiceState | None:
        """
        Verify that SvxLink returned to the running state.

        When a previous PID is known, the new PID must also differ
        from it so that a real service restart is confirmed.
        """

        deadline = (
            time.monotonic()
            + VERIFY_TIMEOUT
        )

        while time.monotonic() < deadline:

            state = NodeControl._get_svxlink_state()

            if state.running:

                pid_changed = (
                    previous_pid <= 0
                    or state.main_pid != previous_pid
                )

                if pid_changed:
                    return state

            time.sleep(
                VERIFY_INTERVAL
            )

        return None

    @staticmethod
    def restart_svxlink() -> ControlResult:
        """
        Restart the SvxLink systemd service.

        sudo is executed in non-interactive mode so the web process
        can never block waiting for a password prompt.

        A successful systemctl return code alone is not considered
        sufficient. SVX Guardian verifies that the service returns
        to active/running state with a valid PID.
        """

        previous_state = (
            NodeControl._get_svxlink_state()
        )

        previous_pid = (
            previous_state.main_pid
        )

        command = [
            SUDO_PATH,
            "-n",
            SYSTEMCTL_PATH,
            "restart",
            SVXLINK_SERVICE,
        ]

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=COMMAND_TIMEOUT,
                check=False,
            )

        except subprocess.TimeoutExpired:
            return ControlResult(
                success=False,
                operation="restart_svxlink",
                return_code=-1,
                message="timeout",
                previous_pid=previous_pid,
                current_pid=0,
            )

        except OSError:
            return ControlResult(
                success=False,
                operation="restart_svxlink",
                return_code=-1,
                message="execution_error",
                previous_pid=previous_pid,
                current_pid=0,
            )

        if completed.returncode != 0:
            return ControlResult(
                success=False,
                operation="restart_svxlink",
                return_code=completed.returncode,
                message="command_failed",
                previous_pid=previous_pid,
                current_pid=0,
            )

        verified_state = (
            NodeControl._verify_svxlink_restart(
                previous_pid
            )
        )

        if verified_state is None:

            current_state = (
                NodeControl._get_svxlink_state()
            )

            return ControlResult(
                success=False,
                operation="restart_svxlink",
                return_code=completed.returncode,
                message="verification_failed",
                previous_pid=previous_pid,
                current_pid=current_state.main_pid,
            )

        return ControlResult(
            success=True,
            operation="restart_svxlink",
            return_code=completed.returncode,
            message="ok",
            previous_pid=previous_pid,
            current_pid=verified_state.main_pid,
        )
