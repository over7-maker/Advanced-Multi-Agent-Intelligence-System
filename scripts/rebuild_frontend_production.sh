#!/bin/bash
# Script to rebuild frontend with all latest changes for production

set -e

echo "========================================"
echo "🔄 Rebuilding Frontend for Production"
echo "========================================"
echo ""

cd "$(dirname "$0")/../frontend"

echo "📦 Step 1: Cleaning old build..."
if [ -d "dist" ]; then
    rm -rf dist
    echo "✅ Old build removed"
else
    echo "ℹ️  No old build found"
fi

echo ""
echo "📦 Step 2: Installing dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"

echo ""
echo "🔨 Step 3: Building frontend..."
npm run build:prod
if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi
echo "✅ Build completed successfully"

echo ""
echo "📊 Step 4: Verifying build..."
if [ -f "dist/index.html" ]; then
    echo "✅ index.html found"
else
    echo "❌ index.html not found!"
    exit 1
fi

if [ -d "dist/assets" ]; then
    echo "✅ Assets directory found"
else
    echo "⚠️  Assets directory not found"
fi

echo ""
echo "========================================"
echo "✅ Frontend rebuild complete!"
echo "========================================"
echo ""
echo "📍 Build location: frontend/dist"
echo "🌐 To preview: cd frontend && npm run preview"
echo "🚀 Or access via backend: http://localhost:8000"
echo ""

