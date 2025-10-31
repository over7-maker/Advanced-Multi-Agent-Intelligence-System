#!/bin/bash

# Workflow Fixes Application Script
# This script applies the fixes to resolve failing GitHub Actions workflows

set -e

echo "🔧 Applying Workflow Fixes for Advanced Multi-Agent Intelligence System"
echo "=================================================================="

# Create backup directory
echo "📁 Creating backup directory..."
mkdir -p .github/workflows/backup

# Backup original workflows
echo "💾 Backing up original workflows..."
cp .github/workflows/03-ai-agent-project-audit-documentation.yml .github/workflows/backup/ 2>/dev/null || echo "⚠️  Original workflow not found, skipping backup"
cp .github/workflows/02-ai-agentic-issue-auto-responder.yml .github/workflows/backup/ 2>/dev/null || echo "⚠️  Original workflow not found, skipping backup"
cp .github/workflows/04-ai-enhanced-build-deploy.yml .github/workflows/backup/ 2>/dev/null || echo "⚠️  Original workflow not found, skipping backup"
cp .github/workflows/05-ai-security-threat-intelligence.yml .github/workflows/backup/ 2>/dev/null || echo "⚠️  Original workflow not found, skipping backup"

echo "✅ Backups created in .github/workflows/backup/"

# Check if fixed workflows exist
echo "🔍 Checking for fixed workflow files..."
if [ ! -f ".github/workflows/03-ai-agent-project-audit-documentation-fixed.yml" ]; then
    echo "❌ Fixed workflow file not found: 03-ai-agent-project-audit-documentation-fixed.yml"
    exit 1
fi

if [ ! -f ".github/workflows/02-ai-agentic-issue-auto-responder-fixed.yml" ]; then
    echo "❌ Fixed workflow file not found: 02-ai-agentic-issue-auto-responder-fixed.yml"
    exit 1
fi

if [ ! -f ".github/workflows/04-ai-enhanced-build-deploy-fixed.yml" ]; then
    echo "❌ Fixed workflow file not found: 04-ai-enhanced-build-deploy-fixed.yml"
    exit 1
fi

if [ ! -f ".github/workflows/05-ai-security-threat-intelligence-fixed.yml" ]; then
    echo "❌ Fixed workflow file not found: 05-ai-security-threat-intelligence-fixed.yml"
    exit 1
fi

echo "✅ All fixed workflow files found"

# Replace original workflows with fixed versions
echo "🔄 Replacing original workflows with fixed versions..."

# Remove the "-fixed" suffix from the fixed workflows
cp .github/workflows/03-ai-agent-project-audit-documentation-fixed.yml .github/workflows/03-ai-agent-project-audit-documentation.yml
cp .github/workflows/02-ai-agentic-issue-auto-responder-fixed.yml .github/workflows/02-ai-agentic-issue-auto-responder.yml
cp .github/workflows/04-ai-enhanced-build-deploy-fixed.yml .github/workflows/04-ai-enhanced-build-deploy.yml
cp .github/workflows/05-ai-security-threat-intelligence-fixed.yml .github/workflows/05-ai-security-threat-intelligence.yml

echo "✅ Workflows replaced successfully"

# Clean up fixed workflow files
echo "🧹 Cleaning up temporary files..."
rm .github/workflows/*-fixed.yml

echo "✅ Temporary files removed"

# Verify the changes
echo "🔍 Verifying changes..."
echo "📋 Workflow files in .github/workflows/:"
ls -la .github/workflows/*.yml | grep -E "(03-ai-agent-project-audit-documentation|02-ai-agentic-issue-auto-responder|04-ai-enhanced-build-deploy|05-ai-security-threat-intelligence)"

echo ""
echo "🎉 Workflow fixes applied successfully!"
echo ""
echo "📊 Summary of changes:"
echo "  ✅ Simplified dependency installation"
echo "  ✅ Added comprehensive error handling"
echo "  ✅ Reduced timeout values"
echo "  ✅ Added fallback result generation"
echo "  ✅ Original workflows backed up to .github/workflows/backup/"
echo ""
echo "🚀 The workflows should now run more reliably and provide better error reporting."
echo "📝 Check the WORKFLOW_FIXES_SUMMARY.md file for detailed information about the changes."
echo ""
echo "Next steps:"
echo "  1. Commit these changes to your repository"
echo "  2. Monitor the workflows to ensure they're working correctly"
echo "  3. Check the workflow logs for any remaining issues"
echo ""
echo "🔧 Workflow fixes complete!"