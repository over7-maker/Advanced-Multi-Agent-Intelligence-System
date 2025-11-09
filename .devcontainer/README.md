# AMAS Development Container

This directory provides a robust, reproducible development environment for the Advanced Multi-Agent Intelligence System (AMAS) project.

## Purpose

- Ensures every developer, contributor, and CI pipeline runs in an identical Python 3.11/Linux environment
- Pre-configures core VS Code extensions for Python/AI workflows (see below)
- Supports Docker-in-Docker for containerized build/test (dev/test only)
- Automates dependency installation, secrets handling, and workspace setup

## VS Code Extensions (.vscode/extensions.json)

This file lists recommended extensions for the repo. VS Code will suggest them automatically when you open the workspace.
- **Python:** Language support/formatting/testing
- **Ruff:** Fast Python linting/fixing
- **YAML:** Structured config/validation
- **GitHub PRs & Issues:** In-editor PR code review & GitHub integration
- **Docker:** Container workflow management

## Required Files

- **`.devcontainer/devcontainer.json`:** Main devcontainer configuration (image, mounts, features, lifecycle commands)
- **`.devcontainer/setup.sh`:** Setup script for lifecycle commands, must be executable (`chmod +x .devcontainer/setup.sh`)

### Template for `setup.sh`:
```bash
#!/bin/bash
set -e

case "$1" in
  onCreate)
    # Optional: create .env from template if not present
    [ -f .env ] || cp .env.example .env || echo "No .env.example found; skipping"
    ;;
  postCreate)
    # Install dependencies
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt -r requirements-dev.txt
    ;;
  updateContent)
    pip install -r requirements.txt -r requirements-dev.txt
    ;;
esac
```

## Lifecycle Commands

Your devcontainer.json should contain these to guarantee smooth startup:
- **`onCreateCommand`:** Optional one-time setup after container build`
- **`postCreateCommand`:** Required step; installs all dependencies, sets up linting/test tools
- **`updateContentCommand`:** Reapplies dependency install if files/branches change
- **`lifecycleTimeout`:** Optional. Set to 600 (seconds) if installs are slow for you

Each command ensures:
- **Reproducibility:** One-click dev env for all
- **Security:** No root-level setup, no global Python pollution
- **Efficiency:** Uses pip caching and Docker layer optimizations

## Security Best Practices

- Only use Docker-in-Docker for local CI simulation and development
- Never run this devcontainer config in untrusted environments or production
- All `setup.sh` changes should be code reviewed
- Use `.env.example` for placeholders, real secrets only in `.env` (never committed)
- Mounts only what the workspace/project requires, never sensitive user dirs

## Performance Considerations

- **Resource Management:** The default is 4GB RAM, 2 CPUs, can be tuned with `runArgs` in devcontainer.json
- **Timeouts:** pip installs and scripts usually finish within 5 minutes; if not, review setup logs or adjust `lifecycleTimeout` to 600 (max recommended for onboarding)
- **Pip Caching:** By default leverages volume mounts for faster repeat installs:
  ```json
  "mounts": ["source=amas-pip-cache,target=/home/vscode/.cache/pip,type=volume"]
  ```
- **Image updates:** Use Dependabot, Renovate, or other tools to monitor for Python/OS security updates

## Troubleshooting

- **VS Code doesn't prompt/reopen in container:** Use "Dev Containers: Reopen in Container" from command palette
- **Setup script fails:** Check `.devcontainer/setup.sh` is executable and not missing steps
- **Dependencies stall:** Try `docker system prune -a --volumes`, or check for network/firewall issues
- **Slow builds:** Increase resource allocation, use pre-built Dockerfile base, minimize context
- **Secret errors:** Confirm `.env` present and not empty (and not committed!)

## Minimal `devcontainer.json` Example
```json
{
  "name": "AMAS Development Environment",
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
  "lifecycleTimeout": 600,
  "remoteUser": "vscode",
  "mounts": ["source=amas-pip-cache,target=/home/vscode/.cache/pip,type=volume"]
}
```

## 🛡️ Security notes on Docker-in-Docker

Docker-in-Docker (DinD) makes it possible to run docker containers _inside_ the devcontainer for CI simulation or microservice composition. This is powerful but also increases the risk of privilege escalation, so:
- Never expose the dind socket or docker group to untrusted code
- Only use DinD for development/testing; never deploy containers built in DinD direct to production
- If you want safer multi-container workflows, consider Docker-from-Docker (mounting the host socket) in trusted, locked-down environments only

## Environment file workflow

- Use `.env.example` for templates, `.env` for actual local values (never committed)
- Always ensure `.env` is in `.gitignore`
- Validate with `python scripts/validate_env.py --mode basic --verbose`

## Appendix: PR #235 (Production Readiness) Improvements

- All dependencies now installed in a single pip command for speed and consistency
- Extension recommendations cleaned of deprecated/unused extras
- Lifecycle commands in `devcontainer.json` and `setup.sh` now enforce timeouts and robust error handling
- `.env.example` and security checks fully documented and tested
- This onboarding doc refined and clarified for all contributors

All contributors MUST update their forks/workspaces to match these standards for guaranteed compatibility.
