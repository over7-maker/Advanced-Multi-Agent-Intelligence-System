#!/bin/bash
# AMAS Offline Docker Startup

echo "🔒 Starting AMAS Offline System with Docker..."
echo "=============================================="

# Start offline services
docker-compose -f docker-compose-offline.yml up -d

echo "✅ AMAS Offline System started with Docker"
echo "🌐 Access: http://localhost:8000"
echo "📊 Health: http://localhost:8000/health"
