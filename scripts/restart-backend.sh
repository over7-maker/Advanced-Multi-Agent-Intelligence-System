#!/bin/bash
# Script to restart the backend server with the new frontend

echo "🔄 Restarting AMAS Backend Server..."
echo ""

# Kill any existing uvicorn processes
pkill -f "uvicorn main:app" 2>/dev/null || true

# Wait a moment
sleep 2

# Start the backend server
echo "🚀 Starting backend on port 8000..."
echo "📝 Access the new React dashboard at: http://localhost:8000/"
echo ""
echo "⚠️  IMPORTANT: Make sure to:"
echo "   1. Clear your browser cache (Ctrl+Shift+R or Cmd+Shift+R)"
echo "   2. Access http://localhost:8000/ (NOT port 3000)"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000

