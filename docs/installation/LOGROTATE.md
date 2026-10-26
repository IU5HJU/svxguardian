# SVX Guardian - SvxLink Logfile Rotation

> 🇬🇧 **English documentation**
> 🇮🇹 [Documentazione italiana](../it/installation/LOGROTATE.md)

## Overview

`ReflectorMonitor` and `EchoLinkMonitor` reconstruct the current node
state by scanning the SvxLink logfile backwards, looking for the most
recent status line (connection, disconnection, node snapshot).

Without `logrotate` configured for the SvxLink logfile (typically
`/var/log/svxlink`), the file grows without bound. On a real node this
reached 17 MB after 95 days of uptime, and every dashboard request
scanned further back into an ever-growing file, degrading the whole
dashboard.

SVX Guardian addresses this from two independent angles:

- `ReflectorMonitor.MAX_BACKWARD_SCAN_BYTES` bounds how far back the
  application itself ever scans (see
  `src/modules/reflector.py`), so a missing or failed log rotation
  does not bring the dashboard back to multi-second response times;
- `install/logrotate/` lets the Sysop configure OS-level `logrotate`
  for the SvxLink logfile, so it does not keep growing on disk in the
  first place.

Both fixes are complementary and should normally be applied together.

---

## Logrotate Installation Tools

SVX Guardian provides:

```text
install/logrotate/configure-logrotate.sh
install/logrotate/svxlink.logrotate.template
```

---

## svxlink.logrotate.template

The generic `logrotate` template for the SvxLink logfile.

It does not contain node-specific values.

Template variables:

```text
@SVXGUARDIAN_SVXLINK_LOG@
@SVXGUARDIAN_LOGROTATE_SIZE@
@SVXGUARDIAN_LOGROTATE_ROTATE@
```

The rendered configuration uses `copytruncate`, so SvxLink keeps
writing to the same inode it already has open — no SvxLink restart
or log-reopen signal is required after a rotation.

---

## configure-logrotate.sh

The interactive configurator must be run as root:

```bash
sudo ./install/logrotate/configure-logrotate.sh
```

It performs the following steps:

1. detects the SvxLink logfile, using the same priority order as
   `ConfigManager._resolve_log_file`:
   - `SVXGUARDIAN_SVXLINK_LOG` environment override;
   - `LOGFILE=` from a SvxLink systemd defaults file
     (`/etc/default/svxlink` or `/usr/local/etc/default/svxlink`);
   - known existing installation layouts
     (`/var/log/svxlink`, `/usr/local/var/log/svxlink`);
   - historical Debian/Raspberry Pi OS path as fallback;
2. asks for the maximum size before rotation (default `10M`) and the
   number of rotations to keep (default `14`), validating both
   inputs;
3. creates a timestamped backup of any existing
   `/etc/logrotate.d/svxlink` before overwriting it;
4. renders the template and checks that no `@SVXGUARDIAN_*@`
   placeholder is left unresolved;
5. installs the configuration and validates it with
   `logrotate -d`, restoring the backup (or removing the file if
   there was no previous configuration) if validation fails.

A successful run returns:

```text
LOGROTATE_CONFIG_STATUS=SUCCESS
```

---

## Checking an Existing Configuration

If a previous `/etc/logrotate.d/svxlink` already exists, it is
backed up as:

```text
/etc/logrotate.d/svxlink.backup-<timestamp>
```

To compare it with the configuration SVX Guardian just installed:

```bash
diff /etc/logrotate.d/svxlink.backup-<timestamp> /etc/logrotate.d/svxlink
```

Note: a logrotate stanza combining a time interval (`daily`,
`weekly`, `monthly`) with `size` is not a conflict — per the
`logrotate` manual, when `size` is present the time interval is
ignored and rotation is governed purely by size, checked on every
`logrotate` cron run. A pre-existing `daily` directive alongside
`size` is therefore redundant, not a behavior change.

---

## Validating the Installed Configuration

```bash
sudo logrotate -d /etc/logrotate.d/svxlink
```

A dry run (`-d`) never rotates the logfile; it only reports what
would happen.

To force an actual rotation for testing:

```bash
sudo logrotate -f /etc/logrotate.d/svxlink
```

---

## Related Documentation

For the application-side bound on backward log scanning, see
`src/modules/reflector.py::MAX_BACKWARD_SCAN_BYTES` and the
"Performance" design principle in:

```text
docs/ARCHITECTURE.en.md
```
