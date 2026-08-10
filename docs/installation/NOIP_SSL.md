# SVX Guardian - No-IP SSL Certificate Setup

> 🇬🇧 **English documentation**  
> 🇮🇹 [Documentazione italiana](../it/installation/NOIP_SSL.md)

## Scope

This document describes the No-IP SSL certificate workflow tested during SVX Guardian development.

The procedure was validated using:

- a No-IP DDNS hostname;
- a DV certificate issued through No-IP;
- DNS TXT verification;
- PEM Chain download;
- Apache as an HTTPS reverse proxy;
- Gunicorn bound locally to `127.0.0.1:8080`.

The procedure was tested in August 2026.

No-IP may change its website, certificate products, verification workflow, terminology or certificate download formats over time.

For the generic SVX Guardian HTTPS architecture, see:

```text
docs/installation/HTTPS.md
```

---

## Important Principle

The No-IP workflow described in this document does not require public TCP port 80 to be available for SVX Guardian.

Certificate validation was performed using DNS TXT verification.

This is particularly useful in domestic amateur-radio installations where:

- port 80 may already be used by another service;
- port 80 may be blocked;
- the router may impose limitations;
- multiple services may share the same public IP address;
- the radio amateur may not have full control over standard ports.

SVX Guardian can therefore be published over HTTPS without depending on HTTP port 80.

---

## Requirements

Before starting, you need:

- a working No-IP hostname;
- access to the No-IP account managing the hostname;
- SVX Guardian running locally;
- OpenSSL installed;
- Apache installed;
- Gunicorn configured for SVX Guardian;
- root or sudo access to the Raspberry Pi.

The examples in this document use:

```text
example.ddns.net
```

Always replace this with the real hostname of the node.

---

## Recommended Guided Procedure

The recommended entry point is:

```bash
sudo ./install/ssl/setup-https.sh
```

To start a new configuration, choose:

```text
1) Start a new HTTPS certificate setup
```

The guided procedure calls the CSR generation script and prepares the local SSL directory.

---

## SSL Directory

SVX Guardian uses:

```text
/etc/svxguardian/ssl
```

Expected permissions:

```text
root:root
700
```

Private key:

```text
/etc/svxguardian/ssl/example.ddns.net.key
```

Recommended permissions:

```text
root:root
600
```

CSR:

```text
/etc/svxguardian/ssl/example.ddns.net.csr
```

Recommended permissions:

```text
root:root
644
```

Certificate:

```text
/etc/svxguardian/ssl/example.ddns.net.pem
```

Recommended permissions:

```text
root:root
644
```

---

## Step 1 - Generate the Private Key and CSR

Run:

```bash
sudo ./install/ssl/create-csr.sh
```

The script asks for:

```text
Hostname / FQDN
Country code
State / Province
Locality / City
Organization
Organizational Unit
```

The private key is generated locally on the Raspberry Pi and must remain on the node.

The CSR can be submitted to No-IP.

---

## CSR Requirements Observed During Testing

During the real certificate procedure, a CSR containing only the Common Name was not accepted.

The following errors were encountered:

```text
Invalid two character ISO-3166 country code.
```

and:

```text
CSR must contain a State/Province
```

For this reason, the SVX Guardian `create-csr.sh` script requests all fields required by the tested No-IP workflow.

---

## Country Code

The country must be entered using a two-character ISO code.

Examples:

```text
Italy:
IT

Germany:
DE

France:
FR

Spain:
ES

United Kingdom:
GB

United States:
US
```

Do not enter the full country name.

Incorrect:

```text
Italy
Italia
Germany
```

Correct:

```text
IT
DE
```

---

## State / Province

The State / Province field must not be left empty.

Example:

```text
Tuscany
```

Use the region, state or province appropriate for the certificate holder.

---

## Locality / City

Enter the appropriate city or locality.

Example:

```text
Example City
```

---

## Common Name

The Common Name must match the complete hostname used to reach SVX Guardian.

Example:

```text
example.ddns.net
```

Do not use:

```text
localhost
192.168.1.100
raspberrypi
```

unless the certificate has specifically been issued for those identifiers.

---

## Example CSR Subject

A complete Subject may look like:

```text
C=IT
ST=Tuscany
L=Example City
O=SVX Guardian
OU=Amateur Radio
CN=example.ddns.net
```

Organization-related fields may differ.

---

## Inspect the CSR

To inspect the generated CSR:

```bash
sudo openssl req \
  -in /etc/svxguardian/ssl/example.ddns.net.csr \
  -noout \
  -subject \
  -text
```

Check that the Subject contains:

- the correct hostname;
- country;
- state or region;
- locality;
- any organizational information supplied.

---

## Display the CSR

To display the CSR that will be submitted to No-IP:

```bash
sudo cat /etc/svxguardian/ssl/example.ddns.net.csr
```

Copy the complete block:

```text
-----BEGIN CERTIFICATE REQUEST-----
...
-----END CERTIFICATE REQUEST-----
```

The CSR can safely be supplied to the certificate provider.

---

## Never Upload the Private Key

Never display, submit or upload:

```text
/etc/svxguardian/ssl/example.ddns.net.key
```

