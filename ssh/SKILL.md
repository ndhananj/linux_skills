# SSH and Secure Remote Access

This skill covers using SSH for secure remote administration, file transfer, and tunnelling. SSH (Secure Shell) is the standard protocol for encrypted remote access to Linux systems.

## Concepts

SSH uses **public-key cryptography** to authenticate users and encrypt all traffic. The client holds a **private key** (kept secret) and the server holds the corresponding **public key** in `~/.ssh/authorized_keys`. When connecting, the server challenges the client to prove it holds the private key without revealing it.

The **SSH daemon** (`sshd`) runs on the server and listens on port 22 by default. Its configuration in `/etc/ssh/sshd_config` controls which authentication methods are allowed, which users can connect, and many other security parameters.

**SCP** (Secure Copy Protocol) and **rsync over SSH** are the standard tools for transferring files between hosts. rsync is preferred for large or incremental transfers because it only sends changed blocks.

## Tools Available

| Tool | Description |
|------|-------------|
| `run_remote_command` | Execute a command on a remote host via SSH |
| `copy_to_remote` | Copy a file to a remote host with SCP |
| `copy_from_remote` | Copy a file from a remote host with SCP |
| `sync_to_remote` | Synchronise a directory to a remote host with rsync |
| `generate_ssh_key` | Generate a new SSH key pair |
| `add_known_host` | Add a host key to known_hosts |
| `show_ssh_config` | Display the SSH daemon configuration |
| `restart_ssh_daemon` | Restart sshd to apply configuration changes |

## Usage Examples

**Run a command on a remote server:**
```
run_remote_command(host="192.168.1.10", user="ubuntu", command="df -h")
```

**Copy a file to a remote server:**
```
copy_to_remote(local_path="/etc/nginx/nginx.conf", host="web01", user="ubuntu", remote_path="/tmp/nginx.conf")
```

**Sync a local directory to a remote server:**
```
sync_to_remote(local_path="/opt/app/", host="web01", user="ubuntu", remote_path="/opt/app/", delete=True)
```

**Generate an ed25519 key pair:**
```
generate_ssh_key(key_type="ed25519", key_file="/home/ubuntu/.ssh/deploy_key", comment="deploy@ci")
```

## Skill Levels

**Entry** — Connect to remote hosts, understand public/private key pairs, copy files with SCP.

**Beginner** — Set up key-based authentication, disable password login, use SSH config file for host aliases.

**Intermediate** — Configure SSH tunnels and port forwarding, use ProxyJump for bastion hosts, manage multiple key pairs.

**Advanced** — Harden sshd_config (disable root login, restrict ciphers), implement certificate-based authentication, audit SSH access logs.
