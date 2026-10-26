#!/usr/bin/env bash

set -euo pipefail


echo
echo "SVX Guardian SvxLink Logrotate Configurator"
echo "============================================"
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
# Script / template paths
# ============================================================

SCRIPT_DIRECTORY="$(
    cd "$(dirname "${BASH_SOURCE[0]}")"
    pwd
)"

TEMPLATE_FILE="${SCRIPT_DIRECTORY}/svxlink.logrotate.template"

LOGROTATE_FILE="/etc/logrotate.d/svxlink"


if [[ ! -f "${TEMPLATE_FILE}" ]]; then
    echo "ERROR: logrotate template not found:"
    echo "    ${TEMPLATE_FILE}"
    echo
    echo "Make sure the SVX Guardian repository is complete."
    exit 1
fi


if ! command -v logrotate >/dev/null 2>&1; then
    echo "ERROR: logrotate is not installed."
    echo
    echo "Install it with:"
    echo "    sudo apt install logrotate"
    exit 1
fi


# ============================================================
# SvxLink logfile detection
#
# Same priority SVX Guardian itself uses
# (src/core/config.py::ConfigManager._resolve_log_file):
#
# 1. SVXGUARDIAN_SVXLINK_LOG environment override.
# 2. LOGFILE= from a SvxLink systemd defaults file.
# 3. Known existing installation layouts.
# 4. Historical Debian/Raspberry Pi OS path as fallback.
# ============================================================

LOG_FILE="${SVXGUARDIAN_SVXLINK_LOG:-}"


if [[ -z "${LOG_FILE}" ]]; then

    for DEFAULTS_FILE in \
        /etc/default/svxlink \
        /usr/local/etc/default/svxlink
    do

        if [[ -f "${DEFAULTS_FILE}" ]]; then

            DEFAULTS_VALUE="$(
                sed -n \
                    -e 's/^[[:space:]]*LOGFILE[[:space:]]*=[[:space:]]*//p' \
                    "${DEFAULTS_FILE}" \
                | tail -n 1 \
                | tr -d '"'"'"
            )"

            if [[ -n "${DEFAULTS_VALUE}" && "${DEFAULTS_VALUE}" != "syslog:" ]]; then
                LOG_FILE="${DEFAULTS_VALUE}"
                break
            fi

        fi

    done

fi


if [[ -z "${LOG_FILE}" ]]; then

    for CANDIDATE in \
        /var/log/svxlink \
        /usr/local/var/log/svxlink
    do

        if [[ -f "${CANDIDATE}" ]]; then
            LOG_FILE="${CANDIDATE}"
            break
        fi

    done

fi


LOG_FILE="${LOG_FILE:-/var/log/svxlink}"


echo "Detected SvxLink logfile:"
echo "    ${LOG_FILE}"
echo


# ============================================================
# Rotation parameters
# ============================================================

read -r -p "Maximum size before rotation [10M]: " MAX_SIZE
MAX_SIZE="${MAX_SIZE:-10M}"

if [[ ! "${MAX_SIZE}" =~ ^[0-9]+[kMG]?$ ]]; then
    echo "ERROR: invalid size (examples: 10M, 500k, 1G)."
    exit 1
fi


read -r -p "Rotations to keep [14]: " ROTATE_COUNT
ROTATE_COUNT="${ROTATE_COUNT:-14}"

if [[ ! "${ROTATE_COUNT}" =~ ^[0-9]+$ ]]; then
    echo "ERROR: rotation count must be numeric."
    exit 1
fi


# ============================================================
# Configuration summary
# ============================================================

echo
echo "Detected configuration:"
echo
echo "    Logfile:"
echo "        ${LOG_FILE}"
echo
echo "    Maximum size:"
echo "        ${MAX_SIZE}"
echo
echo "    Rotations kept:"
echo "        ${ROTATE_COUNT}"
echo
echo "    Template:"
echo "        ${TEMPLATE_FILE}"
echo
echo "    Configuration:"
echo "        ${LOGROTATE_FILE}"
echo


# ============================================================
# Backup existing configuration
# ============================================================

BACKUP_FILE=""


if [[ -f "${LOGROTATE_FILE}" ]]; then

    TIMESTAMP="$(
        date '+%Y%m%d-%H%M%S'
    )"

    BACKUP_FILE="${LOGROTATE_FILE}.backup-${TIMESTAMP}"

    echo "Existing logrotate configuration detected."
    echo "Creating backup:"
    echo "    ${BACKUP_FILE}"
    echo

    cp \
        --preserve=mode,ownership,timestamps \
        "${LOGROTATE_FILE}" \
        "${BACKUP_FILE}"

fi


# ============================================================
# Render template
# ============================================================

TEMP_FILE="$(
    mktemp
)"

trap 'rm -f "${TEMP_FILE}"' EXIT


sed \
    -e "s|@SVXGUARDIAN_SVXLINK_LOG@|${LOG_FILE}|g" \
    -e "s|@SVXGUARDIAN_LOGROTATE_SIZE@|${MAX_SIZE}|g" \
    -e "s|@SVXGUARDIAN_LOGROTATE_ROTATE@|${ROTATE_COUNT}|g" \
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
# Install configuration
# ============================================================

install \
    -o root \
    -g root \
    -m 644 \
    "${TEMP_FILE}" \
    "${LOGROTATE_FILE}"


echo "Logrotate configuration installed:"
echo "    ${LOGROTATE_FILE}"
echo


# ============================================================
# Validate configuration
# ============================================================

echo "Validating logrotate configuration..."

if ! logrotate -d "${LOGROTATE_FILE}" >/dev/null 2>&1; then

    echo
    echo "ERROR: logrotate configuration validation failed."
    echo

    logrotate -d "${LOGROTATE_FILE}" || true

    if [[ -n "${BACKUP_FILE}" && -f "${BACKUP_FILE}" ]]; then

        echo
        echo "Restoring previous configuration..."

        cp \
            "${BACKUP_FILE}" \
            "${LOGROTATE_FILE}"

    else

        rm -f "${LOGROTATE_FILE}"

    fi

    exit 1

fi

echo "[OK] logrotate configuration syntax"


# ============================================================
# Final status
# ============================================================

echo
echo "LOGROTATE_CONFIG_STATUS=SUCCESS"
echo
echo "Logfile:"
echo "    ${LOG_FILE}"
echo
echo "Maximum size:"
echo "    ${MAX_SIZE}"
echo
echo "Rotations kept:"
echo "    ${ROTATE_COUNT}"
echo
echo "Configuration:"
echo "    ${LOGROTATE_FILE}"
echo

exit 0