The private key must remain on the Raspberry Pi.

It must not be:

- pasted into the No-IP website;
- attached to an email;
- included in documentation;
- uploaded to GitHub;
- sent through chat or messaging software;
- copied to uncontrolled cloud services.

---

## Step 2 - Start the Certificate Procedure on No-IP

Log into the No-IP account managing the hostname.

Open the SSL certificate section.

During the tested workflow, the certificate could be created or activated from the SSL certificate area.

When No-IP asks for the CSR, paste the CSR generated by SVX Guardian.

---

## Step 3 - DNS TXT Verification

During the tested procedure, No-IP generated a TXT verification value.

The TXT record was associated directly with the DDNS hostname.

Example:

```text
example.ddns.net. 300 IN TXT "<verification-token>"
```

The token shown above is intentionally fictitious.

Always use the exact TXT value displayed by No-IP.

---

## Important TXT Record Note

Do not automatically assume that the TXT hostname must be:

```text
_acme-challenge.example.ddns.net
```

During the tested No-IP workflow, the TXT record was associated directly with the DDNS hostname.

Always use:

- the hostname specified by No-IP;
- the value specified by No-IP.

---

## Check TXT Propagation

If `dig` is available:

```bash
dig TXT example.ddns.net +short
```

Public DNS resolvers can also be queried.

Cloudflare:

```bash
dig @1.1.1.1 TXT example.ddns.net +short
```

Google:

```bash
dig @8.8.8.8 TXT example.ddns.net +short
```

The returned value should match the value supplied by No-IP.

---

## Installing dig

On recent Raspberry Pi OS / Debian systems, the package may be:

```bash
sudo apt update
sudo apt install bind9-dnsutils
```

On other systems the following may also be available:

```bash
sudo apt install dnsutils
```

Package names may vary depending on the distribution and version.

---

## Repository Mirror Problems

During testing, installation of the DNS utilities temporarily returned:

```text
404 Not Found
```

errors for some `bind9-*` packages.

The first recovery action should be:

```bash
sudo apt update
```

Then retry the package installation.

Do not immediately modify repository configuration if the problem may simply be caused by outdated local package indexes.

---

## Step 4 - Complete Verification on No-IP

Once the TXT record is publicly visible, return to the No-IP interface and complete the verification.

During testing, the certificate eventually reached the status:

```text
ACTIVE
```

Do not continue with the Apache configuration until the certificate has actually been issued.

---

## Step 5 - Download the Certificate

During testing, No-IP offered multiple certificate download formats.

The format successfully used with SVX Guardian was:

```text
PEM Chain
```

This format contained:

- the hostname certificate;
- intermediate certificates;
- the certificate chain required by Apache.

---

## Why Use PEM Chain

The PEM Chain can be used directly by Apache as:

```text
SSLCertificateFile
```

During the tested installation, the PEM file contained three certificates.

SVX Guardian can automatically verify how many certificates are contained in the file.

---

## Copy the PEM Chain to the Raspberry Pi

Copy the downloaded file to the Raspberry Pi using, for example:

- SFTP;
- SCP;
- FileZilla;
- another secure file-transfer method.

A temporary location can be:

```text
/home/<user>/
```

Example:

```text
/home/<user>/example_ddns_net.pem
```

The private key must not be transferred away from the Raspberry Pi.

---

## Step 6 - Verify the Downloaded Certificate

Run:

```bash
sudo ./install/ssl/verify-certificate.sh
```

Provide:

```text
Certificate PEM file:
<path to downloaded PEM>

Private key file:
/etc/svxguardian/ssl/example.ddns.net.key

Expected hostname / FQDN:
example.ddns.net
```

The script verifies:

- certificate hostname;
- Subject Alternative Name;
- certificate validity;
- certificate/private-key correspondence;
- PEM Chain content.

Expected result:

```text
SSL_CERTIFICATE_STATUS=VALID
```

---

## Example Successful Verification

A successful verification includes:

```text
[OK] Certificate matches hostname
[OK] Certificate is currently valid
[OK] Certificate and private key match
[OK] PEM file contains a certificate chain
```

and ends with:

```text
SSL_CERTIFICATE_STATUS=VALID
```

---

## Certificate and Private Key Do Not Match

If the certificate does not match the private key, do not continue.

One possible cause is generating a new private key after the CSR has already been submitted to the provider.

The certificate is issued for the key used when the original CSR was generated.

Do not regenerate:

```text
example.ddns.net.key
```

after certificate issuance unless a new key/certificate pair is intentionally required.

---

## Step 7 - Install the PEM Chain

Run:

```bash
sudo ./install/ssl/install-certificate.sh
```

The script:

- verifies the certificate;
- verifies the private key;
- checks the hostname;
- checks the PEM content;
- creates a backup of any existing certificate;
- installs the new PEM;
- applies the correct permissions;
- performs a final verification.

Expected result:

```text
SSL_CERTIFICATE_INSTALL_STATUS=SUCCESS
```

The private key is not modified.

---

## Step 8 - Configure Apache

Run:

```bash
sudo ./install/apache/configure-apache.sh
```

