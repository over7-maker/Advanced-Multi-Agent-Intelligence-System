# AMAS Development Container

## Overview
This dev container provides a **reproducible, CI-compliant, and secure** Python 3.11 development environment for AMAS, standardized onboarding for all contributors, and robust automation for modern workflows.

---

## Prerequisites
- **Docker Desktop** (or Docker Engine, latest version)
- **VS Code** with [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

---

## Quick Start
1. **Clone repo & set script permissions**:
   ```bash
   git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
   cd Advanced-Multi-Agent-Intelligence-System
   chmod +x .devcontainer/setup.sh
   ```
2. **Open in VS Code** → "Reopen in Container" at prompt
3. **Wait for install** (all Python dependencies, linters, tools auto-installed)
4. **Verify setup & test**:
   ```bash
   python --version
   pip list
   pytest tests/ -v
   bandit -r src/
   ```

For more info, see [VS Code Dev Containers documentation](https://code.visualstudio.com/docs/devcontainers/containers).

---

## Setup Requirements
- `.devcontainer/devcontainer.json`: Main configuration (image, features, lifecycle commands)
- `.devcontainer/setup.sh`: Lifecycle script (must be executable, see below)

#### `setup.sh` Requirements
- Accepts these arguments:
  - `onCreate`: (Optional) Initializes, e.g., `.env` from `.env.example` if absent
  - `postCreate`: (Required) Installs all dependencies. **Container fails if this step errors!**
  - `updateContent`: (Optional) Handles updates/reinstalls if config changes
- Example:
```bash
#!/bin/bash
set -e
case "$1" in
  onCreate)
    [ -f .env ] || cp .env.example .env 2>/dev/null || echo 'No .env.example found; skipping'
    ;;
  postCreate|updateContent)
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt -r requirements-dev.txt
    ;;
  *)
    echo "Unknown command: $1" >&2; exit 1
    ;;
esac
```
- Must handle repeated/rerun calls (idempotent). If setup.sh fails, container build will hard fail. Check VS Code terminal logs.

---

## Lifecycle Commands & Failure Modes
| Command              | When Runs            | Effect/Error Handling         |
|----------------------|---------------------|------------------------------|
| initializeCommand    | Before build        | Optional, fail-fast, blocks build |
| onCreateCommand      | Once after build    | Warns if missing/skipped     |
| postCreateCommand    | Always post-build   | **Hard fail** if script errors    |
| updateContentCommand | On file/config diff | Optional, otherwise strict fail |

- **Critical:** `postCreateCommand` must never be skipped—if setup.sh is missing/broken, container cannot be created.

---

## Security Notes
> ⚠️ **Security:** `.env` must never be committed, and always placed in `.gitignore`.
> ⚠️ **Docker-in-Docker (DinD):** Increases privilege risk. Enable only for trusted, local CI/dev. [Read Docker Daemon attack surface](https://docs.docker.com/engine/security/#docker-daemon-attack-surface)

---

## Performance & Troubleshooting
- **Use pip cache mounts:**
  ```json
  "mounts": ["source=amas-pip-cache,target=/home/vscode/.cache/pip,type=volume"]
  ```
- Rebuild in VS Code if requirements/config change.
- For dependency install issues: run `docker system prune -a --volumes`
- If setup.sh or `postCreateCommand` fails, inspect terminal logs and CI output for error root-cause.
- For persistent issues: Open an issue and attach logs.

---

## Recommended VS Code Extensions
- Python (ms-python.python)
- Ruff (charliermarsh.ruff)
- YAML (redhat.vscode-yaml)
- GitHub PRs (github.vscode-pull-request-github)
- Docker (ms-azuretools.vscode-docker)

---

## Appendix: PR #235 Production Readiness Impact
After PR #235:
- Unified single-step dependency install (pip)
- Lifecycle scripts & containers are code-auditable, explicit, reproducible, and secure
- Docker-in-Docker security is documented
- All onboarding content is now fully up to date with security, failure, and troubleshooting best practices

---