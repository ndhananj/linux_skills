# Troubleshooting

This skill provides tools for troubleshooting common issues on a Linux system, including hardware and network problems.

## Concepts

- **PCI (Peripheral Component Interconnect):** A local computer bus for attaching hardware devices in a computer.
- **USB (Universal Serial Bus):** An industry standard that establishes specifications for cables and connectors and protocols for connection, communication and power supply between computers, peripheral devices and other computers.
- **DMI (Desktop Management Interface):** A framework for managing and tracking components in a desktop, notebook or server computer, by abstracting these components from the software that manages them.
- **DNS Resolution:** The process of translating a domain name into an IP address.

## Tools

### `list_pci_devices`

Lists PCI devices. This tool is a wrapper for the `lspci` command.

**Usage:**

```python
def list_pci_devices() -> str:
    """
    Lists PCI devices.

    Returns:
        The output of the lspci command.
    """
    pass
```

### `list_usb_devices`

Lists USB devices. This tool is a wrapper for the `lsusb` command.

**Usage:**

```python
def list_usb_devices() -> str:
    """
    Lists USB devices.

    Returns:
        The output of the lsusb command.
    """
    pass
```

### `list_dmi_info`

Lists DMI (Desktop Management Interface) information. This tool is a wrapper for the `dmidecode` command.

**Usage:**

```python
def list_dmi_info() -> str:
    """
    Lists DMI (Desktop Management Interface) information.

    Returns:
        The output of the dmidecode command.
    """
    pass
```

### `systemd_resolve`

Resolves domain names, IP addresses, and other resource records. This tool is a wrapper for the `systemd-resolve` command.

**Usage:**

```python
def systemd_resolve(name: str) -> str:
    """
    Resolves domain names, IP addresses, and other resource records.

    Args:
        name: The name to resolve.

    Returns:
        The output of the systemd-resolve command.
    """
    pass
```
