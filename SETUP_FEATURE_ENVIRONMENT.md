# Feature Development Environment Setup

**Purpose**: Complete guide for setting up the development environment to work on feature branches  
**Target Audience**: Developers working on feature PRs (#237-#242)  
**Prerequisites**: Git, Docker, VS Code

---

## 📋 Quick Setup (5 minutes)

### Step 1: Clone Repository
```bash
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System
```

### Step 2: Open in VS Code with Dev Container
```bash
# Open VS Code in current directory
code .

# When prompted: "Reopen in Container"
# Click "Reopen in Container" button

# Wait for container to build (~2-3 minutes on first run)
```

### Step 3: Verify Environment
```bash
# Inside dev container terminal:
python --version     # Should be 3.11+
pip list | grep amas # Should show amas packages

# Validate configuration
python scripts/validate_env.py --mode basic --verbose
```

### Step 4: Create Feature Branch
```bash
# From main or develop
git checkout main
git pull origin main

# Create feature branch (use one of the patterns below)
git checkout -b feature/security-layer         # For PR #238
git checkout -b feature/observability-slo      # For PR #239
git checkout -b feature/agent-contracts        # For PR #237
git checkout -b feature/progressive-delivery   # For PR #240
git checkout -b feature/performance-scaling    # For PR #241
git checkout -b feature/data-governance        # For PR #242
```

---

## 🔧 Complete Setup Guide

### System Requirements
| Component | Requirement | Recommended |
|-----------|-------------|-------------|
| OS | Linux, macOS, Windows (WSL2) | Linux preferred |
| Docker | v20.10+ | v24.0+ |
| VS Code | v1.80+ | Latest |
| RAM | 4GB minimum | 8GB+ |
| Disk | 10GB free | 20GB free |

### Installation Steps

#### 1. Install Dependencies

**macOS**:
```bash
# Install Docker Desktop
brew install docker-desktop

# Install VS Code
brew install visual-studio-code

# Install Dev Container CLI (optional but recommended)
brew install devcontainers
```

**Linux (Ubuntu/Debian)**:
```bash
# Install Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose-plugin
sudo usermod -aG docker $USER

# Install VS Code
sudo apt-get install code

# Install Dev Container CLI (optional)
curl -fsSL https://get.docker.com -o get-docker.sh | sh
```

**Windows (WSL2)**:
```powershell
# Install Docker Desktop for Windows
choco install docker-desktop

# Install VS Code
choco install vscode

# Ensure WSL2 backend in Docker settings
```

#### 2. Clone Repository
```bash
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System
```

#### 3. Install VS Code Extensions

**Required**:
- Remote - Containers (ms-vscode-remote.remote-containers)
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)

**Install via Command Palette** (Ctrl/Cmd + Shift + P):
```
> Extensions: Install Extensions
ms-vscode-remote.remote-containers
ms-python.python
ms-python.vscode-pylance
```

Or via CLI:
```bash
code --install-extension ms-vscode-remote.remote-containers
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
```

#### 4. Open Project in Dev Container
```bash
code .

# Command Palette (Ctrl/Cmd + Shift + P)
> Remote-Containers: Reopen in Container
```

#### 5: Wait for Container Build

**First Time** (~2-3 minutes):
- Pulls base image: `mcr.microsoft.com/devcontainers/python:1-3.11-bullseye`
- Installs dependencies from `requirements.txt` and `requirements-dev.txt`
- Configures Python environment
- Sets up Git configuration

**Subsequent Times** (~10-30 seconds):
- Uses cached layers
- Quick startup

#### 6: Verify Setup

```bash
# Open integrated terminal in VS Code (Ctrl/Cmd + `)

# Check Python
python --version
# Output: Python 3.11.x

# Check pip packages
pip list | head -20

# Verify AMAS installation
python -c "import amas; print(amas.__version__)"

# Validate environment
python scripts/validate_env.py --mode basic --verbose

# Run tests
pytest tests/ -v --tb=short
```

---

## 🚀 Working with Feature Branches

### Creating a Feature Branch

```bash
# Ensure main is up to date
git checkout main
git pull origin main

# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Push branch to GitHub (creates PR template)
git push -u origin feature/your-feature-name
```

### Development Workflow

```bash
# 1. Make changes
vi src/amas/your_module.py

# 2. Run linting
black src/
flake8 src/
ruff check src/ --fix

# 3. Run type checking
mypy src/

# 4. Run tests (if available)
pytest tests/ -v

# 5. Commit changes
git add src/amas/your_module.py
git commit -m "feat: add your feature"

# 6. Push to GitHub
git push origin feature/your-feature-name

# 7. Create Pull Request
# GitHub will prompt to create PR
```

### Testing Locally Before Push

```bash
# Run all quality checks
make lint      # Or: black . && flake8 . && ruff check .
mypy src/
pytest tests/ -v --cov=src --cov-report=html

