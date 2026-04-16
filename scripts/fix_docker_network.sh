#!/bin/bash
# Script to fix Docker network conflicts

set -e

echo "========================================"
echo "🔧 Fixing Docker Network Conflicts"
echo "========================================"
echo ""

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "💡 Please start Docker and try again."
    exit 1
fi

echo "🔍 Checking for conflicting networks..."
echo ""

# List all networks
echo "📋 Current Docker networks:"
docker network ls | grep amas-network || true
echo ""

echo "🔧 Attempting to remove conflicting network..."
if docker network rm advanced-multi-agent-intelligence-system_amas-network 2>/dev/null; then
    echo "✅ Network removed successfully"
else
    echo "ℹ️  Network not found or already removed"
fi

echo ""
echo "🧹 Cleaning up unused networks..."
docker network prune -f

echo ""
echo "========================================"
echo "✅ Network cleanup complete!"
echo "========================================"
echo ""
echo "💡 Now try running: ./scripts/start_databases.sh"
echo ""

