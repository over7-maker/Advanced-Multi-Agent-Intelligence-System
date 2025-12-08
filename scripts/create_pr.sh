#!/bin/bash
# Bash script to create PR on GitHub
# Usage: bash scripts/create_pr.sh

set -e

echo "🚀 Creating Pull Request..."

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI not found. Please install it first."
    echo "Install: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "⚠️  Not authenticated. Please run: gh auth login"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📌 Current branch: $CURRENT_BRANCH"

# Check if branch exists on remote
if git ls-remote --heads origin "$CURRENT_BRANCH" | grep -q "$CURRENT_BRANCH"; then
    echo "✅ Branch already exists on remote"
else
    echo "📤 Pushing branch to remote..."
    git push -u origin "$CURRENT_BRANCH"
fi

# Create PR
echo "📝 Creating Pull Request..."
PR_TITLE="feat: Complete AMAS Integration Verification & Improvements"

if [ -f "PR_DESCRIPTION.md" ]; then
    gh pr create \
        --title "$PR_TITLE" \
        --body-file PR_DESCRIPTION.md \
        --base main \
        --head "$CURRENT_BRANCH"
else
    gh pr create \
        --title "$PR_TITLE" \
        --body "Complete AMAS integration verification and improvements. See PR_DESCRIPTION.md for details." \
        --base main \
        --head "$CURRENT_BRANCH"
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Pull Request created successfully!"
    echo "🔗 View at: https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/pulls"
else
    echo "❌ Failed to create PR"
    exit 1
fi
