#!/bin/bash

# Create Pull Request for AMAS Project Cleanup
# This script creates a comprehensive PR for the project cleanup

echo "🚀 Creating Pull Request for AMAS Project Cleanup..."

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed. Please install it first:"
    echo "   https://cli.github.com/"
    exit 1
fi

# Check if user is logged in to GitHub
if ! gh auth status &> /dev/null; then
    echo "❌ Not logged in to GitHub. Please run: gh auth login"
    exit 1
fi

# Create the Pull Request
echo "📝 Creating Pull Request..."

gh pr create \
  --title "🧹 MAJOR CLEANUP: Remove Ugly Files & Implement Best Practices" \
  --body-file PR_TEMPLATE.md \
  --base main \
  --head cursor/refactor-and-clean-project-for-best-practices-0dd6 \
  --label "enhancement,cleanup,refactoring" \
  --assignee @me

echo "✅ Pull Request created successfully!"
echo "🔗 View your PR at: https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/pulls"