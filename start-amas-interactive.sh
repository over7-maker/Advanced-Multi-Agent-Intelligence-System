#!/bin/bash
# Quick start script for AMAS Interactive Mode

echo "🚀 Starting AMAS Interactive Mode - Next Generation..."
cd "$(dirname "$0")"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Check if simplified interactive module exists
if [ -f "simple-amas-interactive.py" ]; then
    echo "✅ Interactive module found"
    python3 simple-amas-interactive.py
else
    echo "❌ Interactive module not found. Please run setup script first."
    exit 1
fi