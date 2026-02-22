# Containerization

This skill covers building, running, and managing Linux containers using Docker and Docker Compose. Containers package an application and all its dependencies into a portable, isolated unit that runs consistently across any Linux host.

## Concepts

A **container** is a lightweight, isolated process that shares the host kernel but has its own file system, network namespace, and process tree. Unlike virtual machines, containers do not require a full OS image — they use **images** as read-only templates and add a thin writable layer on top.

A **Docker image** is a layered, immutable snapshot built from a `Dockerfile`. Each instruction in the Dockerfile adds a new layer. Images are stored in registries (Docker Hub, GitHub Container Registry, private registries) and pulled on demand.

**Docker Compose** is a tool for defining and running multi-container applications. A `docker-compose.yml` file declares services, networks, and volumes, and `docker compose up` starts the entire stack with a single command.

## Tools Available

| Tool | Description |
|------|-------------|
| `list_containers` | List running (or all) containers |
| `run_container` | Start a new container from an image |
| `stop_container` | Gracefully stop a running container |
| `start_container` | Start a previously stopped container |
| `remove_container` | Delete a container |
| `container_logs` | Fetch container log output |
| `exec_in_container` | Run a command inside a running container |
| `list_images` | List locally available images |
| `pull_image` | Download an image from a registry |
| `remove_image` | Delete a local image |
| `build_image` | Build an image from a Dockerfile |
| `docker_compose` | Run docker compose commands (up, down, ps, logs) |
| `container_stats` | Show real-time resource usage for all containers |
| `inspect_container` | Return detailed JSON metadata about a container |

## Usage Examples

**Run an nginx web server on port 8080:**
```
run_container(image="nginx:latest", name="web", ports="8080:80", detach=True)
```

**View the last 100 lines of a container's logs:**
```
container_logs(container="web", lines=100)
```

**Execute a shell command inside a running container:**
```
exec_in_container(container="web", command="nginx -t")
```

**Start a full stack with Docker Compose:**
```
docker_compose(action="up -d", compose_file="/opt/myapp/docker-compose.yml")
```

**Build a custom image:**
```
build_image(context_path="/opt/myapp", tag="myapp:1.0")
```

## Skill Levels

**Entry** — Pull and run pre-built images, view logs, stop and remove containers.

**Beginner** — Write Dockerfiles, build custom images, map ports and volumes, use environment variables.

**Intermediate** — Use Docker Compose for multi-service applications, understand networking between containers, manage image layers and build cache.

**Advanced** — Optimise image size with multi-stage builds, configure container resource limits, set up private registries, implement health checks and restart policies.
