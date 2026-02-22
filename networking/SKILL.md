# Networking

This skill provides a comprehensive set of tools for managing network configurations, connections, and troubleshooting on a Linux system.

## Concepts

- **IP Address:** A unique numerical label assigned to each device connected to a computer network that uses the Internet Protocol for communication.
- **Subnet Mask:** A number that defines a range of IP addresses that can be used in a network.
- **Gateway:** A node on a network that serves as an access point to another network.
- **DNS (Domain Name System):** A hierarchical and decentralized naming system for computers, services, or other resources connected to the Internet or a private network.
- **Firewall:** A network security system that monitors and controls incoming and outgoing network traffic based on predetermined security rules.

## Tools

### `ip_address`

Shows and manipulates routing, devices, policy routing and tunnels. This tool is a wrapper for the `ip` command.

**Usage:**

```python
def ip_address(options: str) -> str:
    """
    Shows and manipulates routing, devices, policy routing and tunnels.

    Args:
        options: The options to pass to the ip command (e.g., 'addr show', 'route show').

    Returns:
        The output of the ip command.
    """
    pass
```

### `ifconfig`

Configures network interfaces. This tool is a wrapper for the `ifconfig` command.

**Usage:**

```python
def ifconfig(interface: str = None, options: str = None) -> str:
    """
    Configures network interfaces.

    Args:
        interface: The network interface to configure (e.g., 'eth0').
        options: The options to pass to the ifconfig command (e.g., 'up', 'down').

    Returns:
        The output of the ifconfig command.
    """
    pass
```

### `hostname`

Shows or sets the system's host name. This tool is a wrapper for the `hostname` command.

**Usage:**

```python
def hostname(name: str = None) -> str:
    """
    Shows or sets the system's host name.

    Args:
        name: The new host name.

    Returns:
        The host name.
    """
    pass
```

### `arp`

Manipulates the system's ARP cache. This tool is a wrapper for the `arp` command.

**Usage:**

```python
def arp(options: str) -> str:
    """
    Manipulates the system's ARP cache.

    Args:
        options: The options to pass to the arp command (e.g., '-a', '-d 192.168.1.1').

    Returns:
        The output of the arp command.
    """
    pass
```

### `route`

Shows or manipulates the IP routing table. This tool is a wrapper for the `route` command.

**Usage:**

```python
def route(options: str) -> str:
    """
    Shows or manipulates the IP routing table.

    Args:
        options: The options to pass to the route command (e.g., '-n', 'add default gw 192.168.1.1').

    Returns:
        The output of the route command.
    """
    pass
```

### `dig`

DNS lookup utility. This tool is a wrapper for the `dig` command.

**Usage:**

```python
def dig(name: str, type: str = 'A') -> str:
    """
    DNS lookup utility.

    Args:
        name: The name to lookup.
        type: The type of record to lookup (e.g., 'A', 'MX', 'TXT').

    Returns:
        The output of the dig command.
    """
    pass
```

### `nslookup`

Queries Internet name servers interactively. This tool is a wrapper for the `nslookup` command.

**Usage:**

```python
def nslookup(name: str) -> str:
    """
    Queries Internet name servers interactively.

    Args:
        name: The name to lookup.

    Returns:
        The output of the nslookup command.
    """
    pass
```

### `traceroute`

Prints the route packets trace to network host. This tool is a wrapper for the `traceroute` command.

**Usage:**

```python
def traceroute(host: str) -> str:
    """
    Prints the route packets trace to network host.

    Args:
        host: The host to trace the route to.

    Returns:
        The output of the traceroute command.
    """
    pass
```

### `curl`

Transfers data from or to a server. This tool is a wrapper for the `curl` command.

**Usage:**

```python
def curl(url: str, options: str = None) -> str:
    """
    Transfers data from or to a server.

    Args:
        url: The URL to transfer data from or to.
        options: The options to pass to the curl command (e.g., '-X POST', '-d "key=value"').

    Returns:
        The output of the curl command.
    """
    pass
```

### `wget`

The non-interactive network downloader. This tool is a wrapper for the `wget` command.

**Usage:**

```python
def wget(url: str, options: str = None) -> None:
    """
    The non-interactive network downloader.

    Args:
        url: The URL to download from.
        options: The options to pass to the wget command (e.g., '-O /path/to/file').
    """
    pass
```

### `netcat`

Arbitrary TCP and UDP connections and listens. This tool is a wrapper for the `nc` command.

**Usage:**

```python
def netcat(options: str) -> str:
    """
    Arbitrary TCP and UDP connections and listens.

    Args:
        options: The options to pass to the nc command (e.g., '-l -p 1234', 'example.com 80').

    Returns:
        The output of the nc command.
    """
    pass
```

### `netstat`

Prints network connections, routing tables, interface statistics, masquerade connections, and multicast memberships. This tool is a wrapper for the `netstat` command.

**Usage:**

```python
def netstat(options: str) -> str:
    """
    Prints network connections, routing tables, interface statistics, masquerade connections, and multicast memberships.

    Args:
        options: The options to pass to the netstat command (e.g., '-tulpn', '-r').

    Returns:
        The output of the netstat command.
    """
    pass
```
