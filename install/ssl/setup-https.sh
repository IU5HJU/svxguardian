#!/usr/bin/env bash

set -euo pipefail


echo
echo "SVX Guardian HTTPS Setup"
echo "========================"
echo
echo "This guided procedure configures HTTPS for SVX Guardian."
echo
echo "The DNS/SSL workflow has currently been tested with No-IP."
echo "Public TCP port 80 is NOT required when DNS verification is used."
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

CREATE_CSR_SCRIPT="${SCRIPT_DIRECTORY}/create-csr.sh"
VERIFY_CERTIFICATE_SCRIPT="${SCRIPT_DIRECTORY}/verify-certificate.sh"
INSTALL_CERTIFICATE_SCRIPT="${SCRIPT_DIRECTORY}/install-certificate.sh"

APACHE_DIRECTORY="$(
    cd "${SCRIPT_DIRECTORY}/../apache"
    pwd
)"

CONFIGURE_APACHE_SCRIPT="${APACHE_DIRECTORY}/configure-apache.sh"


REQUIRED_SCRIPTS=(
    "${CREATE_CSR_SCRIPT}"
    "${VERIFY_CERTIFICATE_SCRIPT}"
    "${INSTALL_CERTIFICATE_SCRIPT}"
    "${CONFIGURE_APACHE_SCRIPT}"
)


for SCRIPT in "${REQUIRED_SCRIPTS[@]}"; do
    if [[ ! -x "${SCRIPT}" ]]; then
        echo
        echo "ERROR: required executable script not found:"
        echo "    ${SCRIPT}"
        echo
        echo "Make sure the SVX Guardian repository is complete."
        exit 1
    fi
done


for COMMAND in openssl curl apache2ctl; do
    if ! command -v "${COMMAND}" >/dev/null 2>&1; then
        echo
        echo "ERROR: required command not found:"
        echo "    ${COMMAND}"
        exit 1
    fi
done


SSL_DIRECTORY="/etc/svxguardian/ssl"

mkdir -p "${SSL_DIRECTORY}"
chown root:root "${SSL_DIRECTORY}"
chmod 700 "${SSL_DIRECTORY}"


echo
echo "Choose operation:"
echo
echo "  1) Start a new HTTPS certificate setup"
echo "  2) Continue after receiving the certificate PEM"
echo "  3) Verify an installed certificate"
echo "  4) Configure / repair Apache HTTPS"
echo "  5) Show current SSL files"
echo "  0) Exit"
echo

read -r -p "Selection: " SELECTION


