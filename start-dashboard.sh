#!/bin/bash
# Start AMAS Dashboard

echo "🎨 Starting AMAS Control Center Dashboard..."

# Check if web directory exists
if [ ! -d "web" ]; then
    echo "❌ Web directory not found. Run setup-dashboard.sh first."
    exit 1
fi

cd web

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start development server
echo "🚀 Starting React development server..."
echo ""
echo "🌐 Dashboard will be available at: http://localhost:3000"
echo "📊 API should be running at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the dashboard"

npm start