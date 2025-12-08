#!/bin/bash
# Start Backend Server - Handles port conflicts automatically

PORT=${1:-8000}

echo "🚀 Starting AMAS Backend Server..."
echo ""

# Check if port is in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port $PORT is already in use"
    echo "   Killing existing process..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null
    pkill -f "uvicorn main:app" 2>/dev/null
    sleep 2
    echo "✅ Port $PORT freed"
    echo ""
fi

# Start server
echo "✅ Starting server on port $PORT..."
echo "   Access: http://localhost:$PORT"
echo "   Docs: http://localhost:$PORT/docs"
echo "   Health: http://localhost:$PORT/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port $PORT

