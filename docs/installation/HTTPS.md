# SVX Guardian - HTTPS Setup

> 🇬🇧 **English documentation**  
> 🇮🇹 [Documentazione italiana](../it/installation/HTTPS.md)

## Overview

SVX Guardian can be exposed securely over HTTPS using:

- Apache as reverse proxy;
- Gunicorn as the local application server;
- an SSL/TLS certificate issued for the node hostname;
- a DNS or DDNS hostname;
- optional router/NAT port forwarding.

The recommended architecture is:

```text
Internet
   |
   | HTTPS
   v
Router / NAT
   |
   | public TCP port
   v
Apache HTTPS
   |
   | reverse proxy
   v
127.0.0.1:8080
   |
   v
Gunicorn
   |
   v
SVX Guardian
```

SVX Guardian does not require its backend port to be exposed directly to the Internet.

Gunicorn should normally listen only on:

```text
127.0.0.1:8080
```

Apache handles HTTPS connections and forwards requests to the local Gunicorn backend.

---

## Important Design Principle

SVX Guardian must not depend on public TCP port 80 being available.

Many amateur-radio installations operate on domestic networks where:

- port 80 may already be used by another service;
- port 80 may be blocked by the router or ISP;
- the user may not be able to reserve standard ports;
- multiple services may coexist behind the same public IP address.

For this reason, DNS-based certificate validation is preferred when available.

HTTPS can operate on:

```text
443
```

or on another public port, for example:

```text
8443
9443
10443
```

The certificate identifies the hostname, not the TCP port.

---

## Public Port vs Local Port

The port exposed by the router does not necessarily have to be the same as the port used locally by Apache.

Example 1:

```text
Internet TCP 443
        |
        v
Router
        |
        v
Raspberry Pi TCP 443
```

The dashboard can then be reached using:

```text
https://example.ddns.net
```

Example 2:

```text
Internet TCP 8443
        |
        v
Router
        |
        v
Raspberry Pi TCP 443
```

The dashboard can then be reached using:

```text
https://example.ddns.net:8443
```

The certificate remains valid because it is issued for:

```text
example.ddns.net
```

and is not tied to TCP port 443.

---

## Backend Security

SVX Guardian must not expose Gunicorn directly to the public network.

The recommended Gunicorn binding is:

```text
127.0.0.1:8080
```

The router should not forward TCP port 8080 to the Raspberry Pi.

Correct architecture:

```text
Internet
   |
   v
Apache HTTPS
   |
   v
127.0.0.1:8080
   |
   v
Gunicorn
```

Incorrect architecture:

```text
Internet
   |
   v
TCP 8080
   |
   v
Gunicorn directly exposed
```

---

## SSL Directory

SVX Guardian stores local SSL material in:

```text
/etc/svxguardian/ssl
```

Recommended directory permissions:

```text
root:root
700
```

Private key:

```text
/etc/svxguardian/ssl/<hostname>.key
root:root
600
```

Certificate / PEM chain:

```text
/etc/svxguardian/ssl/<hostname>.pem
root:root
644
```

CSR:

```text
/etc/svxguardian/ssl/<hostname>.csr
root:root
644
```

The private key must never be published, uploaded, emailed, included in documentation or committed to Git.

---

## Git Safety

The repository must ignore real certificate material.

Recommended `.gitignore` rules:

```gitignore
*.key
*.csr
*.pem
*.crt
*.cer
*.p12
*.pfx

/ssl/
/certs/
/certificates/
```

The leading `/` in directory rules is important.

For example:

```gitignore
/ssl/
```

ignores only a root-level directory named `ssl`.

It does not hide:

```text
install/ssl/
```

which contains the SVX Guardian installation scripts and must remain versioned.

---

## HTTPS Installation Tools

SVX Guardian provides the following tools:

```text
install/ssl/create-csr.sh
install/ssl/verify-certificate.sh
install/ssl/install-certificate.sh
install/ssl/setup-https.sh

install/apache/configure-apache.sh
install/apache/svxguardian.conf.template
```

---

## create-csr.sh

This script generates:

```text
/etc/svxguardian/ssl/<hostname>.key
/etc/svxguardian/ssl/<hostname>.csr
```

The private key is generated locally.

The CSR uses SHA-256 and contains the information required by the certificate provider.

The script asks for:

```text
Hostname / FQDN
Country code
State / Province
Locality / City
Organization
Organizational Unit
```

The country code must use the two-character ISO format.

Examples:

```text
IT
DE
FR
ES
GB
US
```

The private key is never displayed by the script.

The generated CSR can be submitted to the certificate provider.

---

## verify-certificate.sh

The certificate verifier checks:

- certificate hostname;
- Subject Alternative Name;
- certificate validity;
- certificate/private-key correspondence;
- number of certificates contained in the PEM;
- presence of a certificate chain.

A successful verification returns:

```text
SSL_CERTIFICATE_STATUS=VALID
```

This machine-readable status can also be used by future installer automation.

---

## install-certificate.sh

The certificate installer:

1. checks that the hostname matches;
2. checks certificate validity;
3. verifies certificate/private-key correspondence;
4. checks the PEM content;
5. creates the SSL directory if required;
6. creates a backup of an existing certificate;
7. installs the new PEM file;
8. applies secure permissions;
9. performs a final verification.

The private key is never replaced or modified.

A successful installation returns:

```text
SSL_CERTIFICATE_INSTALL_STATUS=SUCCESS
```

---

## configure-apache.sh

The Apache configurator:

1. verifies that Apache is installed;
2. asks for the hostname;
3. asks for the local HTTPS port;
4. checks the Gunicorn backend;
5. checks that the certificate and private key exist;
6. enables the required Apache modules;
7. creates a backup of the current SVX Guardian Apache configuration;
8. generates the Apache configuration from the template;
9. adds a non-standard Apache `Listen` port if required;
10. runs `apache2ctl configtest`;
11. enables the SVX Guardian site;
12. reloads Apache;
13. performs a local HTTPS test.

A successful configuration returns:

```text
APACHE_HTTPS_STATUS=SUCCESS
```

---

## setup-https.sh

This is the recommended guided entry point.

Run:

```bash
sudo ./install/ssl/setup-https.sh
```

The menu provides:

```text
1) Start a new HTTPS certificate setup
2) Continue after receiving the certificate PEM
3) Verify an installed certificate
4) Configure / repair Apache HTTPS
5) Show current SSL files
0) Exit
```

The setup can therefore be interrupted while waiting for the certificate provider and resumed later.

When waiting for certificate issuance, the procedure returns:

```text
HTTPS_SETUP_STATUS=WAITING_FOR_CERTIFICATE
```

After successful completion:

```text
HTTPS_SETUP_STATUS=SUCCESS
```

---

## Apache Template

The generic Apache template is located at:

```text
install/apache/svxguardian.conf.template
```

It does not contain node-specific values.

Template variables include:

```text
@SVXGUARDIAN_HOSTNAME@
@SVXGUARDIAN_HTTPS_PORT@
@SVXGUARDIAN_CERTIFICATE@
@SVXGUARDIAN_PRIVATE_KEY@
@SVXGUARDIAN_BACKEND_HOST@
@SVXGUARDIAN_BACKEND_PORT@
```

A typical generated configuration uses:

```text
Backend host: 127.0.0.1
Backend port: 8080
HTTPS port:   443
```

---

## Apache Modules

The HTTPS reverse proxy requires:

```text
ssl
proxy
proxy_http
headers
```

They can be enabled manually with:

```bash
sudo a2enmod ssl
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod headers
```

The automatic Apache configurator performs this step automatically.

---

## Local Backend Test

Before troubleshooting HTTPS, verify that the local backend works.

Example:

```bash
curl -s http://127.0.0.1:8080/api/state
```

A valid JSON response means:

```text
Gunicorn -> SVX Guardian
```

is operational.

---

## Local HTTPS Test

HTTPS can be tested locally without relying on router NAT or the external DNS path.

Example:

```bash
curl \
  --resolve example.ddns.net:443:127.0.0.1 \
  https://example.ddns.net/api/state
```

This verifies:

```text
Apache
  |
  v
Certificate
  |
  v
Reverse proxy
  |
  v
Gunicorn
  |
  v
SVX Guardian
```

while bypassing the public router path.

This test is particularly useful because it helps distinguish an application problem from a router, NAT or external DNS problem.

---

## Apache Configuration Test

Before reloading Apache, always run:

```bash
sudo apache2ctl configtest
```

Expected result:

```text
Syntax OK
```

Then inspect the active VirtualHosts:

```bash
sudo apache2ctl -S
```

Example:

```text
*:443 example.ddns.net
```

---

## Listening Ports

Check Apache:

```bash
sudo ss -lntp | grep ':443'
```

Check Gunicorn:

```bash
sudo ss -lntp | grep ':8080'
```

Recommended configuration:

```text
Apache:
*:443

Gunicorn:
127.0.0.1:8080
```

Gunicorn should not normally listen on:

```text
0.0.0.0:8080
```

in a production installation.

---

## Router / NAT

The router must forward the selected public HTTPS port to the Raspberry Pi.

Standard configuration:

```text
WAN TCP 443
    ->
Raspberry Pi TCP 443
```

Alternative configuration:

```text
WAN TCP 8443
    ->
Raspberry Pi TCP 443
```

Do not forward:

```text
TCP 8080
```

to Gunicorn.

The backend must remain private.

---

## Field Test

The final test should be performed from an external network.

A simple method is:

1. disable Wi-Fi on a smartphone;
2. use the mobile network;
3. open the public HTTPS URL.

Standard HTTPS:

```text
https://example.ddns.net
```

Alternative public port:

```text
https://example.ddns.net:8443
```

Then test the operational dashboard:

```text
https://example.ddns.net/monitor
```

Verify:

- no browser certificate warning;
- dashboard loads completely;
- live data updates;
- EchoLink information updates correctly;
- operational view works;
- language selection works;
- mobile browser behavior is correct.

---

## Troubleshooting Flow

Use the following order.

### 1. Check SVX Guardian

```bash
curl -s http://127.0.0.1:8080/api/state
```

If this fails, the problem is before Apache.

### 2. Check Gunicorn

```bash
sudo systemctl status svxguardian
```

Then:

```bash
sudo ss -lntp | grep ':8080'
```

Expected:

```text
127.0.0.1:8080
```

### 3. Check Apache

```bash
sudo apache2ctl configtest
```

Then:

```bash
sudo apache2ctl -S
```

### 4. Check HTTPS locally

```bash
curl \
  --resolve example.ddns.net:443:127.0.0.1 \
  https://example.ddns.net/api/state
```

If this works, Apache, TLS and SVX Guardian are working locally.

### 5. Check Router / NAT

If the local HTTPS test works but the public address does not, inspect:

- port forwarding;
- firewall;
- public IP address;
- DDNS resolution;
- ISP restrictions;
- obsolete or duplicate forwarding rules.

---

## Common Installation Mistake

A router may still contain an old rule exposing:

```text
TCP 8080
```

even after Apache HTTPS has been configured.

Remove obsolete direct-backend rules.

The expected public path is:

```text
Internet
   |
   v
Apache HTTPS
   |
   v
Gunicorn
```

not:

```text
Internet
   |
   v
Gunicorn
```

---

## Apache Global ServerName Warning

Apache may display:

```text
Could not reliably determine the server's fully qualified domain name
```

while still returning:

```text
Syntax OK
```

This warning does not necessarily mean that the SVX Guardian VirtualHost is broken.

Check the active VirtualHost with:

```bash
sudo apache2ctl -S
```

The warning can later be removed by defining an appropriate global Apache `ServerName`.

---

## Certificate Renewal

Certificate renewal depends on the certificate provider.

SVX Guardian must not assume that all providers:

- offer the same renewal process;
- expose a DNS API;
- use the same certificate lifetime;
- provide the same PEM format.

Provider-specific procedures must therefore be documented separately.

For No-IP, see:

```text
docs/installation/NOIP_SSL.md
```

---

## Security Rules

Never:

```text
publish a private key
commit a private key
upload a private key to GitHub
send a private key by email
copy a private key into documentation
```

Never expose the Gunicorn backend directly to the Internet unless there is a specific and understood reason.

Always:

- use HTTPS for public access;
- protect `/etc/svxguardian/ssl`;
- back up existing Apache configuration;
- verify certificate/private-key correspondence;
- run `apache2ctl configtest` before reload;
- test locally before troubleshooting the router;
- keep certificate-provider-specific configuration outside the application code.

---

## Current Compatibility Status

The HTTPS architecture and scripts have been tested with:

```text
Apache
Gunicorn
SVX Guardian
DNS/DDNS hostname
DNS-based certificate verification
```

The first provider-specific workflow validated during SVX Guardian development was No-IP.

Provider-specific instructions are documented separately so that the core HTTPS architecture remains independent of any single DNS or certificate provider.
