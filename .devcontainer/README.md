# AMAS Development Container

This directory contains the Dev Container configuration for the AMAS project.

## Purpose

The Dev Container provides a consistent, reproducible development environment with:
- Python 3.11 on Debian Bullseye
- Pre-configured VS Code extensions (Python, Ruff, YAML, GitHub Pull Requests and Issues, Docker)
  - These extensions are recommended in `.vscode/extensions.json` and will be suggested when opening the workspace
- Docker-in-Docker support for containerized builds
- GitHub CLI for repository operations
- Automated dependency installation and setup

## Required Files

The Dev Container setup requires the following files:

- **`.devcontainer/devcontainer.json`**: Main configuration file (see "Configuration Example" below)
- **`.devcontainer/setup.sh`**: Setup script for lifecycle commands (must be executable)

To create `setup.sh` if missing:
```bash
touch .devcontainer/setup.sh
chmod +x .devcontainer/setup.sh
```

The script must handle these arguments:
- `onCreate`: Optional setup (e.g., creating `.env` from `.env.example`)
- `postCreate`: Required setup (e.g., installing dependencies)
- `updateContent`: Updates when container content changes

See `.devcontainer/setup.sh` in the repository for the full implementation.

## Configuration Overview

### Lifecycle Commands

- **`initializeCommand`**: Validates Python version (3.11+)
- **`onCreateCommand`**: Performs optional setup (creates `.env` from `.env.example` if available)
  - Non-blocking: Warns if setup.sh missing, continues
- **`postCreateCommand`**: Required setup (installs dependencies)
  - Strict: Fails if setup.sh missing or execution fails
- **`updateContentCommand`**: Updates dependencies when container content changes
  - Strict: Fails if setup.sh missing or execution fails

### Resource Limits

- **Memory**: 4GB (sufficient for Python development with dependencies)
- **CPUs**: 2 cores (balanced for compilation and parallelism)

### Timeouts

All lifecycle commands have a 300-second (5-minute) timeout to prevent indefinite hangs.
- **Default**: 300 seconds (5 minutes) is reasonable for most dependency installations
- **For Large Projects**: If dependency installation takes longer, you can override both the shell timeout and VS Code's lifecycle timeout:
  ```json
  {
    "postCreateCommand": "timeout 600 .devcontainer/setup.sh postCreate",
    "lifecycleTimeout": 600
  }
  ```
  Note: The shell `timeout` command limits script runtime, but VS Code's Dev Containers also enforce a `lifecycleTimeout`. Set both for complete control.
- **Note**: Large Python projects with complex dependencies (numpy, pandas, torch) may require up to 10 minutes on cold starts with slow internet

### Performance Optimization

To reduce `postCreateCommand` execution time and improve container startup:

1. **Pip Caching**: Use volume mounts for pip cache (already configured):
   ```json
   "mounts": [
     "source=amas-pip-cache,target=/home/vscode/.cache/pip,type=volume"
   ]
   ```

2. **Docker Layer Caching**: If using a Dockerfile, structure it for optimal caching:
   ```dockerfile
   COPY requirements.txt .
   RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
   COPY . .
   ```

3. **Pre-built Base Images**: Consider using base images with common dependencies pre-installed

4. **Use `.dockerignore`**: Exclude unnecessary files (`node_modules`, `.git`, etc.) to reduce build context

5. **Pip Configuration**: Use `--cache-dir` in `setup.sh` or configure `pip.conf` for consistent caching

### Security Considerations

1. **Script Execution**: `setup.sh` is executed with explicit permissions (`chmod +x`)
   - **Important**: Review `setup.sh` in PRs before merging. The script runs with container user privileges.
   - **Trust**: Only use `setup.sh` from trusted sources. For high-security environments, consider adding checksum validation:
     ```bash
     echo "expected_sha256_checksum  .devcontainer/setup.sh" | sha256sum -c - || exit 1
     ```
   - **Principle of Least Privilege**: Script runs as `vscode` user (non-root) to limit privilege escalation risk
2. **Timeout Protection**: All commands timeout after 5 minutes to prevent indefinite hangs
   - Note: Timeouts prevent hangs but don't protect against malicious payloads completing within the time window
   - Combine with minimal required privileges and input validation
3. **Error Handling**: Fail-fast behavior for critical setup steps prevents partial/insecure configurations
4. **Non-root User**: Container runs as `vscode` user (not root) to limit privilege escalation risk
5. **Image Updates**: Base images should be regularly updated to include security patches (see "Image Tagging" above)

### Base Image

- **Source**: `mcr.microsoft.com/devcontainers/python:1-3.11-bullseye`
- **Description**: Official Microsoft Dev Container image for Python 3.11 on Debian Bullseye
- **Repository**: https://github.com/microsoft/vscode-dev-containers

### Image Tagging

