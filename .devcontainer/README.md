# AMAS Development Container

Provides a reproducible, secure Python 3.11 development environment for the Advanced Multi-Agent Intelligence System (AMAS), with automated CI-compliant workflows, best-practice onboarding, lifecycle automation, and explicit security guidance.

---

## Prerequisites
- Docker Desktop (latest, Linux/Mac/Windows w/ WSL2)
- VS Code w/ "Dev Containers" extension ([install here](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers))

---

## Quick Start Checklist
- [ ] Run: `git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git`
- [ ] Run: `chmod +x .devcontainer/setup.sh`
- [ ] Open folder in VS Code → Click "Reopen in Container" (prompted automatically)
- [ ] Wait for full install (pip, linters, tools)
- [ ] Validate environment and run:
   ```bash
   python --version
   pip list
   python scripts/validate_env.py --mode basic --verbose
   pytest tests/ -v
   bandit -r src/
   ```

---

## Required Files & Lifecycle Contracts
| File | Purpose |
|------|---------|
| `.devcontainer/devcontainer.json` | Main configuration (image, features, resources, lifecycle) |
| `.devcontainer/setup.sh` | Lifecycle script: must accept `onCreate`, `postCreate`, `updateContent`, be executable |
| `.env.example` | Safe environment variable template |
| `.env` | (local only!) Developer/CI secrets – must never be committed |

### `setup.sh` Script Contract
- Must be executable: `chmod +x .devcontainer/setup.sh`
- Must support idempotent repeated calls with these args:
  - `onCreate`: Setup or copy `.env` from `.env.example` if missing
  - `postCreate`: Full dependency install (`pip install -r requirements.txt -r requirements-dev.txt`)
  - `updateContent`: Handles workspace changes (optional)
- Example implementation:
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
- If script fails, **devcontainer build fails** (see error output for troubleshooting).

---

## Lifecycle and Expected Behavior
- `initializeCommand` (optional): Validates Docker, Python; should fail fast if prerequisites are broken
- `onCreateCommand`: One-time setup after build (`./setup.sh onCreate`); ok to skip if `.env` exists
- `postCreateCommand`: Required post-build setup; always installs full dependencies, lints, and fails container build if not successful
- `updateContentCommand`: Triggers on workspace or file change, e.g. branch switch (optional)
- `lifecycleTimeout`: Recommended `600` (10min) for slow installs; defaults to 300s otherwise

#### Example devcontainer.json lifecycle block:
```json
{
  "onCreateCommand": ".devcontainer/setup.sh onCreate",
  "postCreateCommand": ".devcontainer/setup.sh postCreate",
  "updateContentCommand": ".devcontainer/setup.sh updateContent",
  "lifecycleTimeout": 600
}
```

---

## Security Guidance
> ⚠️ **Sensitive Data:** `.env` must **ONLY** exist locally, never committed; always in `.gitignore`.
> ⚠️ **Docker-in-Docker (DinD):** Powerful but dangerous. Use **only** for local dev/CI simulation and trusted code. _Never enable on prod/privileged hosts._ See [official Docker security docs](https://docs.docker.com/engine/security/#docker-daemon-attack-surface).


---

## Performance and Optimization
- Use pip cache mounts for speed (`"mounts": ["source=amas-pip-cache,target=/home/vscode/.cache/pip,type=volume"]`)
- For large projects: split requirements files to optimize change detection/caching
- Setup commands must be idempotent — never error or duplicate work if run again
- Rebuild container from VS Code when requirements or dependencies change

---

## Troubleshooting & Error Handling
- If **devcontainer fails to build**: check logs in VS Code terminal, inspect output/errors from `setup.sh`
- Common issues: Docker not running, missing/misnamed `setup.sh`, network issues (pip)
- Use `docker system prune -a --volumes` for persistent cache/install errors (warns: will delete all unused Docker resources)
- Verify `.env` present but **never committed**

---

## Extension Recommendations (via `.vscode/extensions.json`)
- Python (ms-python.python)
- Ruff (charliermarsh.ruff)
- YAML (redhat.vscode-yaml)
- GitHub PRs (github.vscode-pull-request-github)
- Docker (ms-azuretools.vscode-docker)

VS Code will automatically suggest these on open for fast bootstrapping.

---

## Appendix: PR #235 Production Readiness Impact
- Unified single-step dependency install
- Explicit, auditable lifecycle setup contract with error-handling
- Docker-in-Docker security warnings reinforced
- All onboarding, troubleshooting, and best practices above now reflect post-PR #235 state

---