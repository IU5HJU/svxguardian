# SVX Guardian Architecture

## Purpose

SVX Guardian is an open-source monitoring platform for SvxLink nodes
running on Raspberry Pi/Linux.

The architecture is designed to keep the following concerns separate:

- state acquisition and monitoring;
- representation of the current state;
- node configuration;
- web interface;
- REST API;
- authentication and operational control;
- SvxLink operational log reading;
- interface localization.

Future features such as notifications, persistent history,
advanced statistics, backup, and automatic recovery mechanisms
must not be considered part of the implemented architecture until
they have actually been developed and tested.

---

## General Architecture

```text
                    SVX Guardian
                         │
                  Guardian Engine
                         │
          ┌──────────────┼──────────────┐
          │              │              │
      Configuration   NodeState      Node Info
                         │
        ┌────────────────┼────────────────┐
        │                │                │
 SystemMonitor     SvxLinkMonitor   EchoLinkMonitor
                                         │
                                  ReflectorMonitor
                         │
                         ▼
                  Canonical state
                         │
             ┌───────────┴───────────┐
             │                       │
        Web Dashboard             REST API
             │
       Multilingual
       presentation
```

The diagram represents a simplified logical view.

The monitors do not form a chain: each monitor updates the parts of
`NodeState` for which it is responsible.

---

## Guardian Engine

The Guardian Engine coordinates the monitoring cycle.

Monitors are registered with Guardian and operate on the shared node
state.

The monitors currently in use are:

- `SystemMonitor`;
- `SvxLinkMonitor`;
- `EchoLinkMonitor`;
- `ReflectorMonitor`.

Each monitor implements the common interface defined by
`BaseMonitor`.

The fundamental contract is:

```python
check(state: NodeState) -> None
```

The monitor receives the current state and updates only the
information for which it is responsible.

---

## NodeState

`NodeState` represents the current dynamic state of the node.

It contains information related to:

### Operating system

- hostname;
- CPU temperature;
- CPU usage;
- RAM usage;
- disk usage;
- uptime.

### SvxLink

- service status;
- PID;
- service uptime.

### EchoLink

- directory status;
- last error;
- connected stations;
- station names;
- connection start time;
- stations with unstable connections;
- connection count;
- transmission state;
- transmitting station;
- recent connections.

### Reflector

- connection status;
- host;
- port;
- talkgroup;
- encryption status;
- connected nodes;
- connection count;
- last error;
- reason for the last disconnection.

The internal state uses canonical technical values independent of the
interface language.

Translation is applied only at the presentation layer.

---

## Static Node Information

Static information obtained from the SvxLink configuration and the
`node_info.json` file is kept separate from the dynamic state.

It includes, among other information:

- callsign;
- description;
- Sysop;
- QTH and locator;
- RX/TX configuration;
- EchoLink configuration;
- Reflector configuration;
- logics and modules;
- SvxLink version;
- detected configuration file paths.

This separation prevents node configuration from being confused with
its current operational state.

---

## Web Application

The web application is built with Flask.

The main operational pages are:

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

Before rendering the normal monitoring pages, the Guardian cycle is
executed and an isolated copy of the current state is created.

This prevents templates from working directly on the shared dynamic
state object.

---

## REST API

SVX Guardian currently exposes:

```text
/api/state
/api/logs
```

### `/api/state`

Runs the monitoring cycle and returns a JSON snapshot of the current
state together with node information.

### `/api/logs`

Incrementally provides new lines from the SvxLink logfile.

The endpoint uses a client cursor and does not execute
`guardian.run()`.

This separation is intentional: frequent RAW LOG polling must not
continuously trigger the complete monitoring cycle.

---

## RAW LOG

The RAW LOG uses a dedicated incremental reader.

The SvxLink operational log remains a RAW source:

- Guardian must not reinterpret its contents on the RAW LOG page;
- log refresh must not execute the complete Guardian cycle;
- the browser maintains its own Pause, Auto-scroll, and Clear behavior;
- Clear never modifies the original logfile.

Incremental reading avoids complete and repeated scans of the logfile
during refresh operations.

---

## Authentication and Operational Control

Public monitoring must continue to work even when the authentication
infrastructure is not configured.

Control operations are instead restricted to authorized Sysop/Co-Sysop
users.

Private configuration is kept outside the repository.

Expected path:

```text
/etc/svxguardian
```

The persistent key used to sign Flask sessions is:

```text
/etc/svxguardian/secret.key
```

If the key or authentication file is unavailable, Guardian does not
automatically generate temporary credentials: authentication remains
unavailable.

Protected operations also use CSRF tokens.

The current control layer includes restarting the SvxLink service
through `NodeControl`.

---

## Multilingual Support

Translations are handled at the presentation layer.

Monitors and `NodeState` use canonical technical values.

The selected language affects the dashboard and user-facing text, not
the meaning of the internal state.

Localization files are kept separate from application code.

---

## Bootstrap

`BootstrapEngine` manages the initial startup sequence.

Currently it:

1. initializes the configuration;
2. configures logging;
3. writes the startup banner to the log.

The bootstrap must remain separate from the operational monitoring
cycle.

---

## Design Principles

### Separation of Responsibilities

Each component must have a clearly identifiable responsibility.

### Independent Monitors

Monitors must not depend directly on one another.

State communication takes place through `NodeState`.

### Canonical State

The internal state must not depend on the UI language.

### Separate Presentation Layer

Translation and formatting belong to the presentation layers.

### Preserved Operational Log

The RAW LOG must remain RAW and must not be transformed into an
interpreted representation.

### Private Configuration Outside the Repository

Credentials, keys, and other secrets must not be stored in the Git
repository.

### Performance

Frequently executed functions must not cause complete and repeated
logfile scans when incremental reading can be used.

### Compatibility

Guardian must be able to operate with real SvxLink installations,
including explicitly supported legacy configurations.

---

## Reflector and Application Clients

Reflector management must keep different concepts separate:

```text
Connected SvxLink nodes
Connected application users/clients
```

Users coming from application clients such as LATRY must not be
artificially inserted into `reflector_connected_nodes`.

The definitive model for Reflector users/clients is still under
analysis and must be validated with real traffic before being extended
to the `/monitor` view.

---

## Future Features

The following features are planned, but must not be considered
implemented until their development and testing are complete:

- notifications;
- persistent history;
- advanced statistics;
- backup;
- automatic recovery;
- complete installation/provisioning;
- HTTPS configuration automation;
- further performance optimizations.

---

## Project Philosophy

SVX Guardian must remain:

- reliable;
- easy to understand;
- modular;
- portable;
- verifiable;
- open source;
- suitable for real-world use on SvxLink amateur radio nodes.
