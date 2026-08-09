#!/usr/bin/env bash

set -euo pipefail


echo
echo "SVX Guardian Apache HTTPS Configurator"
echo


if [[ "${EUID}" -ne 0 ]]; then
    echo "ERROR: this script must be executed as root."
    echo
    echo "Run:"
    echo "    sudo $0"
    echo

    exit 1
fi


SCRIPT_DIRECTORY="$(
    cd "$(dirname "${BASH_SOURCE[0]}")"
    pwd
)"

TEMPLATE_FILE="${SCRIPT_DIRECTORY}/svxguardian.conf.template"

APACHE_SITE_AVAILABLE="/etc/apache2/sites-available/svxguardian.conf"

APACHE_SITE_ENABLED="/etc/apache2/sites-enabled/svxguardian.conf"


if [[ ! -f "${TEMPLATE_FILE}" ]]; then
    echo "ERROR: Apache template not found:"
    echo "    ${TEMPLATE_FILE}"
    exit 1
fi


if ! command -v apache2ctl >/dev/null 2>&1; then
    echo "ERROR: Apache is not installed."
    exit 1
fi


read -r -p "Hostname / FQDN: " HOSTNAME

if [[ -z "${HOSTNAME}" ]]; then
    echo "ERROR: hostname cannot be empty."
    exit 1
fi


read -r -p "Local HTTPS port [443]: " HTTPS_PORT

HTTPS_PORT="${HTTPS_PORT:-443}"


if [[ ! "${HTTPS_PORT}" =~ ^[0-9]+$ ]]; then
    echo "ERROR: HTTPS port must be numeric."
    exit 1
fi


if (( HTTPS_PORT < 1 || HTTPS_PORT > 65535 )); then
    echo "ERROR: invalid TCP port."
    exit 1
fi


read -r -p "Backend host [127.0.0.1]: " BACKEND_HOST

BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"


read -r -p "SVX Guardian backend port [8080]: " BACKEND_PORT

BACKEND_PORT="${BACKEND_PORT:-8080}"


if [[ ! "${BACKEND_PORT}" =~ ^[0-9]+$ ]]; then
    echo "ERROR: backend port must be numeric."
    exit 1
fi


CERTIFICATE_FILE="/etc/svxguardian/ssl/${HOSTNAME}.pem"
PRIVATE_KEY_FILE="/etc/svxguardian/ssl/${HOSTNAME}.key"


if [[ ! -f "${CERTIFICATE_FILE}" ]]; then
    echo
    echo "ERROR: certificate not found:"
    echo "    ${CERTIFICATE_FILE}"
    exit 1
fi


if [[ ! -f "${PRIVATE_KEY_FILE}" ]]; then
    echo
    echo "ERROR: private key not found:"
    echo "    ${PRIVATE_KEY_FILE}"
    exit 1
fi


echo
echo "Checking certificate hostname..."

if ! openssl x509 \
    -in "${CERTIFICATE_FILE}" \
    -noout \
    -checkhost "${HOSTNAME}" \
    >/dev/null 2>&1
then
    echo "[ERROR] Certificate does not match ${HOSTNAME}"
    exit 1
fi

echo "[OK] Certificate matches ${HOSTNAME}"


echo
echo "Checking backend..."

if curl \
    --silent \
    --fail \
    --max-time 5 \
    "http://${BACKEND_HOST}:${BACKEND_PORT}/api/state" \
    >/dev/null
then
    echo "[OK] SVX Guardian backend is reachable"
else
    echo "[ERROR] SVX Guardian backend is not reachable"
    echo
    echo "Expected:"
    echo "    http://${BACKEND_HOST}:${BACKEND_PORT}/api/state"
    exit 1
fi


echo
echo "Enabling required Apache modules..."

a2enmod ssl >/dev/null
a2enmod proxy >/dev/null
a2enmod proxy_http >/dev/null
a2enmod headers >/dev/null


if [[ -f "${APACHE_SITE_AVAILABLE}" ]]; then
    TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"

    BACKUP_FILE="${APACHE_SITE_AVAILABLE}.backup-${TIMESTAMP}"

    echo
    echo "Existing Apache configuration detected."
    echo "Creating backup:"
    echo "    ${BACKUP_FILE}"

    cp \
        --preserve=mode,ownership,timestamps \
        "${APACHE_SITE_AVAILABLE}" \
        "${BACKUP_FILE}"
fi


TEMP_FILE="$(mktemp)"

trap 'rm -f "${TEMP_FILE}"' EXIT


sed \
    -e "s|@SVXGUARDIAN_HOSTNAME@|${HOSTNAME}|g" \
    -e "s|@SVXGUARDIAN_HTTPS_PORT@|${HTTPS_PORT}|g" \
    -e "s|@SVXGUARDIAN_CERTIFICATE@|${CERTIFICATE_FILE}|g" \
    -e "s|@SVXGUARDIAN_PRIVATE_KEY@|${PRIVATE_KEY_FILE}|g" \
    -e "s|@SVXGUARDIAN_BACKEND_HOST@|${BACKEND_HOST}|g" \
    -e "s|@SVXGUARDIAN_BACKEND_PORT@|${BACKEND_PORT}|g" \
    "${TEMPLATE_FILE}" \
    > "${TEMP_FILE}"


install \
    -o root \
    -g root \
    -m 644 \
    "${TEMP_FILE}" \
    "${APACHE_SITE_AVAILABLE}"


if [[ "${HTTPS_PORT}" != "443" ]]; then
    if ! grep -Eq \
        "^[[:space:]]*Listen[[:space:]]+${HTTPS_PORT}([[:space:]]|$)" \
        /etc/apache2/ports.conf
    then
        echo
        echo "Adding Apache Listen directive for TCP ${HTTPS_PORT}"

        printf '\nListen %s\n' "${HTTPS_PORT}" \
            >> /etc/apache2/ports.conf
    fi
fi


echo
echo "Testing Apache configuration..."

if ! apache2ctl configtest; then
    echo
    echo "ERROR: Apache configuration test failed."

    if [[ -n "${BACKUP_FILE:-}" && -f "${BACKUP_FILE}" ]]; then
        echo "Restoring previous configuration..."

        cp \
            "${BACKUP_FILE}" \
            "${APACHE_SITE_AVAILABLE}"
    else
        rm -f "${APACHE_SITE_AVAILABLE}"
    fi

    exit 1
fi


a2ensite svxguardian.conf >/dev/null


echo
echo "Reloading Apache..."

systemctl reload apache2


echo
echo "Testing local HTTPS endpoint..."

if curl \
    --silent \
    --fail \
    --max-time 10 \
    --resolve "${HOSTNAME}:${HTTPS_PORT}:127.0.0.1" \
    "https://${HOSTNAME}:${HTTPS_PORT}/api/state" \
    >/dev/null
then
    echo "[OK] HTTPS endpoint is operational"
else
    echo "[ERROR] HTTPS endpoint test failed"
    exit 1
fi


echo
echo "APACHE_HTTPS_STATUS=SUCCESS"
echo
echo "Hostname:"
echo "    ${HOSTNAME}"
echo
echo "HTTPS port:"
echo "    ${HTTPS_PORT}"
echo
echo "Backend:"
echo "    http://${BACKEND_HOST}:${BACKEND_PORT}"
echo
echo "Certificate:"
echo "    ${CERTIFICATE_FILE}"
echo
echo "Apache site:"
echo "    ${APACHE_SITE_AVAILABLE}"
echo

exit 0
