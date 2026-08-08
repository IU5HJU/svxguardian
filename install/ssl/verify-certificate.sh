#!/usr/bin/env bash

set -euo pipefail


echo
echo "SVX Guardian SSL Certificate Verifier"
echo


if [[ "${EUID}" -ne 0 ]]; then
    echo "ERROR: this script must be executed as root."
    echo
    echo "Run:"
    echo "    sudo $0"
    echo

    exit 1
fi


read -r -p "Certificate PEM file: " CERTIFICATE_FILE

if [[ ! -f "${CERTIFICATE_FILE}" ]]; then
    echo
    echo "ERROR: certificate file not found:"
    echo "    ${CERTIFICATE_FILE}"
    echo

    exit 1
fi


read -r -p "Private key file: " PRIVATE_KEY_FILE

if [[ ! -f "${PRIVATE_KEY_FILE}" ]]; then
    echo
    echo "ERROR: private key file not found:"
    echo "    ${PRIVATE_KEY_FILE}"
    echo

    exit 1
fi


read -r -p "Expected hostname / FQDN: " HOSTNAME

if [[ -z "${HOSTNAME}" ]]; then
    echo
    echo "ERROR: hostname cannot be empty."
    echo

    exit 1
fi


echo
echo "Certificate summary"
echo

openssl x509 \
    -in "${CERTIFICATE_FILE}" \
    -noout \
    -subject \
    -issuer \
    -dates


echo
echo "Subject Alternative Names"
echo

openssl x509 \
    -in "${CERTIFICATE_FILE}" \
    -noout \
    -ext subjectAltName


echo
echo "Checking hostname..."
echo

if openssl x509 \
    -in "${CERTIFICATE_FILE}" \
    -noout \
    -checkhost "${HOSTNAME}" \
    >/dev/null 2>&1
then
    echo "[OK] Certificate matches hostname: ${HOSTNAME}"
else
    echo "[ERROR] Certificate does not match hostname: ${HOSTNAME}"
    echo "SSL_CERTIFICATE_STATUS=INVALID"
    exit 1
fi


echo
echo "Checking certificate validity..."
echo

if openssl x509 \
    -in "${CERTIFICATE_FILE}" \
    -noout \
    -checkend 0 \
    >/dev/null 2>&1
then
    echo "[OK] Certificate is currently valid"
else
    echo "[ERROR] Certificate is expired or not yet valid"
    echo "SSL_CERTIFICATE_STATUS=INVALID"
    exit 1
fi


echo
echo "Checking certificate/private-key pair..."
echo

CERTIFICATE_PUBLIC_KEY_HASH="$(
    openssl x509 \
        -in "${CERTIFICATE_FILE}" \
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
        -in "${PRIVATE_KEY_FILE}" \
        -pubout \
        -outform DER \
    | sha256sum \
    | awk '{print $1}'
)"


if [[ "${CERTIFICATE_PUBLIC_KEY_HASH}" == "${PRIVATE_KEY_PUBLIC_HASH}" ]]; then
    echo "[OK] Certificate and private key match"
else
    echo "[ERROR] Certificate and private key do NOT match"
    echo "SSL_CERTIFICATE_STATUS=INVALID"
    exit 1
fi


CERTIFICATE_COUNT="$(
    grep -c \
        "BEGIN CERTIFICATE" \
        "${CERTIFICATE_FILE}" \
    || true
)"


echo
echo "Certificate chain information"
echo
echo "Certificates found in PEM file: ${CERTIFICATE_COUNT}"


if [[ "${CERTIFICATE_COUNT}" -gt 1 ]]; then
    echo "[OK] PEM file contains a certificate chain"
else
    echo "[WARN] PEM file contains only one certificate"
    echo "[WARN] Apache may require an intermediate certificate chain."
fi


echo
echo "SSL CERTIFICATE STATUS: VALID"
echo
echo "Hostname:"
echo "    ${HOSTNAME}"
echo
echo "Certificate:"
echo "    ${CERTIFICATE_FILE}"
echo
echo "Private key:"
echo "    ${PRIVATE_KEY_FILE}"
echo
echo "SSL_CERTIFICATE_STATUS=VALID"
echo

exit 0
