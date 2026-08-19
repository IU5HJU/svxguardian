# SVX Guardian — Roadmap

[🇮🇹 Italiano](ROADMAP.md) · 🇬🇧 **English**

**SVX Guardian** is an open-source platform for monitoring and supervising **SvxLink** radio nodes.

The goal is to build a modern, modular, reliable and easy-to-deploy system capable of monitoring the entire node: operating system, SvxLink, EchoLink, Reflector and associated services.

---

# Project Goals

- Professional monitoring of SvxLink nodes
- Modern responsive web dashboard
- Mobile-optimized operational view
- Multilingual user interface
- EchoLink and Reflector monitoring
- Real-time RAW LOG
- REST API
- Sysop / Co-Sysop authentication
- HTTPS access
- Telegram and e-mail notifications
- Automated installation and provisioning
- Open Source project for the amateur radio community

---

# Historical Milestone

## v0.1.0 — Core Framework ✅

Completed:

- [x] Initial project structure
- [x] Guardian Engine
- [x] `NodeState` model
- [x] `BaseMonitor` interface
- [x] `SystemMonitor`
- [x] Git repository
- [x] Python virtual environment
- [x] `requirements.txt`

This milestone established the architectural foundation of SVX Guardian.

---

# Current Development Status

> The following sections describe features implemented in the current development branch.  
> Future release numbers will be assigned when releases are formally defined and published.

## System Monitor ✅

- [x] System status
- [x] CPU temperature
- [x] CPU usage
- [x] RAM usage
- [x] Disk usage
- [x] Uptime
- [x] Host and platform information

---

## SvxLink Monitor ✅

- [x] SvxLink service status
- [x] PID
- [x] Service uptime
- [x] SvxLink configuration reading
- [x] Logic detection
- [x] Module detection
- [x] RX information
- [x] TX information
- [x] `node_info.json` reading
- [x] Compatibility with legacy SvxLink configurations
- [x] Guardian state integration

---

## EchoLink Monitor ✅

- [x] EchoLink status
- [x] Directory status
- [x] Connected stations
- [x] RX / transmission state
- [x] Recent connections
- [x] Station information
- [x] Unstable connection detection
- [x] Connection history reading optimization
- [x] Dashboard integration
- [x] Guardian state integration

---

## Reflector Monitor 🚧

Implemented:

- [x] Reflector connection status
- [x] Host and port
- [x] Default TalkGroup
- [x] Active TalkGroup
- [x] Talker status
- [x] Connected SvxLink node detection
- [x] Dashboard integration
- [x] Guardian state integration

In development:

- [ ] Distinction between SvxLink nodes and application users/clients
- [ ] Correct detection of users connected through applications such as LATRY
- [ ] Handling of `Node joined` / `Node left` events
- [ ] Validation with real traffic on the Legacy node
- [ ] Evaluation of future Reflector user integration into the `/monitor` view

---

## Real-time RAW LOG ✅

- [x] Incremental reading of `/var/log/svxlink`
- [x] RAW display without reinterpretation
- [x] Real-time updates
- [x] LIVE
- [x] Pause / Play
- [x] Recovery of events generated while paused
- [x] Auto-scroll ON/OFF
- [x] Display-only Clear function
- [x] Line counter
- [x] Maximum 500-line visual buffer
- [x] Logfile truncation handling
- [x] Logfile change handling
- [x] Reader separated from the `Guardian.run()` cycle
- [x] Validation with real traffic

The RAW LOG intentionally remains uninterpreted in order to give the Sysop a direct view of the events produced by SvxLink.

---

## REST API ✅

- [x] Guardian state JSON export
- [x] `/api/state` endpoint
- [x] Node information export
- [x] Incremental `/api/logs` endpoint
- [x] Isolated state snapshot

Additional endpoints may be introduced as future integrations require them.

---

## Web Dashboard ✅ / 🚧

Implemented:

