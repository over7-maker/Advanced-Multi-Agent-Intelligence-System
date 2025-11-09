# AMAS Development Container – Bulletproof Onboarding & Security Guide

---

## Purpose
Deliver a reproducible Python 3.11 + Docker + CI dev environment for the AMAS project, enabling frictionless, auditable onboarding for all engineers and bots.

---

## Prerequisites Check
- ✅ Docker Desktop 4.20+ (or Docker Engine 24.0+) is running (`docker info`)
- ✅ VS Code 1.85+ with Dev Containers extension 0.275+ (`F1` > "Dev Containers: Reopen in Container")
- ✅ `.devcontainer/devcontainer.json` exists in project root

---

## Quick Start
1. `git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git && cd Advanced-Multi-Agent-Intelligence-System`
2. Create `setup.sh` if missing (`touch .devcontainer/setup.sh`) **then** copy the script below
3. `chmod +x .devcontainer/setup.sh`
4. Open in VS Code → Press `F1` → "Dev Containers: Reopen in Container"
5. Wait for container build to complete and all dependencies to install
6. Run verification commands:
   ```bash
   python --version       # Should show 3.11.x
   docker --version       # Docker CLI in container
   ruff --version         # Linter available
   gh auth status         # GitHub CLI working
   pytest tests/ -v
   bandit -r src/
   ```

---

## Setup Script (`setup.sh`)
```
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
- **Save this as `.devcontainer/setup.sh` and run `chmod +x .devcontainer/setup.sh`**.

---

## Lifecycle Command Reference
| Command              | When Runs               | Behavior / Failure Mode                              |
|----------------------|------------------------|------------------------------------------------------|
| initializeCommand    | On build start         | Checks host/toolchain (fail-fast, optional)          |
| onCreateCommand      | After build            | Copies configs/secrets; skip ok, warn if missing     |
| postCreateCommand    | After build            | Requirement: must succeed, hard fail on error        |
| updateContentCommand | On rebuild/file change | Reinstall/install updates; hard fail on error        |

---

## 🔒 Security Considerations
- **Docker-in-Docker (DinD):** Elevated privileges. Use only for trusted dev/CI builds. Never in prod or with unknown code. [Docker Daemon security](https://docs.docker.com/engine/security/#docker-daemon-attack-surface)
- **setup.sh runs as root in container.** Only include trusted install or package commands.
- **Never commit `.env` files.** Make sure `.env` is listed in `.gitignore` and always review `.env.example` for safety.
- **Use GitHub CLI tokens with minimal scopes.** Never paste a full PAT or secret in scripts.
- **Avoid mounting sensitive host folders inside devcontainer unless required** (e.g., `~/.ssh`, `~/.aws`).

---

## ⚙️ Performance Tips
- Always install OS-level (apt) packages before Python packages for layer caching in Docker.
- Use Dockerfile + multi-stage build if performance becomes an issue for team/CI.
- Run `docker builder prune` to clean caches if space or build time grows.

---

## ✅ Verification
After full container boot, verify with:
```bash
python --version        # 3.11.x
ruff --version
docker --version
pytest tests/ -v
bandit -r src/
gh auth status
```
If any fail, review troubleshooting and setup steps above.

---

## 🛠 Troubleshooting
| Issue                              | Solution                                                      |
|------------------------------------|---------------------------------------------------------------|
| `setup.sh: Permission denied`      | `chmod +x .devcontainer/setup.sh`                             |
| Dev Container fails to build       | VS Code: Cmd Palette > 'Dev Containers: Rebuild Container'    |
| Docker not available in container  | Ensure Docker Desktop is running, integrated with WSL2 (Win)  |
| GitHub CLI not authenticated       | Run `gh auth login` in container                              |
| Dependency install slow/cache fail | Run `docker system prune -a --volumes`; re-pull latest code   |
| No `setup.sh` or incomplete config | Create/copy above, make executable; double-check `devcontainer.json` |

---

## Appendix: PR #235 Integration Summary
- Single-step setup and error-checked onboarding for all developers and CI.
- Explicit lifecycle, security, and troubleshooting best practices implemented.
- Project now ready for full review, audit, or team onboarding with zero external dependencies.

---
