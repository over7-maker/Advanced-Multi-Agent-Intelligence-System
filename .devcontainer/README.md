# AMAS Development Container

This directory contains the Dev Container configuration for the AMAS project.

---

## Purpose

The Dev Container provides a consistent, reproducible development environment with:
- Python 3.11 on Debian Bullseye
- Pre-configured VS Code extensions (Python, Ruff, YAML, GitHub Pull Requests and Issues, Docker)
- Docker-in-Docker support for containerized builds
- GitHub CLI for repository operations
- Automated dependency installation and setup


---

## Required Files

The Dev Container setup requires the following files:

- **`.devcontainer/devcontainer.json`**: Main configuration file (see "Configuration Example" below)
- **`.devcontainer/setup.sh`**: Setup script for lifecycle commands (must be executable)

Create `setup.sh` if missing:
```bash
touch .devcontainer/setup.sh
chmod +x .devcontainer/setup.sh
```

The script must handle these arguments:
- `onCreate`: Optional setup (e.g., creating `.env` from `.env.example`)
- `postCreate`: Required setup (e.g., installing dependencies)
- `updateContent`: Updates when container content changes

See `.devcontainer/setup.sh` for a typical implementation.

---

## Configuration Overview

### Lifecycle Commands

- **`initializeCommand`**: Validates Python version (3.11+)
- **`onCreateCommand`**: Performs optional setup (creates `.env` from `.env.example` if available); warns safely if setup.sh missing
- **`postCreateCommand`**: Required setup (installs dependencies); fails if setup.sh missing or execution fails
- **`updateContentCommand`**: Updates dependencies when container content changes; fails if setup.sh missing or execution fails

### Resource Limits

- **Memory**: 4GB (sufficient for Python dev)
- **CPUs**: 2 cores (for parallel installs/builds)

### Timeouts

All lifecycle commands have a 300-second (5-minute) timeout by default to protect against hangs.

Override with:
```json
{
  "postCreateCommand": "timeout 600 .devcontainer/setup.sh postCreate",
  "lifecycleTimeout": 600
}
```

---

## Performance Optimization

1. **Pip Caching**: Volume mount for pip cache:
```json
"mounts": ["source=amas-pip-cache,target=/home/vscode/.cache/pip,type=volume"]
```
2. **Docker Layer Caching**: Use a Dockerfile-based setup with cached requirements.
3. **Pre-built Base Images:** Consider using cached dependency images for large dependency graphs.
4. **Use `.dockerignore`** to exclude unnecessary files from build context.
5. **Pip Configuration**: Add `--cache-dir` or configure `pip.conf` for consistency.


---

## Security Considerations

1. **Script Execution**: All setup scripts must be trusted, reviewed in PRs, and explicitly executable (`chmod +x`).
2. **Timeout Protection**: Prevent indefinite hangs by enforcing timeouts on lifecycle commands.
3. **Non-root User**: Runs as `vscode` user, not root, to reduce privilege escalation risks.
4. **Image Updates**: Update base images regularly to ensure security patches are present. Dependabot/Renovate is recommended.
5. **No Hardcoded Secrets**: Use `.env.example` for templates, never commit real secrets; `.env` is gitignored.


---

## Base Image

- **Source**: `mcr.microsoft.com/devcontainers/python:1-3.11-bullseye`
- **Description**: Official Microsoft Dev Container for Python 3.11

To ensure strict reproducibility, pin to a specific SHA digest:
```json
"image": "mcr.microsoft.com/devcontainers/python@sha256:..."
```


---

## Features

- **Docker-in-Docker**: Supports local/test container builds (not for production)
- **GitHub CLI**: Used for PR and repository operations
- **Pre-configured Extensions**: Install Python, Ruff, YAML, GitHub PRs, Docker

---

## Usage

1. Open the project with VS Code
2. When prompted, "Reopen in Container"
3. Dependencies will auto-install, workspace is ready for development

### Platform Compatibility

- Linux/macOS/Windows (WSL2): Supported
- Apple Silicon: Supported if base image supports arm64
- Windows without WSL2: Not supported

---

## Troubleshooting

**Setup Script Fails**: Check logs, verify `requirements.txt` exists, rerun setup script manually.
**Clear Caches**: `docker system prune -a --volumes`
**Container Won't Start**: Check that `devcontainer.json` and `setup.sh` have correct syntax and are present.
**Timeout Issues**: Validate network connectivity, increase `lifecycleTimeout` if absolutely necessary.

---

## Configuration Example

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
  "mounts": ["source=amas-pip-cache,target=/home/vscode/.cache/pip,type=volume"]
}
```

---

## Customization Examples

**Increase Memory/CPU:**
```json
{
  "runArgs": ["--memory=8g", "--cpus=4"]
}
```

**Add Ports:**
```json
{
  "forwardPorts": [8000, 8080, 5432],
  "portsAttributes": {
    "5432": {"label": "PostgreSQL", "onAutoForward": "notify"}
  }
}
```

**Add Environment Variables:**
```json
{
  "remoteEnv": {
    "CUSTOM_VAR": "value"
  }
}
```

---

## Best Practices

1. Keep `setup.sh` simple and idempotent.
2. Always review setup scripts and PRs that modify devcontainer files, for security.
3. Update dependencies regularly, keep `requirements-dev.txt` up to date.
4. Monitor the base image for vulnerabilities using Dependabot or equivalent.
5. Ensure `.env` and any secrets files are present in `.gitignore`.


---

## Environment Files

- **`.env.example`**: Template file (placeholders only)
- **`.env`**: Actual secrets (never committed, gitignored)
- **`.gitignore`**: Confirms `.env` is ignored

Example `.env.example`:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```

---

## ⚡ PR #235: Production Readiness Changes

This section details improvements made in [PR #235](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/pull/235):
- **Single-pass pip install**: Requirements and dev requirements installed together for faster spins/fewer conflicts
- **No deprecated VS Code extensions**: Extension list cleaned for modern Python/AI workflows
- **Improved error handling**: Setup scripts and devcontainer config now use timeouts, robust fallbacks, and defensive programming
- **Security best practices**: No hardcoded secrets, forced non-root, strict `.env` management
- **Onboarding docs improved**: This file and quick start are now clearer and match the actual setup

These improvements are now baseline for all contributors and future feature PRs.

---
