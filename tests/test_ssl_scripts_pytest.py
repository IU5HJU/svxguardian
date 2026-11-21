"""
Tests for the SSL installation helpers (install/ssl/ssl-common.sh and the
scripts that use it).

"openssl x509 -checkhost" prints "does match certificate" or "does NOT match
certificate" and exits with status 0 in both cases, so a script that only
tests the exit status accepts a certificate for the wrong hostname. These
tests make sure the hostname check reads the text instead.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
SSL_DIR = ROOT / "install" / "ssl"
COMMON = SSL_DIR / "ssl-common.sh"

pytestmark = pytest.mark.skipif(
    shutil.which("openssl") is None or shutil.which("bash") is None,
    reason="openssl and bash are required",
)


def run(*command: str, stdin: str = "") -> subprocess.CompletedProcess:
    return subprocess.run(
        list(command),
        input=stdin,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def make_certificate(directory: Path, name: str, *dns: str) -> tuple[Path, Path]:
    """Create a self-signed certificate valid for the given DNS names."""

    key = directory / f"{name}.key"
    certificate = directory / f"{name}.pem"

    result = run(
        "openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
        "-days", "2",
        "-keyout", str(key),
        "-out", str(certificate),
        "-subj", f"/CN={dns[0]}",
        "-addext", "subjectAltName=" + ",".join(f"DNS:{d}" for d in dns),
    )
    assert result.returncode == 0, result.stderr

    return certificate, key


def matches(certificate: Path, hostname: str) -> bool:
    result = run(
        "bash",
        "-c",
        'source "$1"; ssl_certificate_matches_hostname "$2" "$3"',
        "bash",
        str(COMMON),
        str(certificate),
        hostname,
    )

    return result.returncode == 0


def test_hostname_check_accepts_the_right_name(tmp_path: Path) -> None:
    certificate, _ = make_certificate(tmp_path, "a", "node.example.org")

    assert matches(certificate, "node.example.org")


def test_hostname_check_rejects_another_name(tmp_path: Path) -> None:
    """The case the old scripts got wrong."""

    certificate, _ = make_certificate(tmp_path, "a", "node.example.org")

    assert not matches(certificate, "other.example.org")


def test_openssl_checkhost_exit_status_is_not_enough(tmp_path: Path) -> None:
    """Documents why the helper reads the text and not the exit status."""

    certificate, _ = make_certificate(tmp_path, "a", "node.example.org")

    result = run(
        "openssl", "x509", "-in", str(certificate), "-noout",
        "-checkhost", "other.example.org",
    )

    assert "does NOT match" in result.stdout + result.stderr
    assert result.returncode == 0


def test_hostname_check_accepts_a_wildcard(tmp_path: Path) -> None:
    certificate, _ = make_certificate(tmp_path, "w", "*.example.org")

    assert matches(certificate, "node.example.org")
    assert not matches(certificate, "node.example.net")


def test_hostname_check_uses_the_first_certificate_of_the_file(
    tmp_path: Path,
) -> None:
    """A PEM that starts with the chain must be rejected."""

    server, _ = make_certificate(tmp_path, "server", "node.example.org")
    chain, _ = make_certificate(tmp_path, "chain", "ca.example.org")

    good = tmp_path / "good.pem"
    good.write_text(server.read_text() + chain.read_text())

    reversed_order = tmp_path / "reversed.pem"
    reversed_order.write_text(chain.read_text() + server.read_text())

    assert matches(good, "node.example.org")
    assert not matches(reversed_order, "node.example.org")


def test_hostname_check_fails_on_a_missing_file(tmp_path: Path) -> None:
    assert not matches(tmp_path / "nonexistent.pem", "node.example.org")


def test_scripts_do_not_call_checkhost_directly() -> None:
    """Every hostname check must go through the helper."""

    offenders = []

    for script in list((ROOT / "install").rglob("*.sh")):
        if script == COMMON:
            continue

        if "-checkhost" in script.read_text():
            offenders.append(str(script.relative_to(ROOT)))

    assert offenders == []


def test_scripts_that_check_the_hostname_load_the_helper() -> None:
    for name in (
        "verify-certificate.sh",
        "install-certificate.sh",
        "setup-https.sh",
    ):
        assert "ssl-common.sh" in (SSL_DIR / name).read_text(), name

    apache = ROOT / "install" / "apache" / "configure-apache.sh"
    assert "ssl-common.sh" in apache.read_text()


@pytest.mark.skipif(
    os.geteuid() != 0,
    reason="verify-certificate.sh refuses to run unless it is root",
)
def test_verify_certificate_script_rejects_the_wrong_hostname(
    tmp_path: Path,
) -> None:
    certificate, key = make_certificate(tmp_path, "a", "node.example.org")
    script = str(SSL_DIR / "verify-certificate.sh")

    wrong = run(
        "bash", script,
        stdin=f"{certificate}\n{key}\nother.example.org\n",
    )

    assert wrong.returncode == 1
    assert "SSL_CERTIFICATE_STATUS=INVALID" in wrong.stdout

    right = run(
        "bash", script,
        stdin=f"{certificate}\n{key}\nnode.example.org\n",
    )

    assert right.returncode == 0
    assert "SSL_CERTIFICATE_STATUS=VALID" in right.stdout
