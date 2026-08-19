# SVX Guardian Dashboard Specification

## 1. Purpose

The SVX Guardian dashboard provides a web view of the operational state
of a SvxLink node.

The interface is designed to be:

- readable at a glance;
- responsive;
- usable on desktop and mobile devices;
- multilingual;
- lightweight;
- consistent with the canonical state maintained by Guardian.

The dashboard must not present features as available when they have not
yet been implemented and tested.

---

## 2. General Structure

The web interface uses Flask, Jinja templates, Bootstrap 5,
Font Awesome, and SVX Guardian stylesheets.

Normal technical pages share:

- a global header;
- responsive content;
- navigation sidebar;
- translation system;
- Light and Dark theme support.

The main pages are:

```text
/                  General dashboard
/monitor           Operational view
/system            System status
/svxlink           SvxLink status and configuration
/echolink          EchoLink status
/reflector         Reflector status
/logs              SvxLink RAW LOG
/configuration     Configuration and control
```

---

## 3. Themes

Two themes are supported:

- Light;
- Dark.

The preference is stored in the browser using:

```text
svxguardian-theme
```

If no preference has been saved, the interface uses the browser/system
preference when available.

The theme is applied as early as possible during page loading to avoid
an initial flash of the wrong theme.

The `/monitor` view uses the same Light/Dark states with a presentation
specifically optimized for operational use.

---

## 4. Multilingual Interface

Interface strings use the Translation Manager.

The internal technical state remains canonical and
language-independent.

Translation is applied only at the presentation layer.

International technical terms may remain unchanged when appropriate.

The languages actually available must be determined from the
localization files present in the project and must not be declared in
this document from a theoretical list.

---

## 5. General Dashboard

The `/` page provides the main node summary.

### General Health

A banner highlights the overall state:

- `HEALTHY`;
- `WARNING`;
- `CRITICAL`;
- unknown state.

The reason associated with the health state is also displayed.

### Node Identity

The dashboard shows, in compact form:

- callsign;
- locator;
- QTH.

### System Summary

A card linked to `/system` shows:

- CPU usage;
- CPU temperature;
- RAM usage;
- disk usage.

### Radio Services

Three cards provide direct access to:

- SvxLink;
- EchoLink;
- Reflector.

Each card displays the current state of the corresponding service using
badges consistent with state severity.

The general dashboard is a summary view. Detailed information belongs
on the dedicated pages.

---

## 6. Operational View `/monitor`

The `/monitor` page is a dedicated operational view designed especially
for quick consultation, including on smartphones.

It does not replicate the full technical dashboard.

It mainly displays EchoLink status and station activity.

The view includes:

- SVX Guardian identity;
- node callsign;
- EchoLink operational status;
- connection count;
- last update time;
- station list;
- station callsign;
- station name when available;
- station state;
- connection duration.

Stations use distinct visual states:

- connected;
- unstable connection;
- transmitting.

The transmitting station receives priority visual emphasis.

The station list may use a more compact representation as the number
of stations increases.

The view updates local timers every second and retrieves new
operational state every 2 seconds.

The `/monitor` model must remain stable. Reflector application-client
users such as LATRY must not be added to this view until the related
state model has been defined and validated on the `/reflector` page.

---

## 7. System Page

The `/system` page displays Linux/Raspberry Pi system status.

It includes:

- hostname;
- uptime;
- CPU temperature;
- CPU usage;
- RAM usage;
- disk usage.

CPU, RAM, and disk are accompanied by progress bars.

The current visual thresholds are:

```text
< 75%       green
75% - 89%   warning
>= 90%      critical
```

CPU temperature is displayed when available.

---

## 8. SvxLink Page

The `/svxlink` page combines dynamic service state and static
information obtained from node configuration.

### Service State

It displays:

- SvxLink status;
- PID;
- service uptime.

### Node Identity

When available, it displays:

- callsign;
- QTH;
- locator;
- Sysop;
- node class;
- geographic position.

### Configuration

The page also exposes information such as:

- SvxLink version;
- detected configuration file;
- `node_info.json` file;
- modules;
- logics;
- RX configuration;
- TX configuration;
- additional technical parameters obtained from configuration.

The page must display `NOT_AVAILABLE` when data is unavailable rather
than inventing values.

---

