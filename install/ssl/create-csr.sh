#!/usr/bin/env bash

set -euo pipefail


echo
echo "============================================================"
echo "SVX Guardian SSL CSR Generator"
echo "============================================================"
echo


if [[ "${EUID}" -ne 0 ]]; then

    echo "ERROR: this script must be executed as root."
    echo
    echo "Run:"
    echo
    echo "    sudo $0"
    echo

    exit 1
fi


SSL_DIRECTORY="/etc/svxguardian/ssl"


echo "SSL certificate request configuration"
echo


read -r -p "Hostname / FQDN: " HOSTNAME

if [[ -z "${HOSTNAME}" ]]; then

    echo "ERROR: hostname cannot be empty."

    exit 1
fi


read -r -p "Country code (ISO-3166, e.g. IT): " COUNTRY

COUNTRY="$(
    printf '%s' "${COUNTRY}" \
    | tr '[:lower:]' '[:upper:]'
)"


if [[ ! "${COUNTRY}" =~ ^[A-Z]{2}$ ]]; then

    echo
    echo "ERROR: country must contain exactly two letters."
    echo "Example: IT, DE, FR, ES, GB, US."
    echo

    exit 1
fi


read -r -p "State / Province: " STATE

if [[ -z "${STATE}" ]]; then

    echo "ERROR: State / Province cannot be empty."

    exit 1
fi


read -r -p "Locality / City: " LOCALITY

if [[ -z "${LOCALITY}" ]]; then

    echo "ERROR: Locality / City cannot be empty."

    exit 1
fi


read -r -p \
    "Organization [SVX Guardian]: " \
    ORGANIZATION

ORGANIZATION="${ORGANIZATION:-SVX Guardian}"


read -r -p \
    "Organizational Unit [Amateur Radio]: " \
    ORGANIZATIONAL_UNIT

ORGANIZATIONAL_UNIT="${
    ORGANIZATIONAL_UNIT:-Amateur Radio
}"


PRIVATE_KEY="${SSL_DIRECTORY}/${HOSTNAME}.key"

CSR_FILE="${SSL_DIRECTORY}/${HOSTNAME}.csr"


echo
echo "The following CSR will be generated:"
echo
echo "Hostname            : ${HOSTNAME}"
echo "Country             : ${COUNTRY}"
echo "State / Province    : ${STATE}"
echo "Locality            : ${LOCALITY}"
echo "Organization        : ${ORGANIZATION}"
echo "Organizational Unit : ${ORGANIZATIONAL_UNIT}"
echo
echo "Private key         : ${PRIVATE_KEY}"
echo "CSR                 : ${CSR_FILE}"
echo


read -r -p "Continue? [y/N]: " CONFIRMATION


case "${CONFIRMATION}" in

    y|Y|yes|YES)

        ;;

    *)

        echo
        echo "Operation cancelled."
        exit 0
        ;;

esac


mkdir -p "${SSL_DIRECTORY}"

chown root:root "${SSL_DIRECTORY}"

chmod 700 "${SSL_DIRECTORY}"


if [[ -e "${PRIVATE_KEY}" ]]; then

    echo
    echo "ERROR: private key already exists:"
    echo
    echo "    ${PRIVATE_KEY}"
    echo
    echo "The existing private key has NOT been overwritten."
    echo

    exit 1
fi


if [[ -e "${CSR_FILE}" ]]; then

    echo
    echo "ERROR: CSR already exists:"
    echo
    echo "    ${CSR_FILE}"
    echo
    echo "Remove or rename it manually before continuing."
    echo

    exit 1
fi


echo
echo "Generating RSA 2048-bit private key..."
echo


openssl genrsa \
    -out "${PRIVATE_KEY}" \
    2048


chown root:root "${PRIVATE_KEY}"

chmod 600 "${PRIVATE_KEY}"


echo
echo "Generating SHA-256 certificate signing request..."
echo


openssl req \
    -new \
    -sha256 \
    -key "${PRIVATE_KEY}" \
    -out "${CSR_FILE}" \
    -subj \
    "/C=${COUNTRY}/ST=${STATE}/L=${LOCALITY}/O=${ORGANIZATION}/OU=${ORGANIZATIONAL_UNIT}/CN=${HOSTNAME}"


chown root:root "${CSR_FILE}"

chmod 644 "${CSR_FILE}"


echo
echo "Validating CSR..."
echo


openssl req \
    -in "${CSR_FILE}" \
    -noout \
    -verify


echo
echo "CSR subject:"
echo


openssl req \
    -in "${CSR_FILE}" \
    -noout \
    -subject


echo
echo "============================================================"
echo "CSR successfully generated"
echo "============================================================"
echo
echo "Private key:"
echo
echo "    ${PRIVATE_KEY}"
echo
echo "DO NOT copy, upload, publish or commit this file."
echo
echo "CSR:"
echo
echo "    ${CSR_FILE}"
echo
echo "The CSR can be safely submitted to the certificate provider."
echo
echo "To display it:"
echo
echo "    sudo cat ${CSR_FILE}"
echo
