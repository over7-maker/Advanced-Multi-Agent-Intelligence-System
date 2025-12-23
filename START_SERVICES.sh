#!/bin/bash
# Quick start script for backend and frontend

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   🚀 AMAS - Start Backend & Frontend                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if services are already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Backend already running on port 8000"
else
    echo "✅ Starting Backend..."
    echo "   Command: uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    echo "   Access: http://localhost:8000"
    echo "   Docs: http://localhost:8000/docs"
    echo ""
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo "   Backend PID: $BACKEND_PID"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -d "frontend" ]; then
    echo "✅ Frontend directory found"
    echo "   To start frontend, run:"
    echo "   cd frontend && npm run dev"
else
    echo "⚠️  Frontend directory not found"
fi

echo ""
echo "✅ Services starting..."
echo "   Press Ctrl+C to stop"
wait
