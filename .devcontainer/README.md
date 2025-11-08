# AMAS Development Container (PR #235 Scope Only)

This guide describes only the devcontainer and onboarding changes introduced by [PR #235](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/pull/235) for improved production readiness and developer onboarding.

---

## 🐳 Quick Start: VS Code Dev Container

1. **Clone the repository**
   ```bash
   git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
   cd Advanced-Multi-Agent-Intelligence-System
   ```
2. **Open with VS Code**
   - Run: `code .`
   - Accept "Reopen in Container" when prompted
3. **Wait for Startup**
   - Installs all dependencies
   - Python 3.11+
   - Preconfigured tools/extensions

---

## 🛠️ Configuration Details

- Pip installs run as a single consolidated command for speed/caching
- Docker-in-Docker option for local container builds (not for production)
- No deprecated or obsolete VS Code extensions
- Security recommendations/best practices for privilege separation
- All sensitive config/environment handled externally – nothing hardcoded

---

## 🧑‍💻 Typical Tasks

- Run checks: 
    ```bash
    python --version
    pip list
    python scripts/validate_env.py --mode basic --verbose
    pytest tests/ -v
    bandit -r src/
    ```
- Update requirements: 
    ```bash
    pip install -r requirements.txt
    ```
- Rebuild: Use VS Code Command Palette > "Dev Containers: Rebuild Container"

---

**For additional onboarding, refer to the updated PHASE_6_IMPROVEMENTS.md. Docs for all other features/integrations will land with their respective PRs in the future.**
