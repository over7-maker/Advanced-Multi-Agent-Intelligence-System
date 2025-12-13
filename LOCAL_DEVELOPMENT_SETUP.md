# 🚀 Local Development Setup Guide

Complete guide for setting up and synchronizing the AMAS project for local development.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Full Setup Process](#full-setup-process)
3. [Synchronization Scripts](#synchronization-scripts)
4. [Local Workflow Execution](#local-workflow-execution)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Step 1: Setup local environment
python scripts/setup_local_environment.py

# Step 2: Sync from GitHub (if network available)
python scripts/sync_from_github.py

# Step 3: Configure environment variables
# Edit .env file and add your API keys
notepad .env  # Windows
# or
nano .env     # Linux/Mac
```

### 2. Verify Installation

```bash
# Test basic imports
python -c "import fastapi, openai, yaml; print('✅ All imports successful')"

# List available workflows
python scripts/run_local_workflows.py --list

# Run a test workflow
python scripts/run_local_workflows.py 00-master-ai-orchestrator.yml --job layer1_detection_analysis
```

---

## 📦 Full Setup Process

### Step 1: Environment Setup

The `setup_local_environment.py` script will:

✅ Check Python version (3.8+ required, 3.11+ recommended)  
✅ Upgrade pip, setuptools, and wheel  
✅ Install all project dependencies  
✅ Create `.env` template file  
✅ Verify required scripts exist  
✅ Run basic import tests  

**Run it:**
```bash
python scripts/setup_local_environment.py
```

### Step 2: GitHub Synchronization

The `sync_from_github.py` script will:

✅ Fetch all branches from GitHub  
✅ Pull latest changes for current branch  
✅ Sync all remote branches locally  
✅ Show final git status  

**Run it:**
```bash
python scripts/sync_from_github.py
```

**Note:** If you have uncommitted changes, the script will ask if you want to stash them.

### Step 3: Configure API Keys

1. Open the `.env` file created by the setup script
2. Add your API keys for at least 3 AI providers (recommended for failover)

**Minimum Configuration (Basic Mode):**
```bash
DEEPSEEK_API_KEY=your_key_here
GLM_API_KEY=your_key_here
GROK_API_KEY=your_key_here
```

**Recommended Configuration (Standard Mode):**
```bash
# Add these to your minimum config
CEREBRAS_API_KEY=your_key_here
NVIDIA_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

### Step 4: Verify Setup

```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip list | grep -E "fastapi|openai|yaml"

# Test imports
python -c "import sys; from src.amas.ai.router import get_available_providers; print('✅ Router available')"
```

---

## 🔄 Synchronization Scripts

### Sync FROM GitHub

```bash
python scripts/sync_from_github.py
```

This script:
- Fetches all remote branches
- Pulls latest changes for current branch
- Handles uncommitted changes (with stashing option)
- Shows final status

### Sync TO GitHub

```bash
python scripts/sync_to_github.py
```

This script:
- Lists uncommitted files
- Stages changes
- Commits with custom or auto-generated message
- Pushes to GitHub (with confirmation)

**Usage:**
```bash
# Interactive mode (recommended)
python scripts/sync_to_github.py

# Or use git commands directly
git add .
git commit -m "Your commit message"
git push origin main
```

---

## 🏃 Local Workflow Execution

### List Available Workflows

```bash
python scripts/run_local_workflows.py --list
```

### List Jobs in a Workflow

```bash
python scripts/run_local_workflows.py --list-jobs 00-master-ai-orchestrator.yml
```

### Run a Complete Workflow

```bash
python scripts/run_local_workflows.py 00-master-ai-orchestrator.yml
```

### Run a Specific Job

```bash
python scripts/run_local_workflows.py 00-master-ai-orchestrator.yml --job layer1_detection_analysis
```

### Available Workflows

| Workflow | Description |
|----------|-------------|
| `00-master-ai-orchestrator.yml` | Master AI orchestrator with 4-layer architecture |
| `01-ai-agentic-project-self-improver.yml` | Project self-improvement system |
| `02-ai-agentic-issue-auto-responder.yml` | Issue auto-responder |
| `03-ai-agent-project-audit-documentation.yml` | Project audit and documentation |
| `04-ai-enhanced-build-deploy.yml` | Build and deployment |
| `05-ai-security-threat-intelligence.yml` | Security threat intelligence |
| `06-ai-code-quality-performance.yml` | Code quality and performance |
| `07-ai-enhanced-cicd-pipeline.yml` | Enhanced CI/CD pipeline |

---

## 🔧 Manual Workflow Execution

If you prefer to run workflows manually, you can execute the Python scripts directly:

### Master Orchestrator - Layer 1

```bash
python .github/scripts/enhanced_code_quality_inspector.py \
  --mode intelligent \
  --priority normal \
  --target all \
  --providers all \
  --use-advanced-manager \
  --output layer1_analysis_results.json
```

### Master Orchestrator - Layer 2

```bash
python .github/scripts/ai_master_orchestrator.py \
  --mode intelligent \
  --priority normal \
  --target all \
  --providers all \
  --use-advanced-manager \
  --input layer1_analysis_results.json \
  --output layer2_decision_results.json
```

### Comprehensive Audit

```bash
python .github/scripts/comprehensive_audit_engine.py \
  --audit-type comprehensive \
  --create-issues false \
  --notify-on-failure false \
  --output audit_results.json
```

---

## 🐛 Troubleshooting

### Issue: "Could not resolve host: github.com"

**Solution:** Check your network connection. You can still work locally:
- All scripts work without GitHub connection
- Workflows can run locally
- Sync when network is available

### Issue: "Python version incompatible"

**Solution:** 
- Install Python 3.8+ (3.11+ recommended)
- Windows: Download from python.org
- Linux: `sudo apt install python3.11` or use pyenv
- Mac: `brew install python@3.11`

### Issue: "Dependencies failed to install"

**Solution:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip setuptools wheel

# Try installing with binary wheels
pip install --prefer-binary -r requirements.txt

# If still failing, install key packages individually
pip install fastapi uvicorn openai anthropic pyyaml
```

### Issue: "Module not found" errors

**Solution:**
```bash
# Ensure you're in the project root
cd /path/to/Advanced-Multi-Agent-Intelligence-System

# Install in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: "API key not found"

**Solution:**
1. Check `.env` file exists and has API keys
2. Load environment variables:
   ```bash
   # Windows (PowerShell)
   Get-Content .env | ForEach-Object { $_.Split('=') | Set-Variable -Name $_[0] -Value $_[1] }
   
   # Windows (CMD) - Use python-dotenv
   python -c "from dotenv import load_dotenv; load_dotenv()"
   
   # Linux/Mac
   export $(cat .env | xargs)
   ```

### Issue: "Workflow script not found"

**Solution:**
```bash
# Verify scripts exist
ls -la .github/scripts/

# Check if you need to sync from GitHub
python scripts/sync_from_github.py
```

### Issue: "Git push failed"

**Solution:**
```bash
# Pull latest changes first
git pull origin main

# Resolve any conflicts
git status

# Then push again
git push origin main
```

---

## 📚 Additional Resources

### Documentation

- [README.md](README.md) - Main project documentation
- [QUICK_START.md](docs/QUICK_START.md) - Quick start guide
- [AI_PROVIDERS.md](docs/AI_PROVIDERS.md) - AI provider configuration
- [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) - Configuration options

### Scripts Reference

| Script | Purpose |
|--------|---------|
| `setup_local_environment.py` | Initial environment setup |
| `sync_from_github.py` | Pull changes from GitHub |
| `sync_to_github.py` | Push changes to GitHub |
| `run_local_workflows.py` | Execute workflows locally |
| `validate_env.py` | Validate environment configuration |
| `benchmark_system.py` | Benchmark system performance |

### Environment Variables

See `.env` template for all available environment variables. Key variables:

- **AI Provider Keys**: `DEEPSEEK_API_KEY`, `GLM_API_KEY`, etc.
- **Security**: `JWT_SECRET_KEY`, `ENCRYPTION_KEY`
- **Configuration**: `RATE_LIMIT_ENABLED`, `AUDIT_LOGGING`
- **Redis**: `AMAS_REDIS_HOST`, `AMAS_REDIS_PORT`

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Python 3.8+ installed and working
- [ ] All dependencies installed (`pip list`)
- [ ] `.env` file created and configured
- [ ] At least 3 AI API keys configured
- [ ] Can import key modules (`fastapi`, `openai`, `yaml`)
- [ ] Git repository is clean or synced
- [ ] Can list workflows (`python scripts/run_local_workflows.py --list`)
- [ ] Can run a test workflow locally
- [ ] Can sync to/from GitHub (if network available)

---

## 🎯 Next Steps

1. **Start Developing**: Make your changes locally
2. **Test Locally**: Run workflows before pushing
3. **Sync Regularly**: Use sync scripts to keep in sync with GitHub
4. **Commit Often**: Use `sync_to_github.py` or git commands

---

**Happy Coding! 🚀**

For issues or questions, check the [GitHub Issues](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues) or [Discussions](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/discussions).