- [x] General dashboard
- [x] System view
- [x] SvxLink view
- [x] EchoLink view
- [x] Reflector view
- [x] RAW LOG view
- [x] Configuration view
- [x] `/monitor` operational view
- [x] Responsive layout
- [x] Desktop support
- [x] Mobile support
- [x] Dynamic updates
- [x] Status indicators
- [x] Multilingual support

Evolving:

- [ ] Further performance optimizations
- [ ] Additional responsive refinements
- [ ] Integration of future Reflector features

---

## Authentication and Node Control ✅ / 🚧

Implemented:

- [x] Sysop authentication
- [x] Co-Sysop authentication
- [x] Web sessions
- [x] CSRF protection
- [x] `SECRET_KEY` stored outside the repository
- [x] Private credentials separated from the repository
- [x] Operational controls protected by authentication

To be completed as part of provisioning:

- [ ] Automatic creation of private files
- [ ] Automatic `SECRET_KEY` generation
- [ ] Automatic permission configuration
- [ ] Service user configuration

---

# Next Development Areas

## Reflector / Application Clients 🚧

Current priority:

- [ ] Complete analysis of real SvxReflector events
- [ ] Node / user separation
- [ ] LATRY user support
- [ ] Legacy testing
- [ ] Definition of the canonical data model
- [ ] Possible integration into `/monitor` only after validation

---

## Notifications

Planned:

- [ ] Telegram
- [ ] E-mail
- [ ] Configurable alerts
- [ ] Definition of notification events
- [ ] Priority levels
- [ ] Protection against repetitive notifications

MQTT remains a possible future extension.

---

## HTTPS and Security

Planned implementation and automation:

- [ ] Apache HTTPS templates
- [ ] Reverse proxy to Guardian
- [ ] Private key and CSR generation
- [ ] DNS verification management
- [ ] Certificate chain installation
- [ ] VirtualHost configuration
- [ ] Controlled Apache reload
- [ ] Portable and documented procedure

---

## Installer and Provisioning

The goal is to provide a reproducible installation procedure for modern Raspberry Pi / Linux systems.

Future provisioning should be able to manage:

- [ ] SvxLink installation
- [ ] SVX Guardian installation
- [ ] Python virtual environment
- [ ] Dependencies
- [ ] SvxLink configuration
- [ ] EchoLink
- [ ] Reflector
- [ ] EchoLink event override
- [ ] systemd services
- [ ] Sysop / Co-Sysop authentication
- [ ] Private files and permissions
- [ ] Apache
- [ ] HTTPS
- [ ] Certificates
- [ ] Initial node configuration
- [ ] Controlled updates

The objective is not simply to install Guardian, but to make the deployment of a **complete SvxLink node** reproducible.

---

# Towards v1.0.0

The first stable release should achieve at least the following goals:

- [ ] Complete and stable monitoring
- [ ] Stable and responsive dashboard
- [ ] Stable EchoLink monitoring
- [ ] Stable Reflector monitoring
- [ ] Stable RAW LOG
- [ ] Stable authentication
- [ ] Documented API
- [ ] Complete internationalization
- [ ] Bilingual documentation
- [ ] Reliable installer
- [ ] Reproducible provisioning
- [ ] Documented and automatable HTTPS configuration
- [ ] Sufficient tests for critical functionality
- [ ] Documented update procedure
- [ ] Community-ready release

---

# Development Method

Changes are developed and validated progressively:

```text
Design
  ↓
LAB
  ↓
Automated tests
  ↓
Functional testing
  ↓
Signed Git commit
  ↓
GitHub
  ↓
Legacy
  ↓
Real-traffic validation
```

This approach keeps development separate from the operational node and allows changes to be validated before they are introduced into production.

---

# Long-Term Vision

SVX Guardian aims to become a reference platform for monitoring and managing SvxLink nodes.

The final vision is to start from a modern Linux / Raspberry Pi OS system and obtain, through a guided and reproducible procedure:

```text
SvxLink
   +
SVX Guardian
   +
EchoLink
   +
Reflector
   +
Dashboard
   +
Real-time LOG
   +
Authentication
   +
HTTPS
   +
Notifications
```

while keeping the system modular, documented, upgradeable and completely open source.

---

**73!**
