# AMAS Development Container

This dev container ensures any developer or CI uses a **reproducible, isolated Python 3.11 (+ Docker, VS Code, GitHub CLI) setup** for the Advanced Multi-Agent Intelligence System project.

---

## Prerequisites
- **Docker Desktop** 4.20+ (or Docker Engine 24.0+)
- **VS Code** 1.85+ with [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) v0.275+

---

## Quick Start Checklist
1. `git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git`
2. `cd Advanced-Multi-Agent-Intelligence-System`
3. `chmod +x .devcontainer/setup.sh`
4. Open folder in VS Code → F1 > "Dev Containers: Reopen in Container"
5. Wait for container to build, dependencies to install (see terminal output)
6. **Verify setup:**
   - `python --version`  (should show Python 3.11.x)
   - `ruff --version`    (should run without error)
   - `docker ps`         (should not require sudo)
   - `pytest tests/ -v`  (should pass)
   - `bandit -r src/`    (should pass)

---

## Required Files / Setup Instructions
| File | Purpose |
|------|---------|
| `.devcontainer/devcontainer.json` | Main config (image, extensions, resources, lifecycle commands) |
| `.devcontainer/setup.sh` | Lifecycle script. Must be executable/handle args as contract below |
| `.env.example` | Safe environment variable template |
| `.env` | (local only!) Site/dev/CI secrets—must never be committed |

### `setup.sh` Lifecycle Arguments
- Must be executable:
  ```bash
  chmod +x .devcontainer/setup.sh
  ```
- Required arg interface:
  - `onCreate`: Copy `.env.example`→ `.env` if `.env` missing (optional init)
  - `postCreate`: Install all dependencies (required step, fails container if error)
  - `updateContent`: (optional) Rebuild step for config/source update
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

---

## Lifecycle Commands (and what can fail)
- `initializeCommand`: Run once on build (fail fast, e.g. check tools)
- `onCreateCommand`: Setup/init after build (warn if missing, skip ok)
- `postCreateCommand`: **Required** dependency install after build (*hard fail if errors!*)
- `updateContentCommand`: Reinstall on file/config diff (strict fail, optional)

---

## Security Best Practices
- `.env` must never be committed, should always be in `.gitignore`.
- Use `.env.example` for public config.
- **Docker-in-Docker (DinD):**
  > ⚠️ DinD enables nested Docker builds (for CI/test), but increases container escape/privilege risks. _Only enable if strictly needed_; never use in prod or untrusted environments. [See Docker daemon security risks](https://docs.docker.com/engine/security/#docker-daemon-attack-surface)
- Never hardcode secrets in `setup.sh` or Dockerfiles—use safe secret or environment injection for dev/CI.

---

## Performance Recommendations
- Enable pip cache in devcontainer.json:
  ```json
  "mounts": ["source=amas-pip-cache,target=/home/vscode/.cache/pip,type=volume"]
  ```
- (Optional) Use [Dev Containers pre-built features](https://containers.dev/features) for Python/Docker/CLI speed.
- If reinstall is slow, consider splitting base/dev requirements for Dockerfile layer caching.

---

## Troubleshooting
- **setup.sh fails:** Check file is present + executable (`chmod +x`).
- **Container build fails:** Inspect postCreate logs—most errors are from pip/network issues or missing `.env`.
- **Dependency install slow:** Prune Docker (`docker system prune -a --volumes`) or rebuild.
- **VS Code won’t prompt/reopen in container:** Make sure Dev Containers extension is enabled, Docker is running, and you’re opening a folder, not a file.

---

## Extension Recommendations
- Python (ms-python.python)
- Ruff (charliermarsh.ruff)
- YAML (redhat.vscode-yaml)
- Docker (ms-azuretools.vscode-docker)
- GitHub PRs (github.vscode-pull-request-github)

VS Code will auto-suggest these via `.vscode/extensions.json` on open.

---

## Appendix: PR #235 Impact
- Unified dependency, extension, and lifecycle setup for all contributors and CIs
- Explicit error/failure contract: container build fails if onboarding breaks
- Security best practice warnings and `.env` handling
- Clear troubleshooting and recommended fastest dev branch setup

---