#!/bin/bash
# Set AMAS devcontainer to use different ports to avoid conflicts
# Run this before opening the devcontainer if port 8000 is in use

export BACKEND_PORT=8001
export DASHBOARD_PORT=8081
export FRONTEND_PORT=3001

echo "✅ AMAS devcontainer ports configured:"
echo "   Backend:   http://localhost:${BACKEND_PORT}"
echo "   Dashboard: http://localhost:${DASHBOARD_PORT}"
echo "   Frontend:  http://localhost:${FRONTEND_PORT}"
echo ""
echo "💡 These ports will be used when you open the devcontainer"
echo "💡 Make sure to run this script in the same terminal session before opening the container"

