# Contributing to SVX Guardian

## 1. Purpose

This document defines the development and contribution rules for the
SVX Guardian project.

The goal is to keep code, documentation, and architecture consistent,
verifiable, and maintainable over time, regardless of the number of
developers or work sessions.

All project changes must follow these guidelines.

---

## 2. Development Philosophy

SVX Guardian prioritizes:

- simplicity;
- clarity;
- modularity;
- readability;
- reliability;
- stability;
- compatibility;
- verifiability.

A simple, verifiable, and well-documented solution is preferable to an
unnecessarily complex one.

A feature that is only planned or designed must not be described as
implemented or complete.

---

## 3. Working Environments

Development uses two separate environments:

- **LAB**: development, modification, and testing;
- **Legacy**: real node with radio traffic, used after validation on
  the LAB and GitHub.

The Legacy node must not be used as the primary development
environment.

Its purpose is to verify Guardian behavior on a real SvxLink
installation with actual radio traffic.

---

## 4. Development Flow

The reference operational flow is:

```text
Design → LAB → pytest → functional test → GPG commit → GitHub
→ Legacy (merge --ff-only) → pytest → restart → real traffic
```

Each step must be verified before moving to the next one.

Changes must first be validated on the LAB.

Only after the corresponding commit has been published and validated
should the Legacy node be updated.

A feature that requires real traffic must not be considered fully
validated solely on the basis of LAB testing.

---

## 5. Operating Method

During development, preferably proceed:

- one step at a time;
- with clearly delimited changes;
- with verification before the next step;
- always reading the actual current version of a file before modifying
  it.

When a change is provided manually for copy and paste, prefer a
complete file ready to copy rather than partial patches when this
reduces the risk of errors or lost context.

Do not use `sudo` to modify files inside the repository.

---

## 6. Pre-Commit Checks

Before every commit, run at least:

```bash
git diff --check
pytest -q
git status --short
```

Also verify:

- that the expected tests pass;
- that the affected documentation is up to date;
- that no temporary or unwanted files are present;
- that no secrets, credentials, or private configuration are included;
- that the diff contains only the intended changes.

Commits intended for the production repository must be signed.

---

## 7. Git and Publishing

The main branch is `main`.

Validated changes are published to GitHub according to the project
workflow.

On the Legacy node, synchronization with the repository must preserve
a linear history by using, when required by the operational flow:

```bash
git merge --ff-only
```

After updating the Legacy node, the relevant automated tests must be
repeated before restart and validation with real traffic.

After pushing, verify that the local and remote repositories are in the
expected state.

---

## 8. Documentation

Documentation is an integral part of the project.

The main structure includes:

### `README.md` / `README.en.md`

Concise project presentation in Italian and English respectively.

### `docs/PROJECT.md` / `docs/PROJECT.en.md`

General project vision and objectives.

### `docs/ARCHITECTURE.md` / `docs/ARCHITECTURE.en.md`

Software architecture and structural principles.

### `docs/DEVELOPMENT.md` / `docs/DEVELOPMENT.en.md`

Development information and procedures.

### `docs/ROADMAP.md` / `docs/ROADMAP.en.md`

Project direction and future activities.

### `docs/DASHBOARD.md` / `docs/DASHBOARD.en.md`

Functional specifications and dashboard organization.

Documentation must clearly distinguish between:

- implemented features;
- features under development;
- planned features.

Do not invent release or milestone numbers that have not been formally
defined in the repository.

---

## 9. Python Conventions

Python code should prioritize:

- a clearly identifiable responsibility for each component;
- readable code;
- reasonably sized functions;
- type hints where appropriate;
- docstrings for public classes and functions;
- logging instead of unstructured diagnostic output;
- separation between acquisition, state, and presentation.

Monitors must operate through the interfaces and state objects defined
by the architecture.

Do not introduce direct dependencies between monitors when
communication can take place through shared state.

---

## 10. HTML and Presentation

Visible interface strings must use the translation system provided by
the project.

Do not move technical logic or state interpretation into templates
when it belongs at the application layer.

Interface changes must be verified on both desktop and mobile.

Guardian's established visual style and colors must be preserved unless
an explicit project decision changes them.

---

## 11. CSS

Prefer descriptive names and easily maintainable rules.

Avoid duplication when a common rule can be reused.

Responsive changes must not solve a desktop problem by creating a
mobile problem, or vice versa.

---

## 12. JSON and Structured Data

Keep structures stable, documented, and consistent with the internal
model.

Internal state values must be technical and canonical.

Localized representation belongs to the presentation layer and must not
change the meaning of internal data.

---

## 13. Internationalization

Guardian's internal state is language-independent.

Translation is applied at presentation layers such as the dashboard,
console, and descriptive user-facing output.

International technical terms may remain unchanged, for example:

- SvxLink;
- EchoLink;
- Reflector;
- RX;
- TX;
- TG;
- CTCSS.

When a translatable string is added or changed, keep the relevant
localization files in the `locale/` directory synchronized.

---

## 14. Secrets and Private Configuration

Credentials, passwords, keys, tokens, and other secrets must not be
stored in the Git repository.

Guardian's private configuration must be kept outside the repository.

The current installation uses:

```text
/etc/svxguardian
```

The persistent Flask session key is stored in:

```text
/etc/svxguardian/secret.key
```

Future installation and provisioning procedures must create and
configure private files with appropriate ownership and permissions,
without hardcoded secrets.

---

## 15. Logs and Performance

The SvxLink RAW LOG must remain RAW.

The RAW LOG page and API must not reinterpret or classify the displayed
lines.

Frequently executed functions must avoid complete and repeated logfile
scans when an incremental or equivalent strategy can be used.

Optimizations that change observable behavior must first be tested on
the LAB and subsequently, when necessary, on the Legacy node.

---

## 16. Compatibility

SVX Guardian must be able to operate on different SvxLink
installations.

Do not assume a specific hardware configuration or a single
configuration-file variant.

Already supported legacy compatibility must be preserved unless an
explicit and documented decision changes it.

The node used for development is a test environment, not a universal
installation model.

---

## 17. Reflector and Application Clients

SvxLink nodes connected to the Reflector and application users/clients
are distinct concepts.

Do not artificially insert users coming from application clients such
as LATRY into `reflector_connected_nodes`.

Any new state model for Reflector users must first be analyzed and
tested with real traffic.

The `/monitor` view must not be modified to integrate these users until
the corresponding model is stable and validated on the `/reflector`
page.

---

## 18. Quality Checks

Before considering an activity complete, verify as appropriate:

- automated tests;
- functional tests;
- desktop and mobile behavior;
- validation with real traffic when required;
- documentation;
- repository state;
- absence of formatting errors reported by `git diff --check`.

Checks must be repeatable.

---

## 19. Goal of Every Change

Every change should improve at least one of the following:

- reliability;
- simplicity;
- readability;
- maintainability;
- documentation;
- compatibility;
- performance;
- Sysop experience.

A feature that has not been sufficiently verified and documented must
not be considered complete.
