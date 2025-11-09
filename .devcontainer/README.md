# AMAS Development Container

Provides a consistent, isolated Python 3.11 development environment for the AMAS project, automating setup, dependencies, and workflows via VS Code Dev Containers for all contributors.

---

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
   cd Advanced-Multi-Agent-Intelligence-System
   ```
2. **Open in VS Code:** `code .` (then click "Reopen in Container" when prompted)
3. **Wait for setup to finish** (dependencies are automatically installed)
4. **Run validation/tests:**
   ```bash
   python --version
   pip list
   python scripts/validate_env.py --mode basic --verbose
   pytest tests/ -v
   bandit -r src/
   ```

For a full overview, see [VS Code Dev Containers Documentation](https://code.visualstudio.com/docs/devcontainers/containers).

---

## Required Files

| File                                   | Purpose                                                      |
|----------------------------------------|--------------------------------------------------------------|
| `.devcontainer/devcontainer.json`      | Main Dev Container config (image, extensions, commands, etc.) |
| `.devcontainer/setup.sh`               | Lifecycle setup/install script (must be executable)           |
| `.env.example`                         | Environment variable template for secrets/config              |

### `setup.sh` script contract
- Must be executable (`chmod +x`)
- Accepts: `onCreate`, `postCreate`, `updateContent` as arguments
- Example template:
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
- Idempotency: Must not error on repeated execution

---

## Lifecycle Commands (as configured in devcontainer.json)

- **`initializeCommand`** (optional): Validate toolchain or pre-install dependencies before build
- **`onCreateCommand`**: Run once after container is created; e.g., `.devcontainer/setup.sh onCreate`. Skips safely if missing.
- **`postCreateCommand`**: _Required_; installs project dependencies; fails container build if fails
- **`updateContentCommand`**: Reruns install if core files change
- **`lifecycleTimeout`**: (default 300, recommended 600 if slow network)

Example:
```json
{
  "onCreateCommand": ".devcontainer/setup.sh onCreate",
  "postCreateCommand": ".devcontainer/setup.sh postCreate",
  "updateContentCommand": ".devcontainer/setup.sh updateContent",
  "lifecycleTimeout": 600
}
```

---

## VS Code Extensions (.vscode/extensions.json)
- Lists recommended extensions for optimal workflows; VS Code will suggest install on open.
  - Python (ms-python.python) — language/lint/test support
  - Ruff/python-ruff — fast linting/fixing
  - YAML — config validation
  - GitHub PRs — integrated review
  - Docker — manage/test containers

---

## Security Notes
- **Never commit real `.env` files.** ALWAYS use `.env.example` templates. Secrets must be loaded only via local, git-ignored `.env`.
- **Docker-in-Docker (DinD) WARNING:**
  > ⚠️ Docker-in-Docker enables advanced multi-container CI simulation, but _dramatically increases attack surface and privilege risk_. Enable only on trusted, local development machines. For more, see [Security Best Practices – Docker](https://docs.docker.com/engine/security/#docker-daemon-attack-surface).

---

## Performance & Idempotency

- **Use pip cache mounts** for faster builds:
  ```json
  "mounts": ["source=amas-pip-cache,target=/home/vscode/.cache/pip,type=volume"]
  ```
- **Layered dependency files:** Optional. For heavy dev/test requirements, split `requirements.txt`, `requirements-dev.txt` so pip only reinstalls changes.
- **setup.sh idempotency:** Must not fail or repeat work unnecessarily on rerun/rebuild.
- **Conditional install:** Advanced: Check for file hash or `.pip-installed` marker before running pip in `postCreate`.

---

## Troubleshooting / FAQ

- **Container fails to start:**
  - Check Docker Desktop is running
  - Validate `devcontainer.json` and `setup.sh` presence and permissions
- **setup.sh errors:**
  - Confirm executable bit: `chmod +x .devcontainer/setup.sh`
  - Re-pull main if missing
- **Slowness on build:**
  - Increase RAM/CPU allocation
  - Use existing cache or pre-built base image
- **Secrets warning:**
  - Validate that `.env` is present, never committed, and not empty
- **General Dev Container/hints:**
  - See the [Dev Container docs](https://code.visualstudio.com/docs/devcontainers/containers)
  - Open an issue in this repo

---

## Appendix: PR #235 (Production Readiness) Improvements

- All dependencies installed in a single unified pip command
- Modern and safe extension recommendations
- Automated, robust error-checked setup and onboarding scripts
- Lifecycle and resource usage best practices codified above
- Docker-in-Docker security clarified and emphasized
- All onboarding and doc content reviewed and improved for absolute clarity

---