#!/bin/bash
# Quick script to start the React Dashboard

echo "🚀 Starting AMAS React Dashboard..."
echo ""

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start dev server
echo "🔥 Starting Vite dev server..."
echo ""
echo "✅ Dashboard will be available at: http://localhost:3000"
echo "   (or http://localhost:3001 if 3000 is busy)"
echo ""
echo "📋 What you should see:"
echo "   - '🤖 AMAS Intelligence Dashboard' title"
echo "   - Material-UI dark theme"
echo "   - Active Workflows section"
echo "   - Agent Status Grid"
echo "   - Performance Metrics"
echo "   - Recent Activity"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev

