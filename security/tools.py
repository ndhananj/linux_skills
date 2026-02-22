"""
security/tools.py — Tools for managing Linux firewall, SSH hardening, and system security.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from command_runner import run_command


def ufw_status() -> str:
    """Show the current UFW (Uncomplicated Firewall) status and rules."""
    return run_command(["ufw", "status", "verbose"])


def ufw_enable() -> str:
    """Enable the UFW firewall."""
    return run_command(["ufw", "--force", "enable"])


def ufw_disable() -> str:
    """Disable the UFW firewall."""
    return run_command(["ufw", "disable"])


def ufw_allow(port: str, protocol: str = None, from_ip: str = None) -> str:
    """Allow traffic through the UFW firewall.

    port: Port number or service name to allow, e.g. '22' or 'http'.
    protocol: Optional protocol: 'tcp' or 'udp'.
    from_ip: Optional source IP address or CIDR range to restrict the rule.
    """
    cmd = ["ufw"]
    if from_ip:
        cmd.extend(["allow", "from", from_ip, "to", "any", "port", str(port)])
    else:
        rule = f"{port}/{protocol}" if protocol else str(port)
        cmd.extend(["allow", rule])
    return run_command(cmd)


def ufw_deny(port: str, protocol: str = None) -> str:
    """Deny traffic through the UFW firewall.

    port: Port number or service name to deny.
    protocol: Optional protocol: 'tcp' or 'udp'.
    """
    rule = f"{port}/{protocol}" if protocol else str(port)
    return run_command(["ufw", "deny", rule])


def ufw_delete_rule(rule_number: int) -> str:
    """Delete a UFW rule by its rule number.

    rule_number: Rule number as shown by ufw_status().
    """
    return run_command(["ufw", "--force", "delete", str(rule_number)])


def iptables_list(table: str = "filter") -> str:
    """List iptables rules.

    table: Table to list: 'filter', 'nat', or 'mangle'.
    """
    return run_command(["iptables", "-t", table, "-L", "-n", "-v"])


def iptables_add_rule(chain: str, protocol: str, port: str, action: str, table: str = "filter") -> str:
    """Add an iptables rule.

    chain: Chain to add the rule to: INPUT, OUTPUT, FORWARD.
    protocol: Protocol: tcp or udp.
    port: Destination port number.
    action: Target action: ACCEPT, DROP, or REJECT.
    table: Table to modify: filter, nat, or mangle.
    """
    return run_command([
        "iptables", "-t", table, "-A", chain,
        "-p", protocol, "--dport", str(port),
        "-j", action,
    ])


def generate_ssh_key(key_type: str = "ed25519", key_file: str = None, comment: str = "") -> str:
    """Generate a new SSH key pair.

    key_type: Key algorithm: 'ed25519' (recommended) or 'rsa'.
    key_file: Path to save the private key. Defaults to ~/.ssh/id_<type>.
    comment: Comment to embed in the public key (e.g. your email address).
    """
    cmd = ["ssh-keygen", "-t", key_type, "-N", "", "-C", comment]
    if key_file:
        cmd.extend(["-f", key_file])
    return run_command(cmd)


def copy_ssh_key(user_at_host: str, identity_file: str = None) -> str:
    """Copy the local SSH public key to a remote host's authorized_keys.

    user_at_host: Remote destination in user@host format.
    identity_file: Path to the private key file to use.
    """
    cmd = ["ssh-copy-id"]
    if identity_file:
        cmd.extend(["-i", identity_file])
    cmd.append(user_at_host)
    return run_command(cmd)


def check_open_ports() -> str:
    """List all open ports and the processes listening on them."""
    return run_command(["ss", "-tulnp"])


def show_failed_logins() -> str:
    """Show recent failed login attempts from the auth log."""
    return run_command(["grep", "Failed password", "/var/log/auth.log"], allow_nonzero=True)


def list_sudoers() -> str:
    """Display the current sudoers configuration."""
    return run_command(["cat", "/etc/sudoers"])


def check_file_integrity(path: str, algorithm: str = "sha256") -> str:
    """Compute the checksum of a file for integrity verification.

    path: Path to the file to checksum.
    algorithm: Hash algorithm: 'md5', 'sha1', 'sha256', or 'sha512'.
    """
    return run_command([f"{algorithm}sum", path])


def show_selinux_status() -> str:
    """Show the current SELinux enforcement status."""
    return run_command(["sestatus"], allow_nonzero=True)


def show_apparmor_status() -> str:
    """Show the current AppArmor status and loaded profiles."""
    return run_command(["apparmor_status"], allow_nonzero=True)
