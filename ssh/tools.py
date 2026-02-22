"""
ssh/tools.py — Tools for SSH key management and secure file transfer.

Note: Interactive SSH sessions (ssh user@host) cannot be executed directly
by the agent because they require a TTY.  Use run_remote_command() to
execute non-interactive commands on remote hosts instead.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from command_runner import run_command


def run_remote_command(host: str, user: str, command: str, key_path: str = None, port: int = 22) -> str:
    """Execute a command on a remote host via SSH (non-interactive).

    host: Hostname or IP address of the remote host.
    user: Username to authenticate as.
    command: Shell command to execute on the remote host.
    key_path: Path to the private key file for authentication.
    port: SSH port number on the remote host.
    """
    cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "-p", str(port)]
    if key_path:
        cmd.extend(["-i", key_path])
    cmd.extend([f"{user}@{host}", command])
    return run_command(cmd)


def copy_to_remote(local_path: str, host: str, user: str, remote_path: str, key_path: str = None, port: int = 22) -> str:
    """Copy a file or directory to a remote host using SCP.

    local_path: Local path to the file or directory to copy.
    host: Hostname or IP address of the remote host.
    user: Username to authenticate as.
    remote_path: Destination path on the remote host.
    key_path: Path to the private key file for authentication.
    port: SSH port number on the remote host.
    """
    cmd = ["scp", "-o", "StrictHostKeyChecking=no", "-P", str(port)]
    if key_path:
        cmd.extend(["-i", key_path])
    cmd.extend([local_path, f"{user}@{host}:{remote_path}"])
    return run_command(cmd)


def copy_from_remote(host: str, user: str, remote_path: str, local_path: str, key_path: str = None, port: int = 22) -> str:
    """Copy a file or directory from a remote host using SCP.

    host: Hostname or IP address of the remote host.
    user: Username to authenticate as.
    remote_path: Path on the remote host to copy from.
    local_path: Local destination path.
    key_path: Path to the private key file for authentication.
    port: SSH port number on the remote host.
    """
    cmd = ["scp", "-o", "StrictHostKeyChecking=no", "-P", str(port)]
    if key_path:
        cmd.extend(["-i", key_path])
    cmd.extend([f"{user}@{host}:{remote_path}", local_path])
    return run_command(cmd)


def sync_to_remote(local_path: str, host: str, user: str, remote_path: str, key_path: str = None, delete: bool = False) -> str:
    """Synchronise a local directory to a remote host using rsync.

    local_path: Local directory to synchronise.
    host: Hostname or IP address of the remote host.
    user: Username to authenticate as.
    remote_path: Destination directory on the remote host.
    key_path: Path to the private key file for authentication.
    delete: When True, delete files on the remote that are not in the local source.
    """
    ssh_cmd = "ssh -o StrictHostKeyChecking=no"
    if key_path:
        ssh_cmd += f" -i {key_path}"
    cmd = ["rsync", "-avz", "-e", ssh_cmd]
    if delete:
        cmd.append("--delete")
    cmd.extend([local_path, f"{user}@{host}:{remote_path}"])
    return run_command(cmd)


def generate_ssh_key(key_type: str = "ed25519", key_file: str = None, comment: str = "") -> str:
    """Generate a new SSH key pair.

    key_type: Key algorithm: 'ed25519' (recommended) or 'rsa'.
    key_file: Path to save the private key. Defaults to ~/.ssh/id_<type>.
    comment: Comment to embed in the public key.
    """
    cmd = ["ssh-keygen", "-t", key_type, "-N", "", "-C", comment]
    if key_file:
        cmd.extend(["-f", key_file])
    return run_command(cmd)


def add_known_host(host: str) -> str:
    """Add a host's public key to the known_hosts file.

    host: Hostname or IP address to scan.
    """
    return run_command(["ssh-keyscan", "-H", host])


def show_ssh_config() -> str:
    """Display the SSH daemon configuration."""
    return run_command(["cat", "/etc/ssh/sshd_config"])


def restart_ssh_daemon() -> str:
    """Restart the SSH daemon (sshd) to apply configuration changes."""
    return run_command(["systemctl", "restart", "sshd"])
