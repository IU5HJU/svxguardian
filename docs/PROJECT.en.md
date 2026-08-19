# SVX Guardian

## Project Handbook

## 1. Vision

SVX Guardian is an open-source platform for monitoring, supervising, and
operationally controlling SvxLink-based radio nodes.

Its goal is to provide the Sysop with a modern, simple, and reliable
view of node status while keeping acquisition, monitoring, internal
state, presentation, and control functions separate.

The project is intended for real and heterogeneous installations and
must not depend on the particular configuration used during
development.

SVX Guardian must grow incrementally: a feature is considered available
only when it has actually been implemented, verified, and documented.

---

## 2. Objectives

The main objectives are:

- monitor Linux/Raspberry Pi system status;
- monitor the SvxLink service;
- monitor EchoLink;
- monitor the Reflector connection;
- provide a responsive web dashboard;
- provide an operational view suitable for mobile use;
- expose REST APIs for state and supported functions;
- preserve and display the SvxLink RAW LOG efficiently;
- support authentication and operational controls restricted to the
  Sysop;
- maintain a multilingual interface;
- support different SvxLink installations;
- make installation and provisioning as guided and repeatable as
  possible in the future.

Future functions such as notifications, persistent history, statistics,
backup, and automatic recovery remain project goals but must not be
presented as already implemented.

---

## 3. Principles

SVX Guardian must remain:

- reliable;
- easy to understand;
- modular;
- readable;
- verifiable;
- portable;
- documented;
- open source.

A simple and robust solution is preferable to an unnecessarily complex
one.

Each component must have a clearly identifiable responsibility.

Internal state must use canonical technical values independent of the
interface language.

Translation belongs to the presentation layers.

---

## 4. Compatibility

SVX Guardian is designed for heterogeneous SvxLink installations.

The project must not assume:

- a specific Raspberry Pi model;
- a single hardware platform;
- a single radio topology;
- a necessarily local Reflector;
- a single configuration-file variant;
- that the development node represents the standard case.

Target environments may include Linux systems on Raspberry Pi and other
platforms compatible with SvxLink.

Topologies may include, depending on the installation:

- simplex nodes;
- repeaters;
- hotspots;
- systems with remote Reflectors;
- systems with local Reflectors;
- mixed or distributed configurations.

Already supported legacy compatibility must be preserved unless an
explicit and documented decision changes it.

---

## 5. LAB and Legacy Environments

Development uses two separate environments.

### LAB

The LAB is the primary environment for:

- development;
- file modification;
- automated tests;
- functional tests;
- commit preparation.

Its configuration may include SvxLink and SvxReflector on the same
machine.

This topology is a test case and is not the standard project model.

### Legacy

The Legacy environment is a real node carrying radio traffic.

It is used after LAB validation to verify:

- behavior on a real installation;
- legacy compatibility;
- real EchoLink traffic;
- real Reflector traffic;
- regressions that cannot be fully reproduced in the LAB.

The Legacy node must not be used as the primary development
environment.

---

## 6. Architecture

The operational architecture revolves around the Guardian Engine and
shared node state.

Simplified view:

```text
                    Guardian Engine
                           │
                ┌──────────┼──────────┐
                │          │          │
            Configuration NodeState Node Info
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
 SystemMonitor       SvxLinkMonitor      EchoLinkMonitor
                                               │
                                        ReflectorMonitor
                           │
                           ▼
                    Canonical state
                           │
                 ┌─────────┴─────────┐
                 │                   │
            Web Dashboard         REST API
```

The monitors do not form a chain.

Each monitor updates only the parts of `NodeState` for which it is
responsible.

The complete technical description is maintained in
`ARCHITECTURE.en.md`.

---

## 7. Data Model

SVX Guardian keeps two concepts distinct.

### NodeInfo

Represents static node and configuration information.

It may include:

- callsign;
- QTH;
- locator;
- Sysop;
- RX/TX configuration;
- modules;
- logics;
- EchoLink configuration;
- Reflector configuration;
- SvxLink version;
- detected file paths.

### NodeState

Represents the current dynamic state.

It includes information related to:

- operating system;
- SvxLink;
- EchoLink;
- Reflector.

This separation prevents node configuration from being confused with
its operational state.

---

## 8. Implemented Components

The current state includes:

- Guardian Engine;
- `SystemMonitor`;
- `SvxLinkMonitor`;
- `EchoLinkMonitor`;
- `ReflectorMonitor`;
- `NodeState`;
- SvxLink configuration reading;
- `node_info.json` reading;
- compatibility with supported legacy configurations;
- static node information;
- web dashboard;
- `/monitor` operational view;
- dedicated technical pages;
- `/api/state`;
- incremental `/api/logs`;
- RAW LOG;
- multilingual support;
- Translation Manager;
- Sysop/Co-Sysop authentication;
- CSRF protection for restricted operations;
- controlled SvxLink service restart.

