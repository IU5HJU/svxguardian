#!/usr/bin/env bash
#
# SVX Guardian - shared helpers for the SSL / Apache installation scripts.
#
# This file is sourced by the other scripts; it is not meant to be run
# directly and has no side effects when sourced.


# ssl_certificate_matches_hostname <certificate-file> <hostname>
#
# Succeeds only if the FIRST certificate in the PEM file is valid for
# <hostname>.
#
# Why this function exists: "openssl x509 -checkhost" prints either
#
#     Hostname example.org does match certificate
#     Hostname example.org does NOT match certificate
#
# but in both cases it exits with status 0 (at least with OpenSSL 1.1.x and
# 3.x), so testing its exit status says nothing about the hostname. The
# answer must be read from the text it prints.
#
# The PEM file has to start with the server certificate, followed by the
# intermediate certificates: a file that starts with the chain fails here.
ssl_certificate_matches_hostname() {
    local certificate_file="$1"
    local hostname="$2"
    local output

    if ! output="$(
        openssl x509 \
            -in "${certificate_file}" \
            -noout \
            -checkhost "${hostname}" \
            2>&1
    )"; then
        return 1
    fi

    [[ "${output}" == *"does match certificate"* ]]
}
