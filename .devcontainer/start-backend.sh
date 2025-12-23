#!/bin/bash
# Start AMAS Backend Server
# Handles optional services gracefully (database, Redis, Neo4j warnings are normal)

set -e

PORT=${1:-8000}

echo "🚀 Starting AMAS Backend Server..."
echo ""

# Detect which main.py to use
if [ -f "main.py" ] && python -c "import main; hasattr(main, 'app')" 2>/dev/null; then
    APP_MODULE="main:app"
    echo "✅ Using main.py (root level)"
elif [ -f "src/amas/api/main.py" ] && python -c "from src.amas.api.main import app" 2>/dev/null; then
    APP_MODULE="src.amas.api.main:app"
    echo "✅ Using src/amas/api/main.py"
else
    echo "❌ Could not find valid application entry point"
    echo "   Run: bash .devcontainer/test-backend.sh"
    exit 1
fi

# Check if port is in use (optional check)
if command -v netstat >/dev/null 2>&1; then
    if netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
        echo "⚠️  Port $PORT is already in use"
        echo "   Trying to free port..."
        # Try to find and kill process (if possible)
        if command -v lsof >/dev/null 2>&1; then
            lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
            sleep 2
        fi
    fi
fi

echo ""
echo "✅ Starting server on port $PORT..."
echo "   Access: http://localhost:$PORT"
echo "   Docs: http://localhost:$PORT/docs"
echo "   Health: http://localhost:$PORT/health"
echo ""
echo "💡 Note: Warnings about database/Redis/Neo4j are normal - these are optional services"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start uvicorn
python -m uvicorn $APP_MODULE --reload --host 0.0.0.0 --port $PORT

