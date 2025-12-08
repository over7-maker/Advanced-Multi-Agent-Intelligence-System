#!/bin/bash
# Start Backend Server - Handles port conflicts

PORT=${1:-8000}

echo "🚀 Starting AMAS Backend Server..."
echo ""

# Kill any process on the port using Python
python3 kill_port_8000.py $PORT

sleep 2

# Start server
echo ""
echo "✅ Starting server on port $PORT..."
echo "   Access: http://localhost:$PORT"
echo "   Docs: http://localhost:$PORT/docs"
echo "   Health: http://localhost:$PORT/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port $PORT

