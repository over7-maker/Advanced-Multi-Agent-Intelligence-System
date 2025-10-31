#!/bin/bash

# Setup Bulletproof AI System for Phase 2 PR Analysis
echo "🚀 Setting up Bulletproof AI System for Phase 2..."

# Make scripts executable
chmod +x .github/scripts/bulletproof_ai_pr_analyzer.py

# Test the universal AI manager
echo "🧪 Testing Universal AI Manager..."
python3 standalone_universal_ai_manager.py

# Test the bulletproof analyzer
echo "🧪 Testing Bulletproof AI Analyzer..."
cd .github/scripts
python3 bulletproof_ai_pr_analyzer.py
cd ../..

echo "✅ Bulletproof AI System setup complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Ensure at least one AI provider API key is configured"
echo "2. Create a PR to trigger the bulletproof analysis workflow"
echo "3. Use the kickoff comment template to run @amas commands"
echo ""
echo "🎯 Ready for Phase 2 PR analysis with bulletproof AI validation!"
