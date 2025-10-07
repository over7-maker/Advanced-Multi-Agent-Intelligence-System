#!/bin/bash
# Script to fix CI pipeline issues for PR #157

echo "🔧 CI Pipeline Fix Script"
echo "========================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d ".github/workflows" ]; then
    echo -e "${RED}Error: .github/workflows directory not found${NC}"
    echo "Please run this script from the repository root"
    exit 1
fi

echo -e "${YELLOW}This script will fix the GitHub Actions CI pipeline issues${NC}"
echo "1. Update deprecated GitHub Actions to v4"
echo "2. Fix pip installation issue"
echo "3. Improve workflow reliability"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Backup existing workflow
if [ -f ".github/workflows/quality-gate.yml" ]; then
    echo -e "${YELLOW}Backing up existing workflow...${NC}"
    cp .github/workflows/quality-gate.yml .github/workflows/quality-gate.yml.backup
    echo -e "${GREEN}✓ Backup created: .github/workflows/quality-gate.yml.backup${NC}"
fi

# Choose workflow version
echo ""
echo "Which workflow version would you like to use?"
echo "1) Complete version (recommended) - comprehensive with all checks"
echo "2) Minimal version - basic functionality only"
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo -e "${YELLOW}Installing complete workflow...${NC}"
        if [ -f ".github/workflows/quality-gate-complete-fix.yml" ]; then
            cp .github/workflows/quality-gate-complete-fix.yml .github/workflows/quality-gate.yml
        else
            echo -e "${RED}Error: quality-gate-complete-fix.yml not found${NC}"
            exit 1
        fi
        ;;
    2)
        echo -e "${YELLOW}Installing minimal workflow...${NC}"
        if [ -f ".github/workflows/quality-gate-minimal.yml" ]; then
            cp .github/workflows/quality-gate-minimal.yml .github/workflows/quality-gate.yml
        else
            echo -e "${RED}Error: quality-gate-minimal.yml not found${NC}"
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}✓ Workflow updated successfully${NC}"

# Create git commit
echo ""
echo -e "${YELLOW}Creating git commit...${NC}"

# Check if there are changes
if git diff --quiet .github/workflows/quality-gate.yml; then
    echo -e "${YELLOW}No changes detected. Workflow may already be up to date.${NC}"
else
    # Add the file
    git add .github/workflows/quality-gate.yml
    
    # Use the prepared commit message
    if [ -f "ci-fix-commit-message.txt" ]; then
        git commit -F ci-fix-commit-message.txt
    else
        git commit -m "fix: Update GitHub Actions workflow to resolve CI failures

- Upgrade deprecated actions to v4
- Fix pip installation issue
- Improve workflow reliability"
    fi
    
    echo -e "${GREEN}✓ Commit created${NC}"
    
    # Ask about pushing
    echo ""
    read -p "Push changes to remote? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push
        echo -e "${GREEN}✓ Changes pushed to remote${NC}"
        echo ""
        echo -e "${GREEN}Success! The CI pipeline should now work correctly.${NC}"
        echo "Check the Actions tab on GitHub to monitor the workflow run."
    else
        echo -e "${YELLOW}Changes committed locally. Run 'git push' when ready.${NC}"
    fi
fi

echo ""
echo "🎉 CI Pipeline fix complete!"
echo ""
echo "Next steps:"
echo "1. Check GitHub Actions tab for workflow status"
echo "2. Verify all checks pass (some warnings are normal)"
echo "3. Once CI passes, the PR can be merged"

# Clean up temporary files
rm -f get-pip.py

exit 0