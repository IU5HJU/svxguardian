#!/usr/bin/env bash

set -euo pipefail


echo
echo "SVX Guardian SSL Certificate Installer"
echo


if [[ "${EUID}" -ne 0 ]]; then
    echo "ERROR: this script must be executed as root."
    echo
    echo "Run:"
    echo "    sudo $0"
    echo

    exit 1
fi


SSL_DIRECTORY="/etc/svxguardian/ssl"


read -r -p "Source PEM certificate file: " SOURCE_CERTIFICATE

if [[ ! -f "${SOURCE_CERTIFICATE}" ]]; then
    echo
    echo "ERROR: certificate file not found:"
    echo "    ${SOURCE_CERTIFICATE}"
    echo

    exit 1
fi


read -r -p "Hostname / FQDN: " HOSTNAME

if [[ -z "${HOSTNAME}" ]]; then
    echo
    echo "ERROR: hostname cannot be empty."
    echo

    exit 1
fi


PRIVATE_KEY="${SSL_DIRECTORY}/${HOSTNAME}.key"
DESTINATION_CERTIFICATE="${SSL_DIRECTORY}/${HOSTNAME}.pem"


if [[ ! -f "${PRIVATE_KEY}" ]]; then
    echo
    echo "ERROR: private key not found:"
    echo "    ${PRIVATE_KEY}"
    echo
    echo "The certificate cannot be installed safely."
    echo

    exit 1
fi


echo
echo "Checking certificate hostname..."
echo

if openssl x509 \
    -in "${SOURCE_CERTIFICATE}" \
    -noout \
    -checkhost "${HOSTNAME}" \
    >/dev/null 2>&1
then
    echo "[OK] Certificate matches hostname: ${HOSTNAME}"
else
    echo "[ERROR] Certificate does not match hostname: ${HOSTNAME}"
    echo "SSL_CERTIFICATE_INSTALL_STATUS=FAILED"
    exit 1
fi


echo
echo "Checking certificate validity..."
echo

if openssl x509 \
    -in "${SOURCE_CERTIFICATE}" \
    -noout \
    -checkend 0 \
    >/dev/null 2>&1
then
    echo "[OK] Certificate is currently valid"
else
    echo "[ERROR] Certificate is expired or not yet valid"
    echo "SSL_CERTIFICATE_INSTALL_STATUS=FAILED"
    exit 1
fi


echo
echo "Checking certificate/private-key pair..."
echo

CERTIFICATE_PUBLIC_KEY_HASH="$(
    openssl x509 \
        -in "${SOURCE_CERTIFICATE}" \
        -pubkey \
        -noout \
    | openssl pkey \
        -pubin \
        -outform DER \
    | sha256sum \
    | awk '{print $1}'
)"

PRIVATE_KEY_PUBLIC_HASH="$(
    openssl pkey \
        -in "${PRIVATE_KEY}" \
        -pubout \
        -outform DER \
    | sha256sum \
    | awk '{print $1}'
)"


if [[ "${CERTIFICATE_PUBLIC_KEY_HASH}" == "${PRIVATE_KEY_PUBLIC_HASH}" ]]; then
    echo "[OK] Certificate and private key match"
else
    echo "[ERROR] Certificate and private key do NOT match"
    echo "SSL_CERTIFICATE_INSTALL_STATUS=FAILED"
    exit 1
fi


CERTIFICATE_COUNT="$(
    grep -c \
        "BEGIN CERTIFICATE" \
        "${SOURCE_CERTIFICATE}" \
    || true
)"


if [[ "${CERTIFICATE_COUNT}" -lt 1 ]]; then
    echo
    echo "ERROR: no certificates found in PEM file."
    echo "SSL_CERTIFICATE_INSTALL_STATUS=FAILED"
    exit 1
fi


echo
echo "Certificates found in PEM file: ${CERTIFICATE_COUNT}"

if [[ "${CERTIFICATE_COUNT}" -gt 1 ]]; then
    echo "[OK] Certificate chain detected"
else
    echo "[WARN] PEM file contains only one certificate"
    echo "[WARN] An intermediate certificate may be required"
fi


mkdir -p "${SSL_DIRECTORY}"

chown root:root "${SSL_DIRECTORY}"

chmod 700 "${SSL_DIRECTORY}"


if [[ -f "${DESTINATION_CERTIFICATE}" ]]; then
    TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"

    BACKUP_FILE="${DESTINATION_CERTIFICATE}.backup-${TIMESTAMP}"

    echo
    echo "Existing certificate detected."
    echo
    echo "Creating backup:"
    echo "    ${BACKUP_FILE}"
    echo

    cp \
        --preserve=mode,ownership,timestamps \
        "${DESTINATION_CERTIFICATE}" \
        "${BACKUP_FILE}"

    chown root:root "${BACKUP_FILE}"

    chmod 600 "${BACKUP_FILE}"
fi


echo
echo "Installing certificate..."
echo

install \
    -o root \
    -g root \
    -m 644 \
    "${SOURCE_CERTIFICATE}" \
    "${DESTINATION_CERTIFICATE}"


echo
echo "Performing final verification..."
echo

if ! openssl x509 \
    -in "${DESTINATION_CERTIFICATE}" \
    -noout \
    -checkhost "${HOSTNAME}" \
    >/dev/null 2>&1
then
    echo
    echo "ERROR: installed certificate failed hostname verification."
    echo "SSL_CERTIFICATE_INSTALL_STATUS=FAILED"
    exit 1
fi


INSTALLED_PUBLIC_KEY_HASH="$(
    openssl x509 \
        -in "${DESTINATION_CERTIFICATE}" \
        -pubkey \
        -noout \
    | openssl pkey \
        -pubin \
        -outform DER \
    | sha256sum \
    | awk '{print $1}'
)"


if [[ "${INSTALLED_PUBLIC_KEY_HASH}" != "${PRIVATE_KEY_PUBLIC_HASH}" ]]; then
    echo
    echo "ERROR: installed certificate no longer matches private key."
    echo "SSL_CERTIFICATE_INSTALL_STATUS=FAILED"
    exit 1
fi


echo
echo "SSL CERTIFICATE INSTALLATION: SUCCESS"
echo
echo "Hostname:"
echo "    ${HOSTNAME}"
echo
echo "Certificate:"
echo "    ${DESTINATION_CERTIFICATE}"
echo
echo "Private key:"
echo "    ${PRIVATE_KEY}"
echo
echo "Certificates in PEM chain:"
echo "    ${CERTIFICATE_COUNT}"
echo
echo "The private key was not modified."
echo
echo "SSL_CERTIFICATE_INSTALL_STATUS=SUCCESS"
echo

exit 0