The image tag `1-3.11-bullseye` is standard practice for Dev Containers:
- Microsoft maintains backward compatibility
- Tags are updated with security patches and tooling improvements automatically
- For stricter reproducibility in production, consider pinning to a specific SHA256 digest:
  ```json
  "image": "mcr.microsoft.com/devcontainers/python@sha256:..."
  ```
- **Security Note**: Base images should be periodically reviewed. Consider using Dependabot or Renovate to monitor base image updates and security patches.

### Features

- **Docker-in-Docker**: Required for building container images inside the dev container
  - **Security Note**: Docker-in-Docker (DinD) runs with elevated privileges and increases attack surface. Only use when strictly necessary (e.g., CI/CD simulation).
  - **Alternative**: Consider Docker-outside-Docker (DooD) by mounting the host Docker socket for better security:
    ```json
    "mounts": [
      "source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"
    ]
    ```
    Note: DooD still has security implications and should be used with trusted codebases only.
- **GitHub CLI**: Useful for PR operations and repository management

## Usage

1. Open the project in VS Code
2. When prompted, click "Reopen in Container"
3. The container will automatically:
   - Install Python dependencies
   - Set up the virtual environment
   - Configure VS Code settings

### Platform Compatibility

- **Linux/macOS/Windows (WSL2)**: Fully supported
- **Apple Silicon (ARM64)**: Supported if base image supports `linux/arm64`. May need `--platform linux/arm64` in Docker settings
- **Windows without WSL2**: Not supported; WSL2 is required for Docker and shell scripts

## Troubleshooting

### Setup Script Fails

If `setup.sh` fails:
- Check logs: `/tmp/devcontainer-setup.log`
- Verify `requirements.txt` exists
- Ensure network connectivity for pip installs
- **Recovery**: Open the container terminal manually and run:
  ```bash
  .devcontainer/setup.sh postCreate
  ```
  This will show detailed error output

### Clear Cache and Retry

Sometimes corrupted Docker layers cause failures:
```bash
docker system prune -a --volumes
```
Then reopen the container. **Warning**: This removes all unused Docker resources.

### Container Won't Start

- Verify JSON syntax: `python3 -m json.tool .devcontainer/devcontainer.json`
- Check Docker has sufficient resources (4GB RAM, 2 CPUs)
- Review VS Code Dev Container logs

### Timeout Issues

If setup takes longer than 5 minutes:
- Check network connectivity
- Review dependency installation logs
- Consider increasing timeout if needed (not recommended)

## Configuration Example

Minimal `devcontainer.json` structure:

```json
{
  "name": "AMAS Development Environment",
  "version": "0.1.0",
  "image": "mcr.microsoft.com/devcontainers/python:1-3.11-bullseye",
  "runArgs": ["--memory=4g", "--cpus=2"],
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "charliermarsh.ruff",
        "redhat.vscode-yaml",
        "github.vscode-pull-request-github"
      ]
    }
  },
  "onCreateCommand": ".devcontainer/setup.sh onCreate",
  "postCreateCommand": ".devcontainer/setup.sh postCreate",
  "remoteUser": "vscode",
  "workspaceFolder": "/workspaces/${localWorkspaceFolderBasename}",
  "mounts": [
    "source=amas-pip-cache,target=/home/vscode/.cache/pip,type=volume"
  ]
}
```

## Customization

You can override settings locally by modifying `.devcontainer/devcontainer.json`:

### Example: Increase Memory Allocation
```json
{
  "runArgs": [
    "--memory=8g",
    "--cpus=4"
  ]
}
```

### Example: Add Additional Ports
```json
{
  "forwardPorts": [8000, 8080, 5432],
  "portsAttributes": {
    "5432": {
      "label": "PostgreSQL",
      "onAutoForward": "notify"
    }
  }
}
```

### Example: Add Environment Variables
```json
{
  "remoteEnv": {
    "CUSTOM_VAR": "value"
  }
}
```

## Best Practices

1. **Keep `setup.sh` simple**: It should be idempotent and handle errors gracefully
2. **Review changes**: Always review `setup.sh` changes in PRs before merging (security consideration)
3. **Update dependencies**: Regularly update `requirements.txt` and `requirements-dev.txt`
4. **Monitor resource usage**: Adjust `runArgs` if your system has limited resources
5. **For large projects**: Consider increasing memory to 6-8GB and CPUs to 4 cores for better performance with type checking and parallel test execution

### Environment Files

- **`.env.example`**: Template file committed to version control. Should contain placeholder values (not real secrets).
- **`.env`**: Created from `.env.example` during `onCreateCommand`. Contains actual secrets and should **never** be committed to version control.
- **`.gitignore`**: Ensure `.env` is in `.gitignore` to prevent accidental commits of secrets.

Example `.env.example`:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```
