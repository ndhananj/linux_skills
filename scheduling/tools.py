"""
scheduling/tools.py — Tools for scheduling commands and scripts on Linux.
"""

import sys
import os
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from command_runner import run_command


def list_cron_jobs(user: str = None) -> str:
    """List the current crontab entries.

    user: Optional username to list crontab for. Defaults to the current user.
    """
    cmd = ["crontab", "-l"]
    if user:
        cmd.extend(["-u", user])
    return run_command(cmd, allow_nonzero=True)


def add_cron_job(schedule: str, command: str, user: str = None) -> str:
    """Add a new cron job to the crontab.

    schedule: Cron schedule expression, e.g. '0 2 * * *' for daily at 2am.
    command: Shell command to run on the schedule.
    user: Optional username whose crontab to modify.
    """
    # Read existing crontab
    list_cmd = ["crontab", "-l"]
    if user:
        list_cmd.extend(["-u", user])
    try:
        existing = run_command(list_cmd, allow_nonzero=True)
    except Exception:
        existing = ""

    new_entry = f"{schedule} {command}"
    if new_entry in existing:
        return f"Cron job already exists: {new_entry}"

    new_crontab = (existing.strip() + "\n" + new_entry + "\n").lstrip()

    # Write back via stdin
    write_cmd = ["crontab"]
    if user:
        write_cmd.extend(["-u", user])
    write_cmd.append("-")

    result = subprocess.run(
        write_cmd,
        input=new_crontab,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    return f"Cron job added: {new_entry}"


def remove_cron_job(pattern: str, user: str = None) -> str:
    """Remove cron jobs whose command line contains a given pattern.

    pattern: String to match against existing cron job lines.
    user: Optional username whose crontab to modify.
    """
    list_cmd = ["crontab", "-l"]
    if user:
        list_cmd.extend(["-u", user])
    existing = run_command(list_cmd, allow_nonzero=True)

    lines = [ln for ln in existing.splitlines() if pattern not in ln]
    new_crontab = "\n".join(lines) + "\n"

    write_cmd = ["crontab"]
    if user:
        write_cmd.extend(["-u", user])
    write_cmd.append("-")

    result = subprocess.run(write_cmd, input=new_crontab, capture_output=True, text=True)
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    return f"Removed cron jobs matching: {pattern}"


def schedule_at_job(time: str, command: str) -> str:
    """Schedule a one-time command to run at a specific time using at.

    time: Time specification, e.g. 'now + 5 minutes', '14:30', 'midnight'.
    command: Shell command to run at the specified time.
    """
    result = subprocess.run(
        ["at", time],
        input=command,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() or result.stderr.strip()


def list_at_jobs() -> str:
    """List pending at jobs."""
    return run_command(["atq"], allow_nonzero=True)


def remove_at_job(job_id: int) -> str:
    """Remove a pending at job.

    job_id: Job ID as shown by list_at_jobs().
    """
    return run_command(["atrm", str(job_id)])


def list_systemd_timers() -> str:
    """List all systemd timer units and their next trigger times."""
    return run_command(["systemctl", "list-timers", "--all"])
