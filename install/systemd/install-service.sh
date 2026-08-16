#!/usr/bin/env bash

set -euo pipefail


echo
echo "SVX Guardian Systemd Service Installer"
echo "======================================"
echo


# ============================================================
# Root privileges
# ============================================================

if [[ "${EUID}" -ne 0 ]]; then
    echo "ERROR: this script must be executed as root."
    echo
    echo "Run:"
    echo "    sudo $0"
    echo
    exit 1
fi


# ============================================================
# Script / repository paths
# ============================================================

SCRIPT_DIRECTORY="$(
    cd "$(dirname "${BASH_SOURCE[0]}")"
    pwd
)"

REPOSITORY_DIRECTORY="$(
    cd "${SCRIPT_DIRECTORY}/../.."
    pwd
)"

TEMPLATE_FILE="${SCRIPT_DIRECTORY}/svxguardian.service.template"

SERVICE_NAME="svxguardian.service"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}"


# ============================================================
# Template validation
# ============================================================

if [[ ! -f "${TEMPLATE_FILE}" ]]; then
    echo "ERROR: systemd service template not found:"
    echo "    ${TEMPLATE_FILE}"
    echo
    echo "Make sure the SVX Guardian repository is complete."
    exit 1
fi


# ============================================================
# Installation user detection
# ============================================================

#
# Normal installation:
#
#     sudo ./install/systemd/install-service.sh
#
# In this case SUDO_USER identifies the real user who launched
# the installer.
#
# For unattended/root installations the user may be explicitly
# supplied using:
#
#     SVXGUARDIAN_USER=<user>
#
# Example:
#
#     sudo SVXGUARDIAN_USER=svxlink \
#         ./install/systemd/install-service.sh
#

INSTALL_USER="${SVXGUARDIAN_USER:-}"


if [[ -z "${INSTALL_USER}" ]]; then

    if [[ -n "${SUDO_USER:-}" && "${SUDO_USER}" != "root" ]]; then

        INSTALL_USER="${SUDO_USER}"

    else

        echo "ERROR: unable to determine the SVX Guardian service user."
        echo
        echo "Run this installer using sudo from the normal user:"
        echo
        echo "    sudo $0"
        echo
        echo "or explicitly specify:"
        echo
        echo "    sudo SVXGUARDIAN_USER=<user> $0"
        echo
        exit 1

    fi

fi


if ! id "${INSTALL_USER}" >/dev/null 2>&1; then
    echo "ERROR: user does not exist:"
    echo "    ${INSTALL_USER}"
    exit 1
fi


# ============================================================
# Installation group detection
# ============================================================

INSTALL_GROUP="${SVXGUARDIAN_GROUP:-}"


if [[ -z "${INSTALL_GROUP}" ]]; then

    INSTALL_GROUP="$(
        id -gn "${INSTALL_USER}"
    )"

fi


if ! getent group "${INSTALL_GROUP}" >/dev/null 2>&1; then
    echo "ERROR: group does not exist:"
    echo "    ${INSTALL_GROUP}"
    exit 1
fi


# ============================================================
# Backend port
# ============================================================

BACKEND_PORT="${SVXGUARDIAN_BACKEND_PORT:-8080}"


if [[ ! "${BACKEND_PORT}" =~ ^[0-9]+$ ]]; then
    echo "ERROR: backend port must be numeric."
    exit 1
fi


if (( BACKEND_PORT < 1 || BACKEND_PORT > 65535 )); then
    echo "ERROR: invalid backend TCP port:"
    echo "    ${BACKEND_PORT}"
    exit 1
fi


# ============================================================
# Repository validation
# ============================================================

GUNICORN_EXECUTABLE="${REPOSITORY_DIRECTORY}/.venv/bin/gunicorn"

WEB_APPLICATION="${REPOSITORY_DIRECTORY}/src/web/app.py"


if [[ ! -x "${GUNICORN_EXECUTABLE}" ]]; then
    echo
    echo "ERROR: Gunicorn executable not found:"
    echo "    ${GUNICORN_EXECUTABLE}"
    echo
    echo "Create the SVX Guardian virtual environment and install"
    echo "the project dependencies before installing the service."
    exit 1
fi


