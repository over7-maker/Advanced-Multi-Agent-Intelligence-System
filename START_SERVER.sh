#!/bin/bash
# Start AMAS Backend with NEW React Frontend

echo "🚀 Starting AMAS Backend Server..."
echo "📝 This will serve the NEW React dashboard at: http://localhost:8000/"
echo ""

# Kill any existing servers
pkill -f "uvicorn main:app" 2>/dev/null
sleep 2

# Start the server
cd /workspaces/Advanced-Multi-Agent-Intelligence-System
uvicorn main:app --reload --host 0.0.0.0 --port 8000

