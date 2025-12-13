#!/bin/bash
# Script to check and free up ports for devcontainer

echo "🔍 Checking ports 8000, 3000, 8080..."

# Function to check if port is in use
check_port() {
    local port=$1
    if command -v lsof >/dev/null 2>&1; then
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "⚠️  Port $port is in use"
            lsof -Pi :$port -sTCP:LISTEN
            return 1
        else
            echo "✅ Port $port is available"
            return 0
        fi
    elif command -v netstat >/dev/null 2>&1; then
        if netstat -ano | grep -q ":$port "; then
            echo "⚠️  Port $port is in use"
            netstat -ano | grep ":$port "
            return 1
        else
            echo "✅ Port $port is available"
            return 0
        fi
    elif command -v ss >/dev/null 2>&1; then
        if ss -tulpn | grep -q ":$port "; then
            echo "⚠️  Port $port is in use"
            ss -tulpn | grep ":$port "
            return 1
        else
            echo "✅ Port $port is available"
            return 0
        fi
    else
        echo "⚠️  Cannot check port $port (no port checking tool available)"
        return 0
    fi
}

# Check all ports
check_port 8000
check_port 3000
check_port 8080

echo ""
echo "💡 If ports are in use, you can:"
echo "   1. Stop the processes using these ports (see above)"
echo "   2. Use different ports by setting environment variables:"
echo "      export BACKEND_PORT=8001"
echo "      export DASHBOARD_PORT=8081"
echo "      export FRONTEND_PORT=3001"
echo "   3. Kill processes using these ports (use with caution):"
echo "      lsof -ti:8000 | xargs kill -9"
echo "      lsof -ti:3000 | xargs kill -9"
echo "      lsof -ti:8080 | xargs kill -9"

