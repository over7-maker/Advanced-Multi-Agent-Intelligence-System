#!/bin/bash
# Quick Node.js Installation Script

echo "🔧 Installing Node.js 18.x and npm..."
echo ""

# Update package list
echo "📦 Updating package list..."
apt-get update -qq

# Install Node.js and npm
echo "📦 Installing Node.js and npm..."
apt-get install -y nodejs npm

# Verify installation
echo ""
echo "✅ Installation complete!"
echo ""
node --version
npm --version

echo ""
echo "🚀 Now you can run:"
echo "   cd frontend"
echo "   npm install"
echo "   npm run dev"

