"""
networking/tools.py — Tools for managing Linux network interfaces, routing, and connectivity.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from command_runner import run_command


def show_interfaces(interface: str = None) -> str:
    """Show network interfaces and their IP addresses.

    interface: Optional interface name (e.g. 'eth0') to show only that interface.
    """
    cmd = ["ip", "addr", "show"]
    if interface:
        cmd.append(interface)
    return run_command(cmd)


def bring_interface_up(interface: str) -> str:
    """Bring a network interface up.

    interface: Interface name, e.g. 'eth0'.
    """
    return run_command(["ip", "link", "set", interface, "up"])


def bring_interface_down(interface: str) -> str:
    """Bring a network interface down.

    interface: Interface name, e.g. 'eth0'.
    """
    return run_command(["ip", "link", "set", interface, "down"])


def assign_ip_address(interface: str, address: str) -> str:
    """Assign an IP address to a network interface.

    interface: Interface name, e.g. 'eth0'.
    address: IP address with prefix length, e.g. '192.168.1.10/24'.
    """
    return run_command(["ip", "addr", "add", address, "dev", interface])


def show_routing_table() -> str:
    """Show the kernel IP routing table."""
    return run_command(["ip", "route", "show"])


def add_route(network: str, gateway: str) -> str:
    """Add a static route to the routing table.

    network: Destination network in CIDR notation, e.g. '10.0.0.0/8'.
    gateway: Gateway IP address, e.g. '192.168.1.1'.
    """
    return run_command(["ip", "route", "add", network, "via", gateway])


def delete_route(network: str) -> str:
    """Delete a route from the routing table.

    network: Destination network in CIDR notation, e.g. '10.0.0.0/8'.
    """
    return run_command(["ip", "route", "del", network])


def ping_host(host: str, count: int = 4) -> str:
    """Send ICMP echo requests to a host to test connectivity.

    host: Hostname or IP address to ping.
    count: Number of packets to send.
    """
    return run_command(["ping", "-c", str(count), host])


def traceroute_host(host: str) -> str:
    """Print the route packets take to a network host.

    host: Hostname or IP address to trace.
    """
    return run_command(["traceroute", host])


def dns_lookup(name: str, record_type: str = "A") -> str:
    """Perform a DNS lookup.

    name: Domain name to look up.
    record_type: DNS record type: A, AAAA, MX, NS, TXT, CNAME, etc.
    """
    return run_command(["dig", name, "-t", record_type, "+short"])


def reverse_dns_lookup(ip_address: str) -> str:
    """Perform a reverse DNS lookup for an IP address.

    ip_address: IPv4 or IPv6 address to look up.
    """
    return run_command(["dig", "-x", ip_address, "+short"])


def show_open_ports() -> str:
    """Show all open TCP and UDP ports and the processes listening on them."""
    return run_command(["ss", "-tulnp"])


def show_active_connections() -> str:
    """Show all active network connections."""
    return run_command(["ss", "-tnp"])


def download_file(url: str, output_path: str = None) -> str:
    """Download a file from a URL.

    url: URL of the file to download.
    output_path: Local path to save the file. If omitted, saves to current directory.
    """
    cmd = ["wget", "--quiet", "--show-progress"]
    if output_path:
        cmd.extend(["-O", output_path])
    cmd.append(url)
    return run_command(cmd)


def http_request(url: str, method: str = "GET", headers: str = None, data: str = None) -> str:
    """Make an HTTP request and return the response body.

    url: URL to request.
    method: HTTP method: GET, POST, PUT, DELETE, etc.
    headers: Extra headers in 'Key: Value' format, comma-separated.
    data: Request body for POST/PUT requests.
    """
    cmd = ["curl", "-s", "-X", method]
    if headers:
        for header in headers.split(","):
            cmd.extend(["-H", header.strip()])
    if data:
        cmd.extend(["-d", data])
    cmd.append(url)
    return run_command(cmd)


def show_hostname() -> str:
    """Show the system's hostname."""
    return run_command(["hostname"])


def set_hostname(name: str) -> str:
    """Set the system's hostname.

    name: New hostname.
    """
    return run_command(["hostnamectl", "set-hostname", name])


def show_arp_table() -> str:
    """Show the ARP table (IP to MAC address mappings)."""
    return run_command(["arp", "-n"])
