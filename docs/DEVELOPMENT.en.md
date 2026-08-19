# SVX Guardian Development

## 1. Purpose

This document describes the SVX Guardian development method, the
environments used for validation, and the project's main technical
milestones.

It does not replace:

- `ARCHITECTURE.md`, which describes the architecture;
- `CONTRIBUTING.md`, which defines contribution rules;
- `ROADMAP.md`, which describes future work;
- `DASHBOARD.md`, which documents the web interface.

Features reported as complete must correspond to implementations that
have actually been developed and tested.

---

## 2. Development Environments

SVX Guardian uses two separate environments.

### LAB

The LAB is the primary environment for:

- development;
- file modification;
- automated tests;
- functional tests;
- documentation verification;
- commit preparation.

### Legacy

The Legacy environment is a real node carrying radio traffic.

It is used only after LAB validation and publication of the commit on
GitHub.

It is used to verify:

- compatibility with a real SvxLink installation;
- behavior with legacy configurations;
- real EchoLink and Reflector events;
- actual radio traffic;
- regressions that cannot be fully reproduced in the LAB.

The Legacy node is not the primary development environment.

---

## 3. Operational Flow

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

The actual current version of a file must be read before modifying it.

When a change is provided manually for copy and paste, prefer a complete
file ready to copy when this reduces the risk of errors.

---

## 4. Repository and Commits

The main branch is:

```text
main
```

Commits intended for the production repository must be signed.

On the Legacy node, updates must preserve a linear history through:

```bash
git merge --ff-only
```

Do not use `sudo` to modify files inside the repository.

Repository state must be checked after every push and after every Legacy
update.

---

## 5. Consolidated Technical State

### Data Model

Static node configuration and dynamic runtime state are kept separate.

`NodeInfo` represents static information obtained from SvxLink
configuration and `node_info.json`.

`NodeState` represents the current operational state.

This separation prevents configuration from being confused with
runtime state.

### Monitors

The Guardian Engine currently uses:

- `SystemMonitor`;
- `SvxLinkMonitor`;
- `EchoLinkMonitor`;
- `ReflectorMonitor`.

Each monitor updates the parts of `NodeState` for which it is
responsible.

### SvxLink Configuration

Guardian detects and uses information from:

```text
/etc/svxlink/svxlink.conf
/etc/svxlink/node_info.json
/var/log/svxlink
```

The legacy form:

```text
O_FILE=/etc/svxlink/node_info.json
```

inside `[ReflectorLogic]` is also supported.

### Dashboard and API

The following pages are operational:

```text
/
/monitor
/system
/svxlink
/echolink
/reflector
/logs
/configuration
```

together with:

```text
/api/state
/api/logs
```

### Multilingual Support

Internal state uses canonical technical values independent of language.

Translation is applied only at presentation layers.

### Authentication

Sysop/Co-Sysop authentication uses private configuration outside the
repository.

The current path is:

```text
/etc/svxguardian
```

The persistent Flask session key is:

```text
/etc/svxguardian/secret.key
```

Protected operations use CSRF tokens.

### Node Control

Restarting the SvxLink service is implemented for authorized users.

Other controls that may appear disabled in the interface must not be
considered implemented.

---

## 6. RAW LOG

The RAW LOG was implemented as a function separate from the normal
monitoring cycle.

Consolidated features:

- incremental reading;
- in-memory buffer;
- truncation and rotation handling;
- API separated from `guardian.run()`;
- LIVE state;
- Pause/Play;
- retrieval of lines produced during Pause;
- Auto-scroll ON/OFF;
- Clear limited to the browser display;
- line counter;
- maximum of 500 displayed lines;
- source `/var/log/svxlink`.

Binding decision:

**the RAW LOG remains RAW.**

Guardian must not reinterpret or classify lines displayed on `/logs`.

RAW LOG polling must not trigger execution of the complete monitor set.

---

## 7. EchoLink

The EchoLink monitor currently handles:

- directory status;
- connected stations;
- station names;
- connection duration;
- transmission state;
- recent connections;
- detection of unstable connections.

Recent history was optimized to avoid complete and repeated logfile
scans on every refresh.

Reference commit:

```text
09394b44fc1e07236e629ccbe38b05ef65783db2
Optimize EchoLink recent connection history
```

The EchoLink page and mobile operational view were adapted to display
callsign, name, timing, and connection state clearly.

---

## 8. Reflector and LATRY

The Reflector monitor currently handles:

