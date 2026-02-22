"""
containerization/tools.py — Tools for managing Docker containers and images.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from command_runner import run_command


def list_containers(all_containers: bool = False) -> str:
    """List Docker containers.

    all_containers: When True, show all containers including stopped ones.
    """
    cmd = ["docker", "ps"]
    if all_containers:
        cmd.append("-a")
    return run_command(cmd)


def run_container(image: str, name: str = None, ports: str = None, volumes: str = None,
                  env: str = None, detach: bool = True, command: str = None) -> str:
    """Run a new Docker container.

    image: Docker image name and optional tag, e.g. 'nginx:latest'.
    name: Optional name for the container.
    ports: Port mapping in 'host:container' format, e.g. '8080:80'.
    volumes: Volume mount in 'host:container' format, e.g. '/data:/app/data'.
    env: Environment variable in 'KEY=VALUE' format.
    detach: When True, run the container in the background.
    command: Optional command to run inside the container.
    """
    cmd = ["docker", "run"]
    if detach:
        cmd.append("-d")
    if name:
        cmd.extend(["--name", name])
    if ports:
        cmd.extend(["-p", ports])
    if volumes:
        cmd.extend(["-v", volumes])
    if env:
        cmd.extend(["-e", env])
    cmd.append(image)
    if command:
        cmd.extend(command.split())
    return run_command(cmd)


def stop_container(container: str) -> str:
    """Stop a running Docker container.

    container: Container name or ID.
    """
    return run_command(["docker", "stop", container])


def start_container(container: str) -> str:
    """Start a stopped Docker container.

    container: Container name or ID.
    """
    return run_command(["docker", "start", container])


def remove_container(container: str, force: bool = False) -> str:
    """Remove a Docker container.

    container: Container name or ID.
    force: When True, force removal of a running container.
    """
    cmd = ["docker", "rm"]
    if force:
        cmd.append("-f")
    cmd.append(container)
    return run_command(cmd)


def container_logs(container: str, lines: int = 50) -> str:
    """Fetch the logs of a Docker container.

    container: Container name or ID.
    lines: Number of recent log lines to show.
    """
    return run_command(["docker", "logs", "--tail", str(lines), container])


def exec_in_container(container: str, command: str) -> str:
    """Execute a command inside a running Docker container.

    container: Container name or ID.
    command: Shell command to execute inside the container.
    """
    return run_command(["docker", "exec", container, "bash", "-c", command])


def list_images() -> str:
    """List Docker images."""
    return run_command(["docker", "images"])


def pull_image(image: str) -> str:
    """Pull a Docker image from a registry.

    image: Image name and optional tag, e.g. 'ubuntu:22.04'.
    """
    return run_command(["docker", "pull", image])


def remove_image(image: str, force: bool = False) -> str:
    """Remove a Docker image.

    image: Image name or ID.
    force: When True, force removal even if the image is in use.
    """
    cmd = ["docker", "rmi"]
    if force:
        cmd.append("-f")
    cmd.append(image)
    return run_command(cmd)


def build_image(context_path: str, tag: str, dockerfile: str = None) -> str:
    """Build a Docker image from a Dockerfile.

    context_path: Path to the build context directory.
    tag: Name and optional tag for the image, e.g. 'myapp:1.0'.
    dockerfile: Path to the Dockerfile. Defaults to Dockerfile in context_path.
    """
    cmd = ["docker", "build", "-t", tag]
    if dockerfile:
        cmd.extend(["-f", dockerfile])
    cmd.append(context_path)
    return run_command(cmd)


def docker_compose(action: str, compose_file: str = None) -> str:
    """Run a docker compose command.

    action: Compose action: 'up -d', 'down', 'ps', 'logs', 'pull', etc.
    compose_file: Path to the docker-compose.yml file. Defaults to ./docker-compose.yml.
    """
    cmd = ["docker", "compose"]
    if compose_file:
        cmd.extend(["-f", compose_file])
    cmd.extend(action.split())
    return run_command(cmd)


def container_stats() -> str:
    """Show a live stream of container resource usage statistics (one snapshot)."""
    return run_command(["docker", "stats", "--no-stream"])


def inspect_container(container: str) -> str:
    """Return low-level information about a Docker container.

    container: Container name or ID.
    """
    return run_command(["docker", "inspect", container])