case "${SELECTION}" in

    1)

        echo
        echo "STEP 1 - Generate private key and CSR"
        echo
        echo "SVX Guardian will create:"
        echo
        echo "    /etc/svxguardian/ssl/<hostname>.key"
        echo "    /etc/svxguardian/ssl/<hostname>.csr"
        echo
        echo "The private key must NEVER be uploaded or published."
        echo

        "${CREATE_CSR_SCRIPT}"

        echo
        echo "STEP 1 COMPLETED"
        echo
        echo "Now submit the generated CSR to your SSL provider."
        echo
        echo "No-IP workflow currently tested:"
        echo
        echo "  - create/activate the SSL certificate"
        echo "  - paste the CSR"
        echo "  - perform DNS TXT verification"
        echo "  - wait until the certificate becomes ACTIVE"
        echo "  - download the PEM Chain"
        echo
        echo "When the PEM Chain has been copied to this Raspberry,"
        echo "run this setup script again and select option 2."
        echo
        echo "HTTPS_SETUP_STATUS=WAITING_FOR_CERTIFICATE"
        ;;


    2)

        echo
        echo "STEP 2 - Verify and install certificate"
        echo

        read -r -p "Hostname / FQDN: " HOSTNAME

        if [[ -z "${HOSTNAME}" ]]; then
            echo "ERROR: hostname cannot be empty."
            exit 1
        fi


        PRIVATE_KEY="${SSL_DIRECTORY}/${HOSTNAME}.key"

        if [[ ! -f "${PRIVATE_KEY}" ]]; then
            echo
            echo "ERROR: private key not found:"
            echo "    ${PRIVATE_KEY}"
            echo
            echo "Do not generate a new key if the certificate was"
            echo "issued from an existing CSR."
            exit 1
        fi


        read -r -p "Downloaded PEM Chain file: " SOURCE_PEM

        if [[ ! -f "${SOURCE_PEM}" ]]; then
            echo
            echo "ERROR: PEM file not found:"
            echo "    ${SOURCE_PEM}"
            exit 1
        fi


        echo
        echo "Verifying downloaded certificate..."
        echo


        if ! openssl x509 \
            -in "${SOURCE_PEM}" \
            -noout \
            -checkhost "${HOSTNAME}" \
            >/dev/null 2>&1
        then
            echo "[ERROR] Certificate does not match ${HOSTNAME}"
            echo "HTTPS_SETUP_STATUS=FAILED"
            exit 1
        fi

        echo "[OK] Certificate hostname"


        if ! openssl x509 \
            -in "${SOURCE_PEM}" \
            -noout \
            -checkend 0 \
            >/dev/null 2>&1
        then
            echo "[ERROR] Certificate is expired or not yet valid"
            echo "HTTPS_SETUP_STATUS=FAILED"
            exit 1
        fi

        echo "[OK] Certificate validity"


        CERTIFICATE_PUBLIC_KEY_HASH="$(
            openssl x509 \
                -in "${SOURCE_PEM}" \
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


        if [[ "${CERTIFICATE_PUBLIC_KEY_HASH}" != "${PRIVATE_KEY_PUBLIC_HASH}" ]]; then
            echo
            echo "[ERROR] Certificate and private key do not match"
            echo "HTTPS_SETUP_STATUS=FAILED"
            exit 1
        fi

        echo "[OK] Certificate/private-key pair"


        CERTIFICATE_COUNT="$(
            grep -c \
                "BEGIN CERTIFICATE" \
                "${SOURCE_PEM}" \
            || true
        )"


        if [[ "${CERTIFICATE_COUNT}" -lt 1 ]]; then
            echo
            echo "ERROR: PEM file contains no certificate."
            echo "HTTPS_SETUP_STATUS=FAILED"
            exit 1
        fi


        echo "[OK] Certificates in PEM: ${CERTIFICATE_COUNT}"


        DESTINATION_PEM="${SSL_DIRECTORY}/${HOSTNAME}.pem"


        if [[ -f "${DESTINATION_PEM}" ]]; then
            TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"
            BACKUP_PEM="${DESTINATION_PEM}.backup-${TIMESTAMP}"

            echo
            echo "Existing certificate found."
            echo "Creating backup:"
            echo "    ${BACKUP_PEM}"

            cp \
                --preserve=mode,ownership,timestamps \
                "${DESTINATION_PEM}" \
                "${BACKUP_PEM}"

            chmod 600 "${BACKUP_PEM}"
            chown root:root "${BACKUP_PEM}"
        fi


        install \
            -o root \
            -g root \
            -m 644 \
            "${SOURCE_PEM}" \
            "${DESTINATION_PEM}"


        echo
        echo "[OK] Certificate installed:"
        echo "    ${DESTINATION_PEM}"
        echo


        read -r -p \
            "Configure Apache HTTPS now? [Y/n]: " \
            CONFIGURE_APACHE

        CONFIGURE_APACHE="${CONFIGURE_APACHE:-Y}"


        case "${CONFIGURE_APACHE}" in
            y|Y|yes|YES)
                "${CONFIGURE_APACHE_SCRIPT}"
                ;;
            *)
                echo
                echo "Apache configuration skipped."
                ;;
        esac


        echo
        echo "HTTPS_SETUP_STATUS=SUCCESS"
        ;;


    3)

        echo
        echo "Certificate verification"
        echo

        "${VERIFY_CERTIFICATE_SCRIPT}"
        ;;


    4)

        echo
        echo "Apache HTTPS configuration"
        echo

        "${CONFIGURE_APACHE_SCRIPT}"
        ;;


    5)

        echo
        echo "SVX Guardian SSL directory:"
        echo "    ${SSL_DIRECTORY}"
        echo

        find \
            "${SSL_DIRECTORY}" \
            -maxdepth 1 \
            -type f \
            -printf '%M %u:%g %f\n' \
            2>/dev/null \
        | sort
        ;;


    0)

        echo
        echo "Operation cancelled."
        exit 0
        ;;


    *)

        echo
        echo "ERROR: invalid selection."
        exit 1
        ;;

esac


echo
echo "SVX Guardian HTTPS setup finished."
echo

exit 0
