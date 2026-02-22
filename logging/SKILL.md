# Logging and Log Management

This skill covers viewing, searching, and managing system logs on Linux. Effective log management is essential for security auditing, performance analysis, and troubleshooting.

## Concepts

Modern Linux systems use **systemd-journald** as the primary log collector. It captures output from all systemd services, the kernel, and the boot process, and stores it in a binary format queryable with `journalctl`. Traditional text-based logs in `/var/log/` are still written by **rsyslog** or **syslog-ng**, which receive messages forwarded from journald.

**Log rotation** prevents log files from consuming all available disk space. The `logrotate` utility runs periodically (usually daily via cron) and compresses, renames, and eventually deletes old log files according to rules in `/etc/logrotate.conf` and `/etc/logrotate.d/`.

**Log levels** (from most to least severe): `emerg`, `alert`, `crit`, `err`, `warning`, `notice`, `info`, `debug`. Filtering by level helps focus on actionable events.

## Tools Available

| Tool | Description |
|------|-------------|
| `tail_log` | Show the last N lines of a log file |
| `head_log` | Show the first N lines of a log file |
| `search_log` | Search a log file for a pattern |
| `view_journal` | Query the systemd journal with filters |
| `list_log_files` | List files in /var/log |
| `show_dmesg` | Show kernel ring buffer messages |
| `rotate_logs` | Trigger log rotation with logrotate |
| `write_log_entry` | Write a message to the system log |
| `show_auth_log` | Show recent authentication log entries |
| `show_syslog` | Show recent syslog entries |

## Usage Examples

**Show the last 100 lines of the nginx access log:**
```
tail_log(path="/var/log/nginx/access.log", lines=100)
```

**Search for authentication failures:**
```
search_log(path="/var/log/auth.log", pattern="Failed password", ignore_case=True)
```

**Show all errors from the last hour in the systemd journal:**
```
view_journal(since="1 hour ago", priority="err")
```

**Show logs for a specific service:**
```
view_journal(unit="nginx", lines=200)
```

## Skill Levels

**Entry** — Read log files with tail/cat, understand log file locations, use grep to search logs.

**Beginner** — Use journalctl to query the systemd journal, filter by service and time range, understand log rotation.

**Intermediate** — Configure rsyslog to forward logs to a central server, write custom logrotate rules, set up log alerting.

**Advanced** — Implement structured logging, deploy a centralised log management stack (ELK/Loki), correlate logs across multiple systems for security incident response.