Typical answers:

```text
Hostname / FQDN:
example.ddns.net

Local HTTPS port [443]:
<Enter>

Backend host [127.0.0.1]:
<Enter>

SVX Guardian backend port [8080]:
<Enter>
```

The script:

- verifies the certificate;
- verifies the local backend;
- enables the required Apache modules;
- creates a backup of the existing configuration;
- generates the VirtualHost from the template;
- runs `apache2ctl configtest`;
- reloads Apache;
- performs a local HTTPS test.

Expected result:

```text
APACHE_HTTPS_STATUS=SUCCESS
```

---

## Apache Architecture

The tested configuration is:

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
   |
   v
SVX Guardian
```

Gunicorn is not directly exposed to the Internet.

---

## Step 9 - Router Configuration

Standard configuration:

```text
Internet TCP 443
        ->
Raspberry Pi TCP 443
```

If public port 443 is unavailable:

```text
Internet TCP 8443
        ->
Raspberry Pi TCP 443
```

The public URL then becomes:

```text
https://example.ddns.net:8443
```

The certificate remains valid because it identifies the hostname rather than the TCP port.

---

## Do Not Forward TCP 8080

Remove any obsolete router rule exposing:

```text
TCP 8080
```

The tested SVX Guardian production configuration uses:

```text
127.0.0.1:8080
```

for Gunicorn.

The backend must remain locally accessible only.

---

## Step 10 - Test HTTPS Locally

Before testing Internet access:

```bash
curl \
  --resolve example.ddns.net:443:127.0.0.1 \
  https://example.ddns.net/api/state
```

A valid JSON response confirms that the following components are working:

```text
Apache HTTPS
Certificate
Reverse proxy
Gunicorn
SVX Guardian
```

without involving the router.

---

## Step 11 - Field Test

Use a smartphone.

Disable Wi-Fi.

Use the mobile network.

Open:

```text
https://example.ddns.net
```

Then test:

```text
https://example.ddns.net/monitor
```

Verify:

- no SSL certificate warnings;
- complete dashboard loading;
- operational view loading;
- live data updates;
- EchoLink information updates;
- language selection;
- correct behavior on the mobile device.

---

## Troubleshooting

### Certificate is ACTIVE but HTTPS does not work

Check:

```bash
sudo apache2ctl configtest
```

Then:

```bash
sudo apache2ctl -S
```

Finally:

```bash
sudo ss -lntp | grep ':443'
```

---

### Backend Does Not Respond

Check:

```bash
curl -s http://127.0.0.1:8080/api/state
```

If this command fails, troubleshoot SVX Guardian/Gunicorn before Apache.

---

### Local HTTPS Works but Internet Access Does Not

Check:

- router port forwarding;
- firewall;
- DDNS resolution;
- public IP address;
- possible ISP restrictions;
- obsolete or duplicate forwarding rules.

---

### Public URL Behaves Unexpectedly

Check whether the router still contains an old forwarding rule for:

```text
8080
```

During development, an obsolete port 8080 forwarding rule caused confusing behavior even though Apache HTTPS itself was configured correctly.

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

This warning does not necessarily mean that the SVX Guardian VirtualHost is incorrect.

Check the active VirtualHosts with:

```bash
sudo apache2ctl -S
```

The warning can later be removed by defining an appropriate global Apache `ServerName`.

---

## Certificate Renewal

The exact renewal procedure depends on No-IP and the certificate product being used.

Do not assume that a future No-IP renewal procedure will remain identical to the workflow documented here.

Before renewal:

1. keep the existing private key unless key rotation is intentionally required;
2. generate the CSR as required by the provider;
3. complete DNS validation;
4. download the new PEM Chain;
5. verify the certificate;
6. install it using the SVX Guardian certificate installer;
7. reload Apache;
8. repeat the HTTPS tests.

The installer automatically creates a backup when replacing an existing certificate.

---

## Security Checklist

Before considering the installation complete, verify:

```text
[ ] The private key remains only on the node
[ ] Private key permissions are 600
[ ] SSL directory permissions are 700
[ ] The PEM certificate has been verified
[ ] The certificate matches the hostname
[ ] The certificate matches the private key
[ ] apache2ctl configtest returns Syntax OK
[ ] Gunicorn listens only on 127.0.0.1
[ ] The router does not expose TCP 8080
[ ] HTTPS works locally
[ ] HTTPS works from an external network
[ ] /monitor works from a smartphone
```

---

## Files That Must Never Be Committed

Never commit real cryptographic material:

```text
*.key
*.csr
*.pem
*.crt
*.cer
*.p12
*.pfx
```

The repository must contain only:

- scripts;
- templates;
- documentation.

Real certificates and private keys remain outside the repository.

---

## Tested Status

The procedure documented here was successfully used to reach:

```text
https://<No-IP-hostname>
```

through:

```text
No-IP hostname
    ->
DNS certificate validation
    ->
Apache HTTPS
    ->
Gunicorn
    ->
SVX Guardian
```

without requiring public TCP port 80 to be available for SVX Guardian.

No-IP is the first provider-specific SSL workflow validated with SVX Guardian.