# Check output
lsb_release -a  # Linux
uname -a       # macOS

# View coverage report
python -m http.server --directory=htmlcov 8000
# Open http://localhost:8000 in browser
```

### Creating Pull Request

```bash
# After pushing, go to GitHub
# https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System

# Click "Compare & pull request"

# Fill in PR details:
# - Title: feat: add your feature description
# - Description: Explain what your feature does
# - Link issues: Fixes #XXX (if applicable)
# - Add labels: feature, phase-X

# Create PR

# GitHub Actions will:
# 1. Run code quality checks
# 2. Run security scans
# 3. Run bulletproof AI analysis
# 4. Collect metrics
# 5. Generate reports
```

---

## 🔠 Environment Configuration

### AI Provider Keys (Optional for Development)

```bash
# Inside dev container, create .env file
cat > .env <<'EOF'
# At least one provider key required for AI analysis
DEEPSEEK_API_KEY=your_key
GLM_API_KEY=your_key
GROK_API_KEY=your_key

# Optional premium providers
CEREBRAS_API_KEY=your_key
NVIDIA_API_KEY=your_key
EOF

# Load environment
source .env

# Validate
python scripts/validate_env.py --mode basic --verbose
```

### Python Virtual Environment (Manual Setup)

If not using dev container:

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# OR
venv\\Scripts\\activate  # Windows

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verify
python --version
pip list
```

---

## 📊 Development Tools

### Code Formatting
```bash
# Black (code formatter)
black src/ tests/

# isort (import sorter)
isort src/ tests/

# Ruff (linter)
ruff check src/ --fix
```

### Type Checking
```bash
# MyPy (static type checker)
mypy src/

# Check specific file
mypy src/amas/your_module.py
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_router.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run with markers
pytest -m "not slow" -v  # Skip slow tests
```

### Security Scanning
```bash
# Bandit (security linter)
bandit -r src/

# Safety (dependency vulnerabilities)
safety check

# Semgrep (comprehensive code scanning)
semgrep --config=p/security-audit src/
```

---

## 👠 Troubleshooting

### Dev Container Won't Start

```bash
# Check Docker daemon
docker ps

# Rebuild container
# VS Code: "Dev Containers: Rebuild Container"

# Clear Docker resources
docker system prune -a

# Check logs
# VS Code: "Dev Containers: Show Container Log"
```

### Python Package Import Errors

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name '*.pyc' -delete

# Check Python path
python -c "import sys; print('\\n'.join(sys.path))"
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows

# Or use different port
python -m uvicorn main:app --port 8001
```

### Git Configuration Issues

```bash
# Configure Git inside container
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Generate SSH key if needed
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to GitHub
# https://github.com/settings/keys
```

---

## 🔗 CI/CD Integration

### GitHub Actions Workflow

When you push to your feature branch, GitHub automatically runs:

1. **Code Quality Checks**
   - Python syntax validation
   - Black formatting check
   - Flake8 linting
   - Ruff analysis

2. **Security Scans**
   - Bandit security check
   - Semgrep code analysis
   - Dependency vulnerability check

3. **Bulletproof AI Analysis**
   - Real AI code review
   - Security recommendations
   - Performance suggestions
   - Quality improvements

4. **Test Suite**
   - Unit tests
   - Integration tests
   - Coverage reporting

### Viewing Workflow Results

```bash
# Go to your PR on GitHub
https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/pull/YOUR_PR_NUMBER

# Scroll down to see:
# - ✅ Passing checks
# - ❌ Failed checks
# - 📊 Analysis reports
```

---

## 🎈 Best Practices

### Before Committing
- [ ] Code passes linting (`black`, `ruff`)
- [ ] Type checking passes (`mypy`)
- [ ] All tests pass (`pytest`)
- [ ] Security scan clean (`bandit`)
- [ ] No hardcoded secrets
- [ ] Documentation updated

### PR Description Template
```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## How to Test
Steps to test the changes.

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No new warnings generated
```

### Commit Message Format
```
feat: add new feature description
fix: resolve bug description
docs: update documentation
refactor: restructure code
test: add or update tests
chore: update dependencies
```

---

## 📄 Resources

- **Dev Container Docs**: `.devcontainer/README.md`
- **Project Architecture**: `docs/ARCHITECTURE.md`
- **API Reference**: `docs/API_DOCUMENTATION.md`
- **Phase 6 Improvements**: `PHASE_6_IMPROVEMENTS.md`
- **GitHub Repo**: https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System

---

## ✅ Ready to Contribute?

1. Fork the repository
2. Clone your fork
3. Create feature branch
4. Make changes
5. Push and create PR
6. Wait for CI/CD checks
7. Address review feedback
8. Merge when approved

**Estimated time to first contribution**: 15-30 minutes with this guide.

---

**Questions?** Open an issue or start a discussion on GitHub.  
**Version**: 3.0.1 | **Last Updated**: Nov 8, 2025
