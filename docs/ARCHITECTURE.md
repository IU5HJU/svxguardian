# SVX Guardian

## Project Goal

SVX Guardian is an intelligent monitoring and self-healing system for SvxLink nodes.

The objective is to continuously monitor every component of a SvxLink installation and automatically detect failures, notify the system administrator and, whenever possible, recover from faults without human intervention.

---

# Main Features

- SvxLink monitoring
- EchoLink monitoring
- SvxReflector monitoring
- Raspberry Pi health monitoring
- Automatic recovery
- Web dashboard
- Telegram notifications
- Historical database
- Statistics
- Backup support

---

# Software Architecture

```
                Guardian Engine
                       │
     ┌─────────────────┼──────────────────┐
     │                 │                  │
 SystemMonitor   SvxLinkMonitor    ReflectorMonitor
     │                 │                  │
     └─────────────────┼──────────────────┘
                       │
                EchoLinkMonitor
                       │
                  NodeState
                       │
      ┌────────────────┴───────────────┐
      │                                │
 Dashboard                    Notifications
```

---

# Design Principles

Every module must have a single responsibility.

Modules never print output directly.

Modules never interact with each other.

Modules only update the shared NodeState object.

The Guardian Engine coordinates the execution of every monitor.

---

# Execution Flow

1. Load configuration
2. Initialize NodeState
3. Execute monitors
4. Update NodeState
5. Save history
6. Generate notifications
7. Wait
8. Repeat

---

# Coding Style

- Python 3
- PEP8 compliant
- Type hints
- Extensive comments
- Modular design
- Logging instead of print()

---

# Project Philosophy

Reliable

Simple

Modular

Open Source

Designed for Amateur Radio operators
