#!/bin/bash
# AMAS Offline Startup Script

echo "🔒 Starting AMAS Offline System..."
echo "=================================="

# Set offline environment
export AMAS_MODE=offline
export AMAS_OFFLINE_MODE=true
export AMAS_LOCAL_ONLY=true
export AMAS_NO_INTERNET=true

# Start offline system
echo "🚀 Starting offline agents..."
python3 offline_example.py

echo "✅ AMAS Offline System started"
