#!/bin/bash
# Post-Commit Hook: Check AI Analysis
# Add this to your .git/hooks/post-commit or run manually after commits

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Checking for PR number...${NC}"

# Try to get PR number from current branch
PR_NUMBER=$(git branch --show-current | grep -oE 'pr-?[0-9]+' | grep -oE '[0-9]+' || echo "")

if [ -z "$PR_NUMBER" ]; then
    # Try from commit message
    PR_NUMBER=$(git log -1 --pretty=%B | grep -oE '#[0-9]+' | head -1 | grep -oE '[0-9]+' || echo "")
fi

if [ -z "$PR_NUMBER" ]; then
    echo -e "${YELLOW}⚠️  Could not auto-detect PR number.${NC}"
    echo -e "${YELLOW}💡 Run manually: python scripts/wait_for_ai_analysis.py <PR_NUMBER> --wait${NC}"
    exit 0
fi

echo -e "${GREEN}✅ Found PR #$PR_NUMBER${NC}"
echo -e "${BLUE}⏳ Waiting for AI Analysis...${NC}"

python scripts/wait_for_ai_analysis.py "$PR_NUMBER" --wait