Technical documentation for individual components belongs in the
dedicated documents and source code.

---

## 9. Dashboard

The web interface includes:

```text
/                  General dashboard
/monitor           Operational view
/system            System
/svxlink           SvxLink
/echolink          EchoLink
/reflector         Reflector
/logs              RAW LOG
/configuration     Configuration and control
```

The interface supports:

- responsive design;
- desktop and mobile use;
- Light and Dark themes;
- translation of user-facing strings.

The complete specification is maintained in `DASHBOARD.en.md`.

---

## 10. EchoLink

EchoLink monitoring includes operational state and information about
connected stations.

It handles, among other data:

- directory state;
- connected stations;
- names;
- connection timing;
- transmission state;
- recent connections;
- unstable connections.

Operational monitoring also uses a local SvxLink integration based on:

```text
/usr/share/svxlink/events.d/local/EchoLink.tcl
```

Guardian expects the events:

```text
SVXGUARDIAN_ECHOLINK_RX_START
SVXGUARDIAN_ECHOLINK_RX_STOP
```

Future complete installation must manage this dependency automatically
without placing private configuration in the repository.

---

## 11. Reflector

The Reflector monitor handles:

- connection state;
- host;
- port;
- talkgroup;
- encryption;
- connected nodes;
- errors;
- reason for the last disconnection.

Connected SvxLink nodes and application users/clients are distinct
concepts.

Users coming from clients such as LATRY must not be artificially
inserted into `reflector_connected_nodes`.

The Reflector user/client model must be defined and validated with real
traffic on `/reflector` before being extended to `/monitor`.

---

## 12. RAW LOG

The `/logs` page provides access to the SvxLink operational log.

Project decision:

**the RAW LOG remains RAW.**

Guardian must not reinterpret or classify lines shown in this view.

Reading is incremental and separate from the normal `guardian.run()`
cycle.

The page provides local controls for:

- Pause/Play;
- Auto-scroll;
- Clear.

`Clear` does not modify the original logfile.

This architecture avoids complete and repeated logfile scans during
frequent polling.

---

## 13. Security and Private Configuration

Public monitoring must be able to operate even when authentication is
not configured.

Control functions are instead restricted to authorized Sysop/Co-Sysop
users.

Secrets, passwords, keys, and credentials must not be stored in the Git
repository.

The current private configuration uses:

```text
/etc/svxguardian
```

The persistent key used for Flask sessions is:

```text
/etc/svxguardian/secret.key
```

Protected operations use CSRF tokens.

---

## 14. HTTPS

HTTPS access through an Apache reverse proxy is part of the
infrastructure planned for a complete installation.

The procedure tested with No-IP includes:

- key and CSR generation;
- CSR requirements;
- DNS TXT verification;
- PEM chain installation;
- Apache VirtualHost;
- configuration reload.

This procedure must be preserved and made automatable in the future
installer.

It must not be described as completed automatic provisioning.

---

## 15. Development Method

The reference workflow is:

```text
Design → LAB → pytest → functional test → GPG commit → GitHub
→ Legacy (merge --ff-only) → pytest → restart → real traffic
```

Before every commit, run at least:

```bash
git diff --check
pytest -q
git status --short
```

Commits intended for the production repository must be signed.

The actual current version of a file must be read before modifying it.

Complete rules are defined in `CONTRIBUTING.en.md` and
`DEVELOPMENT.en.md`.

---

## 16. Documentation

Documentation is an integral part of the project.

The planned bilingual structure includes:

```text
README.md
README.en.md
docs/ROADMAP.md
docs/ROADMAP.en.md
docs/ARCHITECTURE.md
docs/ARCHITECTURE.en.md
docs/CONTRIBUTING.md
docs/CONTRIBUTING.en.md
docs/DASHBOARD.md
docs/DASHBOARD.en.md
docs/DEVELOPMENT.md
docs/DEVELOPMENT.en.md
docs/PROJECT.md
docs/PROJECT.en.md
```

The README should remain concise.

Technical detail belongs in documents under `docs/`.

Release or milestone numbers that have not been formally defined in the
repository must not be invented.

---

## 17. Future Features

Future direction includes, among other items:

- notifications;
- persistent history;
- advanced statistics;
- backup;
- automatic recovery;
- dedicated Reflector application-user/client model;
- complete node provisioning;
- guided installation;
- HTTPS automation;
- automatic configuration of Guardian dependencies;
- further performance optimizations.

These items represent goals and not currently available features.

Detailed planning belongs in `ROADMAP.en.md`.

---

## 18. Long-Term Goal

SVX Guardian aims to become a reliable and easily installable open-source
platform for monitoring SvxLink nodes.

The project should be usable by amateur radio operators with different
installations without requiring their systems to replicate the
development environment.

Code quality, verifiability, compatibility, and documentation are
considered integral parts of the product.
