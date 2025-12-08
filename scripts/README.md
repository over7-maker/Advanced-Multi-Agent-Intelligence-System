# 📜 AMAS Development Scripts

This directory contains utility scripts for local development and synchronization with GitHub.

## 🚀 Quick Reference

### Setup & Installation

```bash
# Complete environment setup
python scripts/setup_local_environment.py

# Sync from GitHub
python scripts/sync_from_github.py
```

### Synchronization

```bash
# Pull latest changes from GitHub
python scripts/sync_from_github.py

# Push local changes to GitHub
python scripts/sync_to_github.py
```

### Workflow Execution

```bash
# List available workflows
python scripts/run_local_workflows.py --list

# Run a workflow
python scripts/run_local_workflows.py 00-master-ai-orchestrator.yml

# Run a specific job
python scripts/run_local_workflows.py 00-master-ai-orchestrator.yml --job layer1_detection_analysis
```

## 📋 Script Descriptions

### `setup_local_environment.py`

Complete local development environment setup:
- Checks Python version compatibility
- Upgrades pip, setuptools, wheel
- Installs all project dependencies
- Creates `.env` template file
- Verifies required scripts exist
- Runs basic import tests

**Usage:**
```bash
python scripts/setup_local_environment.py
```

### `sync_from_github.py`

Synchronizes local repository with GitHub:
- Fetches all remote branches
- Pulls latest changes for current branch
- Handles uncommitted changes (with stashing option)
- Shows final git status

**Usage:**
```bash
python scripts/sync_from_github.py
```

**Features:**
- Automatic branch detection
- Uncommitted changes handling
- Remote branch synchronization
- Status reporting

### `sync_to_github.py`

Pushes local changes to GitHub:
- Lists uncommitted files
- Stages changes interactively
- Commits with custom or auto-generated message
- Pushes to GitHub (with confirmation)

**Usage:**
```bash
python scripts/sync_to_github.py
```

**Features:**
- Interactive file selection
- Custom commit messages
- Safety confirmations
- Error handling

### `run_local_workflows.py`

Executes GitHub Actions workflows locally:
- Parses workflow YAML files
- Runs equivalent Python scripts
- Handles workflow jobs and steps
- Supports job filtering

**Usage:**
```bash
# List workflows
python scripts/run_local_workflows.py --list

# Run complete workflow
python scripts/run_local_workflows.py 00-master-ai-orchestrator.yml

# Run specific job
python scripts/run_local_workflows.py 00-master-ai-orchestrator.yml --job layer1_detection_analysis

# List jobs in workflow
python scripts/run_local_workflows.py --list-jobs 00-master-ai-orchestrator.yml
```

**Features:**
- YAML workflow parsing
- Script execution mapping
- Step-by-step execution
- Error handling and reporting

## 🔧 Additional Scripts

### Testing Scripts

Located in `scripts/testing/`:
- `validate_workflows.py` - Validate workflow YAML syntax
- `validate_complete_workflows.py` - Comprehensive workflow validation
- `test_universal_ai_workflow.py` - Test AI workflow execution

### Maintenance Scripts

Located in `scripts/maintenance/`:
- `ultimate_workflow_fixer.py` - Fix workflow issues
- `run_workflow_verification.py` - Verify workflow execution
- `complete_workflow_setup.py` - Complete workflow setup

### Validation Scripts

- `validate_env.py` - Validate environment configuration
- `benchmark_system.py` - Benchmark system performance

## 📚 Documentation

- [LOCAL_DEVELOPMENT_SETUP.md](../LOCAL_DEVELOPMENT_SETUP.md) - Complete setup guide
- [README.md](../README.md) - Main project documentation
- [QUICK_START.md](../docs/QUICK_START.md) - Quick start guide

## ⚠️ Notes

1. **Network Issues**: If you can't connect to GitHub, scripts will still work locally
2. **Dependencies**: Some scripts require additional packages (install via `requirements.txt`)
3. **Python Version**: Python 3.8+ required, 3.11+ recommended
4. **Environment**: Always ensure `.env` file is configured with API keys

## 🐛 Troubleshooting

### Script won't run

```bash
# Check Python version
python --version

# Check if script is executable
chmod +x scripts/setup_local_environment.py  # Linux/Mac

# Run with explicit Python
python scripts/setup_local_environment.py
```

### Import errors

```bash
# Ensure you're in project root
cd /path/to/Advanced-Multi-Agent-Intelligence-System

# Install dependencies
pip install -r requirements.txt

# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Git errors

```bash
# Verify git is installed
git --version

# Check git status
git status

# Verify remote
git remote -v
```

---

**For more help, see [LOCAL_DEVELOPMENT_SETUP.md](../LOCAL_DEVELOPMENT_SETUP.md)**


