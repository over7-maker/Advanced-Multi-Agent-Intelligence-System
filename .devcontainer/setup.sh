#!/usr/bin/env bash
set -euo pipefail

# Log all output for debugging
exec > >(tee -a /tmp/devcontainer-setup.log) 2>&1
echo "=========================================="
echo "Dev Container Setup: ${1:-unknown}"
echo "Timestamp: $(date -u +"%Y-%m-%d %H:%M:%SZ")"
echo "User: $(whoami)"
echo "=========================================="

# Dev Container Setup Script
# Handles both onCreate and postCreate operations

# Validate required tools
if ! command -v python3 &> /dev/null; then
  echo "❌ Error: python3 not found"
  exit 1
fi

if ! command -v pip &> /dev/null && ! python3 -m pip --version &> /dev/null; then
  echo "⚠️ Warning: pip not found, will use python3 -m pip"
fi

ACTION="${1:-postCreate}"

case "$ACTION" in
  onCreate)
    echo "🔧 Running onCreate setup..."
    if [ -f .env.example ]; then
      cp .env.example .env
      echo "✓ Created .env from .env.example"
    else
      echo "⚠ Warning: .env.example not found. Create .env manually."
    fi
    ;;
    
  postCreate)
    echo "📦 Installing dependencies..."

    # Create virtual environment if it doesn't exist
    if [ ! -d /home/vscode/venv ]; then
      python3 -m venv /home/vscode/venv || {
        echo "❌ Failed to create virtual environment"
        exit 1
      }
      echo "✓ Created virtual environment"
    fi

    # Activate virtual environment
    source /home/vscode/venv/bin/activate || {
      echo "❌ Failed to activate virtual environment"
      exit 1
    }
    export VIRTUAL_ENV=/home/vscode/venv
    export PATH="$VIRTUAL_ENV/bin:$PATH"

    # Install requirements.txt (required)
    if [ -f requirements.txt ]; then
      pip install --no-input --progress-bar off -r requirements.txt || {
        echo "❌ Failed to install requirements.txt"
        exit 1
      }
      echo "✓ Installed requirements.txt"
    else
      echo "❌ Error: requirements.txt not found (required)"
      exit 1
    fi

    # Install requirements-dev.txt (optional)
    if [ -f requirements-dev.txt ]; then
      pip install --no-input --progress-bar off -r requirements-dev.txt || {
        echo "⚠️ Warning: Failed to install requirements-dev.txt (non-fatal)"
      }
      echo "✓ Installed requirements-dev.txt"
    else
      echo "ℹ️ requirements-dev.txt not found (optional)"
    fi

    # Verify Python installation and dependencies
    python -c "import sys; assert sys.version_info >= (3, 11), 'Python 3.11+ required'; print(f'✅ Python {sys.version}')" || {
      echo "❌ Python version check failed"
      exit 1
    }
    echo "✅ Dependencies installed successfully"
    ;;
    
  updateContent)
    echo "🔄 Running updateContent (dependency refresh)..."
    # Activate venv if it exists, create if not
    if [ ! -d /home/vscode/venv ]; then
      echo "Creating virtual environment..."
      python3 -m venv /home/vscode/venv || {
        echo "❌ Failed to create virtual environment"
        exit 1
      }
    fi
    source /home/vscode/venv/bin/activate || {
      echo "❌ Failed to activate virtual environment"
      exit 1
    }
    export VIRTUAL_ENV=/home/vscode/venv
    export PATH="$VIRTUAL_ENV/bin:$PATH"

    # Only update dependencies if requirements files exist
    if [ -f requirements.txt ]; then
      pip install --upgrade pip --quiet || {
        echo "⚠️ Warning: pip upgrade failed (continuing)"
      }
      pip install --no-input --progress-bar off -r requirements.txt --upgrade || {
        echo "❌ Failed to update requirements.txt"
        exit 1
      }
      echo "✓ Updated requirements.txt"
    else
      echo "❌ Error: requirements.txt not found"
      exit 1
    fi
    if [ -f requirements-dev.txt ]; then
      pip install --no-input --progress-bar off -r requirements-dev.txt --upgrade || {
        echo "⚠️ Warning: Failed to update requirements-dev.txt (non-fatal)"
      }
      echo "✓ Updated requirements-dev.txt"
    else
      echo "ℹ️ requirements-dev.txt not found (optional)"
    fi
    echo "✅ Update complete"
    ;;
    
  *)
    echo "Usage: $0 [onCreate|postCreate|updateContent]"
    exit 1
    ;;
esac
