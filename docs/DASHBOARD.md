# SVX Guardian Dashboard Specification

## Overview

The SVX Guardian dashboard provides a real-time overview of the health of a SvxLink radio node.

The interface is designed to be:

- Responsive
- Multi-language
- Lightweight
- Mobile friendly
- Readable at a glance

---

# Dashboard Layout

## Header

Always visible.

Contains:

- SVX Guardian logo
- Callsign
- Language selector
- Theme selector (Light / Dark)
- Settings button

---

## Global Health

Large status card.

Possible states:

- 🟢 Healthy
- 🟡 Warning
- 🔴 Critical

Displays:

- Health status
- Health reason
- Last update

---

## Node Information

Displays:

- Hostname
- Callsign
- Raspberry Pi model
- Operating system
- Uptime

---

## System Status

Displays:

- CPU Temperature
- CPU Usage
- RAM Usage
- Disk Usage
- CPU Frequency
- System Load

---

## Radio Services

Displays:

### SvxLink

- Running
- Version
- Service uptime

### EchoLink

- Registration status
- Callsign
- Connection status

### Reflector

- Connected
- Reflector name
- Talk Group
- Connection duration

---

## Events

Latest events in reverse chronological order.

Examples:

- SvxLink started
- EchoLink connected
- Reflector disconnected
- CPU temperature warning

---

## Charts

Historical charts.

Initially:

- CPU Temperature
- CPU Usage
- RAM Usage

Future versions:

- Network traffic
- Disk usage
- GPIO status

---

## Footer

Displays:

- SVX Guardian version
- Build date
- Git commit
- Copyright

---

# Refresh Policy

Dashboard refresh:

Every second.

The page must never reload.

Updates are performed through REST API.

---

# Themes

Supported themes:

- Light
- Dark

Theme selection is stored in browser preferences.

---

# Languages

Supported languages:

- English
- Italian
- French
- Spanish
- German
- Russian

Future:

- Portuguese
- Polish

---

# Design Principles

The dashboard should immediately answer:

- Is the node operational?
- Is SvxLink running?
- Is EchoLink available?
- Is the Reflector connected?
- Is the Raspberry Pi healthy?

The interface must avoid unnecessary information.

Important information should always be visible.

Details should be accessible with a single click.
