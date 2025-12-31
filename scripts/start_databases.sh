#!/bin/bash
# Script to start all databases (PostgreSQL, Redis, Neo4j) using Docker Compose

set -e

echo "========================================"
echo "🗄️  Starting AMAS Databases"
echo "========================================"
echo ""

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "💡 Please start Docker and try again."
    exit 1
fi

# Check if network exists
echo "🔍 Checking Docker network..."
if docker network inspect advanced-multi-agent-intelligence-system_amas-network > /dev/null 2>&1; then
    echo "ℹ️  Network already exists"
else
    echo "ℹ️  Network does not exist, will be created"
fi

# Try to start databases
echo "📦 Starting PostgreSQL, Redis, and Neo4j..."
if ! docker-compose up -d postgres redis neo4j; then
    echo ""
    echo "⚠️  Failed to start databases. Trying to fix network issue..."
    echo ""
    echo "🔧 Attempting to remove conflicting network..."
    docker network rm advanced-multi-agent-intelligence-system_amas-network 2>/dev/null || true
    
    echo "🔄 Retrying database startup..."
    if ! docker-compose up -d postgres redis neo4j; then
        echo ""
        echo "❌ Failed to start databases after retry"
        echo ""
        echo "💡 Try manually:"
        echo "   1. docker network prune"
        echo "   2. docker-compose up -d postgres redis neo4j"
        exit 1
    fi
fi

echo ""
echo "⏳ Waiting for databases to be ready..."
sleep 15

echo ""
echo "✅ Checking database status..."
docker-compose ps postgres redis neo4j

echo ""
echo "========================================"
echo "✅ Databases Started!"
echo "========================================"
echo ""
echo "📊 Database Status:"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo "   - Neo4j: localhost:7687 (Web UI: http://localhost:7474)"
echo ""
echo "💡 To view logs: docker-compose logs -f postgres redis neo4j"
echo "💡 To stop: docker-compose stop postgres redis neo4j"
echo ""