if [[ ! -f "${WEB_APPLICATION}" ]]; then
    echo
    echo "ERROR: SVX Guardian web application not found:"
    echo "    ${WEB_APPLICATION}"
    exit 1
fi


# ============================================================
# Required commands
# ============================================================

REQUIRED_COMMANDS=(
    curl
    getent
    grep
    id
    install
    sed
    ss
    systemctl
)


for COMMAND in "${REQUIRED_COMMANDS[@]}"; do

    if ! command -v "${COMMAND}" >/dev/null 2>&1; then
        echo "ERROR: required command not found:"
        echo "    ${COMMAND}"
        exit 1
    fi

done


# ============================================================
# Configuration summary
# ============================================================

echo "Detected configuration:"
echo
echo "    User:"
echo "        ${INSTALL_USER}"
echo
echo "    Group:"
echo "        ${INSTALL_GROUP}"
echo
echo "    Repository:"
echo "        ${REPOSITORY_DIRECTORY}"
echo
echo "    Backend:"
echo "        127.0.0.1:${BACKEND_PORT}"
echo
echo "    Template:"
echo "        ${TEMPLATE_FILE}"
echo
echo "    Service:"
echo "        ${SERVICE_FILE}"
echo


# ============================================================
# Backup existing service
# ============================================================

BACKUP_FILE=""


if [[ -f "${SERVICE_FILE}" ]]; then

    TIMESTAMP="$(
        date '+%Y%m%d-%H%M%S'
    )"

    BACKUP_FILE="${SERVICE_FILE}.backup-${TIMESTAMP}"

    echo "Existing systemd service detected."
    echo "Creating backup:"
    echo "    ${BACKUP_FILE}"
    echo

    cp \
        --preserve=mode,ownership,timestamps \
        "${SERVICE_FILE}" \
        "${BACKUP_FILE}"

fi


# ============================================================
# Render systemd template
# ============================================================

TEMP_FILE="$(
    mktemp
)"

trap 'rm -f "${TEMP_FILE}"' EXIT


sed \
    -e "s|@SVXGUARDIAN_USER@|${INSTALL_USER}|g" \
    -e "s|@SVXGUARDIAN_GROUP@|${INSTALL_GROUP}|g" \
    -e "s|@SVXGUARDIAN_DIRECTORY@|${REPOSITORY_DIRECTORY}|g" \
    -e "s|@SVXGUARDIAN_BACKEND_PORT@|${BACKEND_PORT}|g" \
    "${TEMPLATE_FILE}" \
    > "${TEMP_FILE}"


# ============================================================
# Check unresolved template variables
# ============================================================

if grep -Eq '@SVXGUARDIAN_[A-Z0-9_]+@' "${TEMP_FILE}"; then

    echo
    echo "ERROR: unresolved template variables detected:"
    echo

    grep -Eo \
        '@SVXGUARDIAN_[A-Z0-9_]+@' \
        "${TEMP_FILE}" \
        | sort -u

    exit 1

fi


# ============================================================
# Install service file
# ============================================================

install \
    -o root \
    -g root \
    -m 644 \
    "${TEMP_FILE}" \
    "${SERVICE_FILE}"


echo "Systemd service installed:"
echo "    ${SERVICE_FILE}"
echo


# ============================================================
# Validate systemd unit
# ============================================================

if command -v systemd-analyze >/dev/null 2>&1; then

    echo "Checking systemd service syntax..."

    if ! systemd-analyze verify "${SERVICE_FILE}"; then

        echo
        echo "ERROR: systemd service validation failed."

        if [[ -n "${BACKUP_FILE}" && -f "${BACKUP_FILE}" ]]; then

            echo "Restoring previous service configuration..."

            cp \
                "${BACKUP_FILE}" \
                "${SERVICE_FILE}"

        else

            rm -f "${SERVICE_FILE}"

        fi

        systemctl daemon-reload

        exit 1

    fi

    echo "[OK] systemd service syntax"

fi


# ============================================================
# Reload systemd
# ============================================================

echo
echo "Reloading systemd..."

systemctl daemon-reload


# ============================================================
# Enable service
# ============================================================

echo
echo "Enabling SVX Guardian at boot..."

systemctl enable "${SERVICE_NAME}" >/dev/null


# ============================================================
# Restart service
# ============================================================

echo
echo "Starting SVX Guardian..."