## 9. EchoLink Page

The `/echolink` page is the dedicated technical EchoLink view.

### General State

It displays:

- EchoLink status;
- connection count;
- node callsign;
- presence of the EchoLink module;
- last error when present.

The main states are represented with distinct badges, including:

- `ONLINE`;
- `OFFLINE`;
- `DNS_ERROR`;
- `ERROR`;
- unknown state.

### Connected Stations

The page displays currently connected EchoLink stations.

### Recent Connections

A section is dedicated to recent events/connections.

For each connection it may display:

- callsign;
- station name;
- connection date/time;
- duration;
- status;
- disconnection date/time.

Connections identified as unstable are explicitly highlighted.

The page dynamically updates state through `/api/state` every
2 seconds without requiring a full page reload.

---

## 10. Reflector Page

The `/reflector` page displays the technical state of the Reflector
connection.

It includes:

- status;
- host;
- port;
- connection count;
- talkgroup;
- encryption state;
- reason for the last disconnection;
- last error;
- connected SvxLink nodes.

Presentation states include:

- `CONNECTING`;
- `CONNECTED`;
- `RECONNECTING`;
- `DISCONNECTED`;
- `AUTH_ERROR`;
- `TIMEOUT`;
- `ERROR`;
- unknown state.

The page dynamically updates state through `/api/state` every
2 seconds.

### Nodes and Application Clients

`reflector_connected_nodes` represents connected SvxLink nodes.

Users coming from application clients such as LATRY are a different
concept and must not be artificially inserted into this list.

The definitive model for Reflector users/clients remains under
analysis and must be validated with real traffic before being extended
to other views.

---

## 11. RAW LOG

The `/logs` page displays the SvxLink operational log as a RAW source.

The page must not reinterpret, classify, or semantically modify logfile
lines.

The reader is incremental and uses `/api/logs`.

Polling occurs every 2 seconds.

Browser-local controls are available for:

- Pause/Play;
- Auto-scroll;
- Clear.

`Clear` only clears the browser display and does not modify the original
logfile.

The view maintains a read cursor and limits the number of lines retained
in the browser to prevent unbounded page growth.

RAW LOG polling must not execute the complete `guardian.run()` cycle.

---

## 12. Configuration and Control

The `/configuration` page separates configuration viewing from
operations that modify node state.

Public monitoring must remain available even when authentication is not
configured.

Control operations are restricted to authorized Sysop/Co-Sysop users.

Protected operations use CSRF tokens.

The currently available operational control includes restarting the
SvxLink service.

Future controls that may be visible but disabled in the interface must
not be documented as implemented features.

---

## 13. Data Refresh

There is no general rule that the entire dashboard refreshes every
second.

Refresh policies depend on the page.

Currently:

```text
/monitor       state: 2 s, local timers: 1 s
/echolink      state: 2 s
/reflector     state: 2 s
/logs          new lines: 2 s
```

Pages that perform dynamic updates use the APIs without fully reloading
the page.

Technical pages that are static after loading must not introduce
polling without a real need.

---

## 14. Responsive Design

The interface must remain usable on both desktop and mobile.

The technical dashboard uses Bootstrap's responsive grid and
Guardian-specific styles.

The `/monitor` view uses a dedicated layout with constrained width,
large elements, and priority operational information.

Responsive changes must be tested in both conditions and must not
unnecessarily alter Guardian's established visual style.

---

## 15. Features Not Yet Implemented

The following must not be described as current dashboard features until
they have been developed and tested:

- historical charts;
- general persistent history;
- advanced statistics;
- general system event panel;
- automatic recovery controls;
- backup functions;
- new Reflector views based on application clients that have not yet
  been modeled.

Documentation must be updated when any of these features actually
becomes available.

---

## 16. Design Principles

The dashboard should make it possible to understand quickly:

- whether the node is operational;
- whether SvxLink is running;
- whether EchoLink is available;
- whether the Reflector is connected;
- whether the Linux/Raspberry Pi system is healthy;
- which EchoLink stations are currently connected;
- whether an EchoLink connection is unstable or transmitting.

Summary information belongs on the general dashboard.

Details belong on dedicated pages.

The operational view must prioritize readability and immediacy.

The RAW LOG must remain RAW.

Multilingual presentation must not change the meaning of internal
state.
