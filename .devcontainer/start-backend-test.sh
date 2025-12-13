#!/bin/bash
# Quick test script to start backend and verify it works
# This will start the server in the background, test it, then stop it

set -e

echo "🚀 AMAS Backend Quick Start Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Detect which main.py to use
STARTUP_CMD=""
APP_MODULE=""

if [ -f "main.py" ]; then
    if python -c "import main; hasattr(main, 'app')" 2>/dev/null; then
        STARTUP_CMD="uvicorn main:app --host 0.0.0.0 --port 8000"
        APP_MODULE="main:app"
        echo -e "${GREEN}✅ Using main.py (root level)${NC}"
    fi
fi

if [ -z "$STARTUP_CMD" ] && [ -f "src/amas/api/main.py" ]; then
    if python -c "from src.amas.api.main import app" 2>/dev/null; then
        STARTUP_CMD="uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000"
        APP_MODULE="src.amas.api.main:app"
        echo -e "${GREEN}✅ Using src/amas/api/main.py${NC}"
    fi
fi

if [ -z "$STARTUP_CMD" ]; then
    echo -e "${RED}❌ Could not find valid application entry point${NC}"
    echo ""
    echo "Please run diagnostic test first:"
    echo "   bash .devcontainer/test-backend.sh"
    exit 1
fi

# Check if port is available
echo ""
echo "🔌 Checking port 8000..."
if command -v netstat >/dev/null 2>&1; then
    if netstat -tuln 2>/dev/null | grep -q ":8000 "; then
        echo -e "${YELLOW}⚠️  Port 8000 is in use${NC}"
        echo "   Trying to use port 8001 instead..."
        STARTUP_CMD="${STARTUP_CMD//:8000/:8001}"
        TEST_PORT=8001
    else
        echo -e "${GREEN}✅ Port 8000 is available${NC}"
        TEST_PORT=8000
    fi
else
    TEST_PORT=8000
fi

# Start server in background
echo ""
echo "🚀 Starting backend server..."
echo "   Command: $STARTUP_CMD"
echo ""

# Start uvicorn in background
python -m uvicorn $APP_MODULE --host 0.0.0.0 --port $TEST_PORT > /tmp/uvicorn-test.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start (max 10 seconds)..."
for i in {1..10}; do
    sleep 1
    if curl -s http://localhost:$TEST_PORT/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Server started successfully!${NC}"
        echo ""
        echo "📊 Server Status:"
        curl -s http://localhost:$TEST_PORT/health | python -m json.tool 2>/dev/null || curl -s http://localhost:$TEST_PORT/health
        echo ""
        echo -e "${GREEN}✅ Backend is working!${NC}"
        echo ""
        echo "🌐 Access points:"
        echo "   Health:    http://localhost:$TEST_PORT/health"
        echo "   API Docs:  http://localhost:$TEST_PORT/docs"
        echo "   ReDoc:     http://localhost:$TEST_PORT/redoc"
        echo ""
        echo "🛑 Stopping test server..."
        kill $SERVER_PID 2>/dev/null || true
        wait $SERVER_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Test complete!${NC}"
        echo ""
        echo "🚀 To start the backend permanently:"
        echo "   $STARTUP_CMD"
        exit 0
    fi
done

# If we get here, server didn't start
echo -e "${RED}❌ Server failed to start within 10 seconds${NC}"
echo ""
echo "📋 Server logs:"
tail -20 /tmp/uvicorn-test.log 2>/dev/null || echo "   No logs available"
echo ""
echo "🛑 Stopping server process..."
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

echo ""
echo "💡 Troubleshooting:"
echo "   1. Run diagnostic: bash .devcontainer/test-backend.sh"
echo "   2. Check for import errors in the logs above"
echo "   3. Verify dependencies: pip list | grep -E '(fastapi|uvicorn)'"
echo "   4. Try starting manually: $STARTUP_CMD"
exit 1