if ! systemctl restart "${SERVICE_NAME}"; then

    echo
    echo "ERROR: unable to start ${SERVICE_NAME}"
    echo

    systemctl status \
        "${SERVICE_NAME}" \
        --no-pager \
        -l \
        || true

    exit 1

fi


# ============================================================
# Wait for startup
# ============================================================

STARTUP_ATTEMPTS=10
STARTUP_DELAY=1
SERVICE_READY=false


for ((ATTEMPT = 1; ATTEMPT <= STARTUP_ATTEMPTS; ATTEMPT++)); do

    if systemctl is-active \
        --quiet \
        "${SERVICE_NAME}"
    then

        SERVICE_READY=true
        break

    fi

    sleep "${STARTUP_DELAY}"

done


if [[ "${SERVICE_READY}" != "true" ]]; then

    echo
    echo "ERROR: SVX Guardian service is not active."
    echo

    systemctl status \
        "${SERVICE_NAME}" \
        --no-pager \
        -l \
        || true

    exit 1

fi


echo "[OK] SVX Guardian service is active"


# ============================================================
# Backend test
# ============================================================

echo
echo "Checking SVX Guardian backend..."


BACKEND_URL="http://127.0.0.1:${BACKEND_PORT}/api/state"

BACKEND_READY=false


for ((ATTEMPT = 1; ATTEMPT <= STARTUP_ATTEMPTS; ATTEMPT++)); do

    if curl \
        --silent \
        --fail \
        --max-time 5 \
        "${BACKEND_URL}" \
        >/dev/null
    then

        BACKEND_READY=true
        break

    fi

    sleep "${STARTUP_DELAY}"

done


if [[ "${BACKEND_READY}" != "true" ]]; then

    echo
    echo "ERROR: SVX Guardian backend is not reachable."
    echo
    echo "Expected:"
    echo "    ${BACKEND_URL}"
    echo

    journalctl \
        -u "${SERVICE_NAME}" \
        -n 50 \
        --no-pager \
        || true

    exit 1

fi


echo "[OK] SVX Guardian backend is reachable"


# ============================================================
# Verify backend bind address
# ============================================================

echo
echo "Checking backend network exposure..."


LISTEN_OUTPUT="$(
    ss -ltnp 2>/dev/null \
        | grep -E \
            "[[:space:]]([^[:space:]]*:)?${BACKEND_PORT}[[:space:]]" \
        || true
)"


if [[ -z "${LISTEN_OUTPUT}" ]]; then

    echo
    echo "ERROR: no listening socket found on TCP ${BACKEND_PORT}."
    exit 1

fi


if echo "${LISTEN_OUTPUT}" \
    | grep -Eq \
        "(0\.0\.0\.0|\[::\]|\*):${BACKEND_PORT}([[:space:]]|$)"
then

    echo
    echo "ERROR: SVX Guardian backend is exposed externally."
    echo
    echo "${LISTEN_OUTPUT}"
    echo
    echo "Expected bind address:"
    echo "    127.0.0.1:${BACKEND_PORT}"
    exit 1

fi


if ! echo "${LISTEN_OUTPUT}" \
    | grep -Eq \
        "127\.0\.0\.1:${BACKEND_PORT}([[:space:]]|$)"
then

    echo
    echo "ERROR: expected local backend socket not found."
    echo
    echo "${LISTEN_OUTPUT}"
    echo
    echo "Expected:"
    echo "    127.0.0.1:${BACKEND_PORT}"
    exit 1

fi


echo "[OK] Gunicorn is bound to 127.0.0.1:${BACKEND_PORT}"
echo "[OK] Backend is not exposed on 0.0.0.0:${BACKEND_PORT}"


# ============================================================
# Final status
# ============================================================

echo
echo "SVX Guardian systemd installation completed."
echo
echo "Service:"
echo "    ${SERVICE_NAME}"
echo
echo "User:"
echo "    ${INSTALL_USER}"
echo
echo "Group:"
echo "    ${INSTALL_GROUP}"
echo
echo "Repository:"
echo "    ${REPOSITORY_DIRECTORY}"
echo
echo "Backend:"
echo "    ${BACKEND_URL}"
echo
echo "SYSTEMD_INSTALL_STATUS=SUCCESS"
echo

exit 0
