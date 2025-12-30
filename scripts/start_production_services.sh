#!/bin/bash
# Script to start all production services (Backend + Frontend Preview)

set -e

echo "========================================"
echo "🚀 Starting AMAS Production Services"
echo "========================================"
echo ""

# Check if backend is running
echo "📍 Checking Backend status..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Backend is not running on port 8000"
    echo "📝 Starting Backend in background..."
    cd "$(dirname "$0")/.."
    export ENVIRONMENT=production
    export DATABASE_URL="postgresql://postgres:amas_password@localhost:5432/amas"
    export REDIS_URL="redis://localhost:6379/0"
    nohup python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
    echo "⏳ Waiting for backend to start..."
    sleep 5
else
    echo "✅ Backend is already running"
fi

echo ""
echo "📍 Starting Frontend Preview (Port 4173)..."
cd "$(dirname "$0")/../frontend"

# Check if frontend preview is already running
if ! lsof -Pi :4173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "🚀 Starting Frontend Preview..."
    nohup npm run preview > ../logs/frontend.log 2>&1 &
    echo "⏳ Waiting for frontend to start..."
    sleep 3
else
    echo "⚠️  Frontend preview is already running on port 4173"
fi

echo ""
echo "========================================"
echo "✅ Services Started!"
echo "========================================"
echo ""
echo "🌐 Frontend Preview: http://localhost:4173"
echo "🌐 Landing Page: http://localhost:4173/landing"
echo "🌐 Testing Dashboard: http://localhost:4173/testing"
echo "🌐 Dashboard: http://localhost:4173/dashboard"
echo "🌐 Backend API: http://localhost:8000"
echo "🌐 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Note: Make sure to rebuild frontend first if you made changes:"
echo "   ./scripts/rebuild_frontend_production.sh"
echo ""

