#!/bin/bash
# Post-create script for AMAS devcontainer
# Don't exit on error - continue with setup even if some steps fail
set +e

echo "🚀 Setting up AMAS development environment..."

# Get workspace path from environment or use current directory
WORKSPACE_DIR="${WORKSPACE_FOLDER:-$(pwd)}"
if [ -n "$WORKSPACE_FOLDER" ]; then
    cd "$WORKSPACE_FOLDER" || cd /workspaces/*/ 2>/dev/null || true
else
    # Try to find workspace directory
    if [ -d "/workspaces" ]; then
        cd /workspaces/*/ 2>/dev/null || true
    fi
fi

echo "📁 Working directory: $(pwd)"

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel

# Install/update dependencies
echo "📦 Installing dependencies..."
if [ -f requirements.txt ]; then
    echo "   Installing from requirements.txt..."
    pip install --root-user-action=ignore -r requirements.txt || {
        echo "   ⚠️  Some packages had conflicts, installing core packages..."
        pip install --root-user-action=ignore fastapi uvicorn pydantic pyyaml openai passlib[bcrypt]
    }
    # Try to install dev requirements if available
    if [ -f requirements-dev.txt ]; then
        echo "   Installing additional dev dependencies..."
        pip install --root-user-action=ignore -r requirements-dev.txt || echo "   ⚠️  Dev dependencies had some issues, continuing..."
    fi
else
    echo "   ⚠️  No requirements file found, installing core packages..."
    pip install --root-user-action=ignore fastapi uvicorn pydantic pyyaml openai passlib[bcrypt]
fi

# Verify Python installation
echo "🐍 Verifying Python setup..."
python --version
python -c "import sys; print(f'Python path: {sys.executable}')"

# Verify key imports
echo "🔍 Testing key imports..."
python -c "import fastapi; print('✅ FastAPI')" || echo "⚠️  FastAPI not available"
python -c "import yaml; print('✅ PyYAML')" || echo "⚠️  PyYAML not available"
python -c "import openai; print('✅ OpenAI')" || echo "⚠️  OpenAI not available"

# Check Node.js/npm for frontend
echo ""
echo "🔍 Checking Node.js/npm..."
if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
    echo "   ✅ Node.js $(node --version) is installed"
    echo "   ✅ npm $(npm --version) is installed"
    # Check if frontend directory exists and install dependencies
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
        echo ""
        echo "📦 Installing frontend dependencies..."
        cd frontend && npm install --legacy-peer-deps 2>&1 | tail -5 || echo "   ⚠️  Frontend dependencies had some issues, continuing..."
        cd ..
    fi
else
    echo "   ⚠️  Node.js/npm not found (frontend development will require manual installation)"
fi

# Detect which main.py to use
echo ""
echo "🔍 Detecting application entry point..."
STARTUP_CMD=""
if [ -f "main.py" ]; then
    echo "   ✅ Found main.py (root level)"
    if python -c "import main; hasattr(main, 'app')" 2>/dev/null; then
        STARTUP_CMD="uvicorn main:app --reload --host 0.0.0.0 --port 8000"
        echo "   ✅ main.py contains FastAPI app"
    else
        echo "   ⚠️  main.py found but app not detected, checking src/amas/api/main.py..."
        if [ -f "src/amas/api/main.py" ]; then
            if python -c "from src.amas.api.main import app" 2>/dev/null; then
                STARTUP_CMD="uvicorn src.amas.api.main:app --reload --host 0.0.0.0 --port 8000"
                echo "   ✅ Using src/amas/api/main.py"
            fi
        fi
    fi
elif [ -f "src/amas/api/main.py" ]; then
    echo "   ✅ Found src/amas/api/main.py"
    if python -c "from src.amas.api.main import app" 2>/dev/null; then
        STARTUP_CMD="uvicorn src.amas.api.main:app --reload --host 0.0.0.0 --port 8000"
        echo "   ✅ src/amas/api/main.py contains FastAPI app"
    else
        echo "   ⚠️  src/amas/api/main.py found but import failed"
    fi
else
    echo "   ⚠️  No main.py found - backend may not start"
fi

# Run diagnostic test if script exists
if [ -f ".devcontainer/test-backend.sh" ]; then
    echo ""
    echo "🔍 Running backend diagnostic test..."
    bash .devcontainer/test-backend.sh || echo "   ⚠️  Diagnostic test had issues (see output above)"
fi

# Set up git (if needed)
if [ -d .git ]; then
    echo "📝 Configuring git..."
    CURRENT_DIR=$(pwd)
    git config --global --add safe.directory "$CURRENT_DIR" || true
fi

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file template..."
    CURRENT_DIR=$(pwd)
    cat > .env << EOF
# AMAS Environment Configuration
AMAS_ENV=development
PYTHONPATH=$CURRENT_DIR

# Port Configuration (optional - defaults used if not set)
# BACKEND_PORT=8000
# DASHBOARD_PORT=8080
# FRONTEND_PORT=3000

# Add your API keys here
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here
EOF
    echo "✅ Created .env file - please add your API keys"
fi

# Display port configuration
echo ""
echo "🔌 Port Configuration:"
BACKEND_PORT=${BACKEND_PORT:-8000}
DASHBOARD_PORT=${DASHBOARD_PORT:-8080}
FRONTEND_PORT=${FRONTEND_PORT:-3000}
echo "   Backend API:   http://localhost:${BACKEND_PORT}"
echo "   Dashboard:    http://localhost:${DASHBOARD_PORT}"
echo "   Frontend:      http://localhost:${FRONTEND_PORT}"
echo "   (Ports can be configured via BACKEND_PORT, DASHBOARD_PORT, FRONTEND_PORT env vars)"

echo ""
echo "✅ AMAS development environment ready!"
echo ""
echo "📚 Next steps:"
echo "   1. Add API keys to .env file (if needed)"
if [ -n "$STARTUP_CMD" ]; then
    echo "   2. Start backend:"
    echo "      Option A (recommended): bash .devcontainer/start-backend.sh"
    echo "      Option B (manual): $STARTUP_CMD"
    echo "      Option C (test first): bash .devcontainer/test-backend.sh"
else
    echo "   2. Run diagnostic: bash .devcontainer/test-backend.sh"
    echo "      This will help identify the correct startup command"
fi
echo "   3. Access FastAPI docs at http://localhost:${BACKEND_PORT}/docs"
echo ""
echo "💡 Important Notes:"
echo "   - Warnings about database/Redis/Neo4j are NORMAL - these are optional"
echo "   - Backend will work without these services"
echo "   - Run: bash .devcontainer/test-backend.sh (for diagnostics)"
echo "   - Run: bash .devcontainer/start-backend.sh (to start server)"
echo ""

