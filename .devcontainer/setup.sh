#!/bin/bash
set -euxo pipefail

# Dev Container Setup Script
# Handles both onCreate and postCreate operations

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
      python3 -m venv /home/vscode/venv
      echo "✓ Created virtual environment"
    fi
    
    # Activate virtual environment
    source /home/vscode/venv/bin/activate
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
      echo "⚠ Warning: requirements.txt not found (treated as optional)"
    fi
    
    # Install requirements-dev.txt (optional)
    if [ -f requirements-dev.txt ]; then
      pip install --no-input --progress-bar off -r requirements-dev.txt
      echo "✓ Installed requirements-dev.txt"
    else
      echo "⚠ requirements-dev.txt not found (optional)"
    fi
    
    # Verify Python installation
    python -c "import sys; print(f'✅ Python {sys.version}')"
    echo "✅ Dependencies installed successfully"
    ;;
    
  updateContent)
    echo "🔄 Running updateContent (dependency refresh)..."
    # Only update dependencies if requirements files changed
    if [ -f requirements.txt ]; then
      source /home/vscode/venv/bin/activate 2>/dev/null || python3 -m venv /home/vscode/venv && source /home/vscode/venv/bin/activate
      pip install --upgrade pip --quiet
      pip install --no-input --progress-bar off -r requirements.txt --upgrade
      echo "✓ Updated requirements.txt"
    fi
    if [ -f requirements-dev.txt ]; then
      source /home/vscode/venv/bin/activate
      pip install --no-input --progress-bar off -r requirements-dev.txt --upgrade
      echo "✓ Updated requirements-dev.txt"
    fi
    echo "✅ Update complete"
    ;;
    
  *)
    echo "Usage: $0 [onCreate|postCreate|updateContent]"
    exit 1
    ;;
esac
