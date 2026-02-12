#!/bin/bash
# Script to restart Neo4j container to reset authentication rate limit

echo "========================================"
echo "🔄 Restarting Neo4j Container"
echo "========================================"
echo ""

echo "📍 Checking Neo4j container status..."
docker ps --filter "name=neo4j" --format "{{.Names}}\t{{.Status}}"

echo ""
echo "🔄 Restarting Neo4j container..."

# Try to restart using container name
if docker restart advanced-multi-agent-intelligence-system-neo4j-1 2>/dev/null; then
    echo "✅ Neo4j container restarted successfully"
elif docker-compose restart neo4j 2>/dev/null; then
    echo "✅ Neo4j service restarted successfully"
else
    echo "❌ Failed to restart Neo4j"
    echo "💡 Try manually: docker restart <neo4j-container-name>"
    exit 1
fi

echo ""
echo "⏳ Waiting for Neo4j to start (10 seconds)..."
sleep 10

echo ""
echo "📍 Checking Neo4j status after restart..."
docker ps --filter "name=neo4j" --format "{{.Names}}\t{{.Status}}"

echo ""
echo "========================================"
echo "✅ Neo4j restart complete!"
echo "========================================"
echo ""
echo "💡 Note: Wait 10-15 seconds before restarting the backend"
echo "   to allow Neo4j to fully initialize."
echo ""

