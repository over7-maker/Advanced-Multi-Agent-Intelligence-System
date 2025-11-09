# AMAS Development Container

This directory provides a **consistent and isolated development environment** for the Advanced Multi-Agent Intelligence System (AMAS) project.

---

## Quick Start Checklist
1. **Clone the repository:**
   ```bash
   git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
   cd Advanced-Multi-Agent-Intelligence-System
   ```
2. **Open with VS Code:**
   - Run: `code .`
   - Accept "Reopen in Container" when prompted
3. **Wait for setup:**
   - Dev Container will auto-install Python dependencies and configure your environment
4. **Validate everything works:**
   ```bash
   python --version  # (should be 3.11+)
pip list            # all dependencies installed
python scripts/validate_env.py --mode basic --verbose
pytest tests/ -v
bandit -r src/
   ```

For more info: [VS Code Dev Containers Documentation](https://code.visualstudio.com/docs/devcontainers/containers)

---

## VS Code Extensions
This project recommends a set of VS Code extensions for the best developer experience. **.vscode/extensions.json** makes VS Code prompt you to install:
- **Python** (`ms-python.python`): Python language, linting, testing
- **Ruff** (`charliermarsh.ruff`): Fast code linter/fixer
- **YAML** (`redhat.vscode-yaml`): Config schemas, linting
- **GitHub PRs & Issues** (`github.vscode-pull-request-github`): Integrated PR management
- **Docker** (`ms-azuretools.vscode-docker`): Container build/test workflow

---

## Required Files (and their role)
- **.devcontainer/devcontainer.json** - *Dev Container configuration file* (image, features, extensions, resource limits, lifecycle commands)
- **.devcontainer/setup.sh** - *Lifecycle script* for creating `.env` from `.env.example`, installing dependencies, or any custom startup logic (must be executable with `chmod +x`)

**Example template for setup.sh:**
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
esac
```

---

## Lifecycle Commands Explained
- **onCreateCommand:** One-time setup or file generation after build (usually copies .env.example)
- **postCreateCommand:** Required! Installs all dependencies and finalizes dev environment
- **updateContentCommand:** Triggers when source files/config change, re-installs dependencies to stay fresh
- **lifecycleTimeout:** Optional. Default is 300sec, increase to 600 if builds routinely run slow for you

These guarantees:
- **Fast/consistent onboarding.**
- **No global pip pollution.**
- **Run as non-root `vscode` user.**
- **All critical setup steps explicit and logged.**

---

## Security and Performance
- **Docker-in-Docker** is enabled for local multi-container dev/test but **should never be used for prod or untrusted code**
  - ⚠️ [Read why this is dangerous and the best mitigation strategies](https://docs.docker.com/engine/security/#docker-daemon-attack-surface)
- **Secrets**: Only use `.env.example` for templates. Never commit `.env` or real credentials; always add to `.gitignore`.
- **Automated scripts run as a user, not root**
- **Image, package, and extension updates** should be reviewed in PRs. Use Dependabot/Renovate for ongoing security.
- **Timeouts and resource constraints**: Defaults (4GB RAM, 2 CPU, 5-minute command timeouts) are safe for most onboarding. Can be tuned in devcontainer.json

---

## Troubleshooting & FAQ
- **Dev Container won't start?**  Check Docker Desktop is running, you have enough RAM/CPU, and devcontainer.json is valid JSON.
- **`setup.sh` errors?**  Ensure file is present and executable. Re-pull main branch if needed.
- **Dependency install fails?**  Try `docker system prune -a --volumes`, ensure network/internet ok, rerun container build.
- **Security warning: Docker-in-Docker**  Don't use on shared, sensitive, or prod systems. Disable DinD feature or use Docker-from-Docker only when fully trusted.
- **Need help?**  See [VS Code Dev Containers docs](https://code.visualstudio.com/docs/devcontainers/containers) or open an issue/discussion in the repo.

---

## Minimal devcontainer.json Example
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

---

## Appendix: PR #235 Improvements
- **Unified pip install:** Requirements and dev dependencies installed in one step
- **Modern extensions only:** Clean recommendations in .vscode/extensions.json
- **Lifecycle commands & scripts clarified, including error handling and timeouts**
- **Better security documentation:** Emphasized non-root, .env usage, no production DinD
- **All onboarding/tuning information above up to date as of PR #235**

---
