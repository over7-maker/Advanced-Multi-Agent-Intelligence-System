# AMAS Development Container

This directory contains the Dev Container configuration for the AMAS project.

---

## Purpose

The Dev Container provides a consistent, reproducible development environment with:
- Python 3.11 on Debian Bullseye
- Pre-configured VS Code extensions (Python, Ruff, YAML, GitHub Pull Requests and Issues, Docker)
  - These extensions are recommended in `.vscode/extensions.json` and will be suggested when opening the workspace
- Docker-in-Docker support for containerized builds
- GitHub CLI for repository operations
- Automated dependency installation and setup

---

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
   cd Advanced-Multi-Agent-Intelligence-System
   ```
2. **Open with VS Code**
   - Run: `code .`
   - Accept "Reopen in Container" when prompted
3. **Wait for Container Startup**
   - Installs all dependencies automatically
4. **Validate Environment in Container Terminal:**
   ```bash
   python --version     # Should be 3.11+
pip list              # All required packages
python scripts/validate_env.py --mode basic --verbose
pytest tests/ -v
bandit -r src/
   ```

---

## Configuration and Customization

- **Pip install**: Per PR #235, all requirements are installed in a single command for speed/caching.
- **Docker-in-Docker**: Available for simulating build/test pipelines (do not use in production).
- **Resource allocation**: Default 4GB RAM, 2 CPUs, can be tuned in `devcontainer.json`.
- **.env Management**: No secrets or API keys hardcoded; use `.env` (copied automatically from `.env.example`). Ensure `.env` is in `.gitignore`.
- **Timeouts**: Setup scripts and dependency installs default to a 5-minute timeout to avoid hangs.

### Pre-installed Extensions
- Python (ms-python.python)
- Ruff (charliermarsh.ruff)
- YAML (redhat.vscode-yaml)
- GitHub Pull Requests and Issues (github.vscode-pull-request-github)
- Docker support

---

## Security Guidance
- Dev Container runs as non-root `vscode` user by default
- All scripts and dependencies are reviewed before execution
- Use only `.env.example` template as a safe baseline; never commit actual secrets
- Docker-in-Docker is for trusted, local dev and CI use only

---

## Troubleshooting
- **Container won't start**: Check for syntax errors in `devcontainer.json` and if you have enough system memory/CPU
- **Dependency install errors**: Confirm network access and that `requirements.txt` is present
- **Setup timeout**: If setup takes longer than 5 minutes, check network speed and pip output logs
- **Reset/Rebuild Dev Container**: Use "Dev Containers: Rebuild Container" from VS Code command palette
- **Clear Docker caches if needed**:
  ```bash
  docker system prune -a --volumes
  ```

---

## ⚡ PR #235: Production Readiness Changes
This section details improvements made in [PR #235](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/pull/235):

- **Single-pass pip install**: Requirements and dev requirements installed together for faster spins, fewer conflicts
- **No deprecated extensions**: Clean, relevant extension set for Python/AI workflows
- **Improved error handling**: Hardened setup scripts with defensive programming and timeouts
- **Security best practices reminded**: No hardcoded secrets; runs as non-root; `.env` templates enforced
- **Docs improved**: Onboarding and quick start clarified to match real developer flow

All enhancements are now part of the standard dev container setup described above.

---

**Future changes and docs for other features will be introduced in their own PRs following the same onboarding/quality principles.**
