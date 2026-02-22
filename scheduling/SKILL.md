# Task Scheduling

This skill covers scheduling commands and scripts to run automatically at specific times or intervals using cron, at, and systemd timers.

## Concepts

**cron** is the classic Unix job scheduler. The **crontab** (cron table) is a per-user file that lists jobs and their schedules. Each line has five time fields (minute, hour, day-of-month, month, day-of-week) followed by the command to run. The system-wide crontab is at `/etc/crontab`; per-user crontabs are managed with `crontab -e`.

The **at** command schedules a one-time job to run at a specific time. Unlike cron, which runs jobs repeatedly, `at` runs a job once and then discards it.

**systemd timers** are the modern alternative to cron. A timer unit (`.timer`) activates a corresponding service unit (`.service`) on a schedule. Timers support monotonic schedules (e.g. "30 minutes after boot") in addition to calendar-based schedules, and their execution is logged in the systemd journal.

## Tools Available

| Tool | Description |
|------|-------------|
| `list_cron_jobs` | List crontab entries for a user |
| `add_cron_job` | Add a new cron job |
| `remove_cron_job` | Remove cron jobs matching a pattern |
| `schedule_at_job` | Schedule a one-time job with at |
| `list_at_jobs` | List pending at jobs |
| `remove_at_job` | Remove a pending at job |
| `list_systemd_timers` | List all systemd timers and their next trigger |

## Cron Schedule Reference

| Expression | Meaning |
|------------|---------|
| `* * * * *` | Every minute |
| `0 * * * *` | Every hour |
| `0 2 * * *` | Daily at 02:00 |
| `0 2 * * 0` | Weekly on Sunday at 02:00 |
| `0 2 1 * *` | Monthly on the 1st at 02:00 |
| `*/15 * * * *` | Every 15 minutes |

## Usage Examples

**Schedule a daily backup at 3am:**
```
add_cron_job(schedule="0 3 * * *", command="/opt/scripts/backup.sh >> /var/log/backup.log 2>&1")
```

**Run a one-time database migration in 5 minutes:**
```
schedule_at_job(time="now + 5 minutes", command="/opt/scripts/migrate.sh")
```

**List all scheduled jobs:**
```
list_cron_jobs()
list_at_jobs()
list_systemd_timers()
```

## Skill Levels

**Entry** — Understand cron syntax, list and add simple cron jobs.

**Beginner** — Use environment variables in crontab, redirect output to log files, use `at` for one-time tasks.

**Intermediate** — Create systemd timer units, use `@reboot` and `@daily` shortcuts, manage system-wide cron jobs in `/etc/cron.d/`.

**Advanced** — Implement distributed job scheduling, use `flock` to prevent overlapping runs, monitor job execution with alerting.