- connection state;
- host;
- port;
- talkgroup;
- encryption;
- connected nodes;
- errors;
- reason for the last disconnection.

Reflector application-client handling is still under analysis.

Real traffic has shown events such as:

```text
ReflectorLogic: Node joined:
IU5HJU

ReflectorLogic: Talker start on TG #2225: IU5HJU
```

while `/reflector` may display only nodes reconstructed through the
current `reflector_connected_nodes` logic.

Consolidated decision:

- do not force LATRY users into `reflector_connected_nodes`;
- keep SvxLink nodes and application users/clients distinct;
- validate the new model first on `/reflector`;
- do not modify `/monitor` until the LATRY/Reflector model is stable and
  validated with real traffic.

Events to analyze on the Legacy node include:

```text
Node joined
Node left
Connected nodes
Talker start
Talker stop
```

---

## 9. Legacy Compatibility

Compatibility with existing SvxLink installations is a project
requirement.

Support for the legacy `node_info.json` configuration has been added.

Reference commit:

```text
e056000b935b01fbe693e320fc0cc9afa45e2971
Support legacy SvxLink node info configuration
```

Guardian must not be designed exclusively around the LAB node
configuration.

---

## 10. HTTPS and Private Configuration

HTTPS access through an Apache reverse proxy is part of the planned
complete-node infrastructure.

The procedure tested with No-IP must be preserved and made suitable for
automation.

It includes:

- key and CSR generation;
- CSR requirements;
- DNS TXT verification;
- PEM chain installation;
- Apache VirtualHost configuration;
- reload;
- secrets outside the repository.

These procedures must not be described as completed automatic
provisioning until the corresponding installer is implemented.

---

## 11. EchoLink Override

Operational EchoLink monitoring uses a local SvxLink integration based
on:

```text
/usr/share/svxlink/events.d/local/EchoLink.tcl
```

Guardian requires the events:

```text
SVXGUARDIAN_ECHOLINK_RX_START
SVXGUARDIAN_ECHOLINK_RX_STOP
```

Future provisioning must manage:

- backup of an existing file;
- override installation;
- ownership;
- permissions;
- compatibility with the installed SvxLink version.

---

## 12. Development Timeline

### August 4, 2026

Main activities:

- refactoring of configuration reading;
- introduction of separation between static configuration and
  operational state;
- integration of node data;
- extension of Reflector information;
- expansion of `/api/state`;
- dashboard updates using real node data.

Important design decision:

SVX Guardian must support heterogeneous installations and must not
assume that LAB topology is the standard model.

### August 5, 2026

Main activities:

- consolidation of internationalization;
- use of the translation system for visible strings;
- synchronization of localization files;
- introduction of `tools/check_i18n.py`;
- checking JSON consistency and translation keys;
- consolidation of repository and working rules.

From this point the project follows the principle:

**canonical internal state, translation at the presentation layer.**

### August 18, 2026

Several aspects of the operational view and RAW LOG were consolidated.

Verified commits:

```text
7115ab5 Refine operational log controls
4d64c04 Refine raw log mobile controls
```

The RAW LOG was also tested on the Legacy node and found to be smooth.

### August 19, 2026

The first bilingual documentation checkpoint was completed.

Signed commit:

```text
b2b55a2 Update bilingual project documentation
```

The LAB repository was aligned with `origin/main`.

Revision and bilingual creation of the remaining technical documents
were then started.

---

## 13. Tests

The latest test state reported in the operational checkpoint was:

```text
22 passed
```

This value represents a verified state at that checkpoint and must not
be treated as a permanent number.

The number of tests may change as the project evolves.

The rule remains:

```bash
pytest -q
```

must be run before commits required by the development workflow.

---

## 14. Bilingual Documentation

The planned documentation structure is:

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

Technical detail belongs in the documents under `docs/`.

---

## 15. Principles to Preserve

The following decisions must not be lost during development:

1. the RAW LOG remains RAW;
2. LAB first, Legacy second;
3. production commits are signed;
4. internal state is canonical and language-independent;
5. secrets stay outside Git;
6. avoid complete logfile scans during frequent refreshes;
7. mobile is as important as desktop;
8. always read the actual file before modifying it;
9. do not declare planned work as complete;
10. do not invent release numbers;
11. SvxLink nodes and Reflector application clients are distinct
    concepts;
12. `/monitor` remains frozen with respect to LATRY until the model is
    stable and validated.
