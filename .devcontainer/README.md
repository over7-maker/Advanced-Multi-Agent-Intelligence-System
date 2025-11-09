# AMAS Development Container – **Full Onboarding, Security, and Troubleshooting Reference**

---

## Purpose
Provide a bulletproof, reproducible Python 3.11/Docker/CI environment for all AMAS developers and CIs — so every onboarding starts identically and securely.

---

## Prerequisites (With Version Pinning)
- **Docker Desktop** 4.20+ (or Docker Engine 24.0+)
- **VS Code** 1.85+ with [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) 0.275+

---

## Quick Start: 5-Minute Checklist
1. Clone: `git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git && cd Advanced-Multi-Agent-Intelligence-System`
2. Ensure: `chmod +x .devcontainer/setup.sh` (create `touch .devcontainer/setup.sh` if missing; copy-paste script from below)
3. Open VS Code → F1 → "Dev Containers: Reopen in Container"
4. Wait for container build, dependency/linter install (see VS Code output)
5. Verify:
   - `python --version` (Python 3.11.x)
   - `docker ps` (Docker works, no sudo)
   - `ruff --version` (extension/linter present)
   - `pytest tests/ -v`, `bandit -r src/` (tests, security scan pass)

---

## Required Files & Setup Contracts
| File | Purpose |
|------|---------|
| `.devcontainer/devcontainer.json` | Main config (image/features/lifecycle/extensions/version) |
| `.devcontainer/setup.sh` | Must be executable, accept argument: `onCreate`, `postCreate`, `updateContent`. See template below. |
| `.env.example` | Template for safe env/root secrets. Never contains real keys. |
| `.env` | Local only! Real secrets; must never be committed. Always in `.gitignore`. |

### `setup.sh` Creation & Lifecycle Contract
1. Create if missing: `touch .devcontainer/setup.sh`
2. Make executable: `chmod +x .devcontainer/setup.sh`
3. **Script contract:**
   - `onCreate`: (optional) Copies `.env.example` → `.env` if `.env` missing
   - `postCreate`: (required) Installs Python deps (hard fail if errors)
   - `updateContent`: (optional; re-run on config change)
```bash
#!/bin/bash
set -e
case "$1" in
  onCreate)
    [ -f .env ] || cp .env.example .env 2>/dev/null || echo 'No .env.example found; skipping'
    ;;
  postCreate|updateContent)
    pip install --upgrade pip setuptools wheel
    pip install --cache-dir /home/vscode/.cache/pip -r requirements.txt -r requirements-dev.txt
    ;;
  *)
    echo "Unknown command: $1" >&2; exit 1
    ;;
esac
```
- Script must NOT fail on repeated calls (idempotent)

---

## Lifecycle Commands Explained
| Command | Phase | Contract |
|---------|-------|----------|
| `initializeCommand` | On build | (optional) Validates Python 3.11+, Docker in place; fail fast if unsupported |
| `onCreateCommand` | After build | Creates/seeds base configs; warns/silently skips if missing |
| `postCreateCommand` | End of build | Always run, hard fail if script/dep error occurs |
| `updateContentCommand` | On config/source change | Freshens install; hard error on fail  |

---

## Security – Never skip!
- **.env is never to be committed**: ALWAYS add to `.gitignore`, confirm by running `git status` after setup
- **Use `.env.example`** for safe placeholder values
- **Never hardcode secrets**, passwords, or tokens in scripts or Dockerfiles
- **Docker-in-Docker WARNING:**
  > ⚠️ Using DinD exposes host Docker. Only use in trusted/CI situations. [Details here.](https://docs.docker.com/engine/security/#docker-daemon-attack-surface)

---

## Performance & Dependency Optimization
- Use persistent pip cache mount in devcontainer:
  ```json
  "mounts": ["source=amas-pip-cache,target=/home/vscode/.cache/pip,type=volume"]
  ```
- (Optional) Use Dockerfile for base deps if iterating on heavy requirements
- Split prod/dev dependency files for Docker layer optimization
- Pin container images:
  ```json
  "image": "mcr.microsoft.com/devcontainers/python:0.269.0-3.11-bullseye"
  ```
  – Update versions with Dependabot.

---

## Troubleshooting
- **setup.sh permission denied**: `chmod +x .devcontainer/setup.sh`
- **Container build fails**: Review logs for pip errors; confirm Docker Desktop is running
- **Dependency reinstall slow**: Prune docker cache: `docker system prune -a --volumes`
- **VS Code Dev Container fails**: Confirm correct extension, Docker version, and folder open
- **Secrets error**: Check `.env` exists (never committed)
- **Dev container hooks not running**: Confirm command in `devcontainer.json` matches contract above

---

## VS Code Extensions & Feature Flow
- Python (ms-python.python)
- Ruff (charliermarsh.ruff)
- YAML (redhat.vscode-yaml)
- Docker (ms-azuretools.vscode-docker)
- GitHub PRs (github.vscode-pull-request-github)
-- Will be auto-suggested by VS Code on open

---

## Appendix: PR #235 Modernization Impact
- Implements single-step, auditable onboarding flow
- Pin images & dependencies for CI/modern multi-dev reproducibility
- Security, troubleshooting, and cloud CI/dev sequence all clarified, contractually enforceable, and bulletproofed
- All onboarding, dev, and CI failures now 0-surprise, with explicit recovery guidance

---
