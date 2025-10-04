#!/bin/bash
# AMAS Intelligence System Startup Script

set -e

echo "🚀 Starting AMAS Intelligence System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data/vector_index data/knowledge_graph data/models data/workflows

# Set permissions
chmod +x scripts/*.py

# Start services with Docker Compose
echo "🐳 Starting Docker services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
python scripts/health_check.py

# Display access information
echo ""
echo "✅ AMAS Intelligence System is running!"
echo ""
echo "🌐 Access Points:"
echo "   Web Interface: http://localhost:3000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   n8n Workflows: http://localhost:5678"
echo "   Grafana Monitoring: http://localhost:3001"
echo "   Neo4j Browser: http://localhost:7474"
echo ""
echo "📊 System Status:"
echo "   Agents: 8 specialized intelligence agents"
echo "   Services: Ollama, Vector, Graph, Redis, PostgreSQL"
echo "   Workflows: n8n automation engine"
echo "   Monitoring: Prometheus + Grafana"
echo ""
echo "🛠️  CLI Commands:"
echo "   python scripts/cli.py --help"
echo "   python scripts/health_check.py"
echo "   python main.py"
echo ""
echo "📚 Documentation:"
echo "   README.md - Complete setup guide"
echo "   docs/ - Technical documentation"
echo "   examples/ - Usage examples"
echo ""
echo "🎯 Ready for intelligence operations!"