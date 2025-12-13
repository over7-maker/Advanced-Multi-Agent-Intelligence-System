#!/bin/bash
# FIX NOW - Force serve NEW React frontend

echo "🛑 Stopping ALL servers..."
pkill -f "uvicorn" 2>/dev/null
pkill -f "vite" 2>/dev/null
pkill -f "npm" 2>/dev/null
sleep 2

echo "✅ All servers stopped"
echo ""
echo "🚀 Starting backend with NEW React frontend..."
echo "📝 Access at: http://localhost:8000/"
echo ""

cd /workspaces/Advanced-Multi-Agent-Intelligence-System

# Verify frontend exists
if [ ! -f "frontend/dist/index.html" ]; then
    echo "❌ ERROR: frontend/dist/index.html not found!"
    echo "Building frontend..."
    cd frontend && npm run build && cd ..
fi

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

