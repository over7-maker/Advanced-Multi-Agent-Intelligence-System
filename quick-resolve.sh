#!/bin/bash
# Quick conflict resolution helper for PR #157

echo "🔧 PR #157 Conflict Resolution Helper"
echo "===================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if in merge conflict state
if ! git status | grep -q "You have unmerged paths"; then
    echo -e "${RED}❌ No merge conflict detected!${NC}"
    echo "Are you sure you're in the middle of resolving conflicts?"
    exit 1
fi

echo -e "${GREEN}✓ Merge conflict state detected${NC}"
echo ""

# Show conflicted files
echo -e "${YELLOW}📋 Conflicted files:${NC}"
git diff --name-only --diff-filter=U
echo ""

# Critical reminder
echo -e "${RED}⚠️  CRITICAL REMINDERS:${NC}"
echo "1. Keep PR #157's test improvements (metadata structure)"
echo "2. Use TaskPriority enum (not strings) in tests"
echo "3. Preserve new submit_task signature"
echo "4. Keep async fixture fixes"
echo ""

# Offer quick actions
echo -e "${BLUE}Quick actions available:${NC}"
echo "1. Create backups of all conflicted files"
echo "2. Show example of new task structure"
echo "3. Check for remaining conflict markers"
echo "4. Exit and resolve manually"
echo ""

read -p "Choose action (1-4): " choice

case $choice in
    1)
        echo "Creating backups..."
        mkdir -p conflict-backups
        for f in $(git diff --name-only --diff-filter=U); do
            backup_name="conflict-backups/$(echo $f | tr '/' '_').backup"
            cp "$f" "$backup_name" 2>/dev/null && echo "  ✓ Backed up $f"
        done
        echo -e "${GREEN}Backups created in conflict-backups/${NC}"
        ;;
    
    2)
        echo ""
        echo -e "${YELLOW}OLD task structure (don't use):${NC}"
        cat << 'EOF'
task = await orchestrator.submit_task(
    title="My Task",
    description="Description",
    parameters={"key": "value"},
    priority="high"  # STRING - BAD!
)
EOF
        echo ""
        echo -e "${GREEN}NEW task structure (use this):${NC}"
        cat << 'EOF'
from amas.core.unified_orchestrator_v2 import TaskPriority

task = await orchestrator.submit_task(
    description="Description",
    task_type="analysis", 
    priority=TaskPriority.HIGH,  # ENUM - GOOD!
    metadata={
        "title": "My Task",
        "parameters": {"key": "value"},
        "required_agent_roles": ["analyzer"]
    }
)
EOF
        ;;
    
    3)
        echo "Checking for conflict markers..."
        found=0
        for pattern in "<<<<<<< HEAD" "=======" ">>>>>>>"; do
            if grep -r "$pattern" src/ tests/ README.md 2>/dev/null | head -5; then
                found=1
                echo "  ... (showing first 5 matches)"
            fi
        done
        if [ $found -eq 0 ]; then
            echo -e "${GREEN}✓ No conflict markers found!${NC}"
        else
            echo -e "${RED}⚠️  Conflict markers still present!${NC}"
        fi
        ;;
    
    4)
        echo "Exiting. Resolve conflicts manually using your editor."
        echo ""
        echo "Remember to:"
        echo "  1. Edit each file to resolve conflicts"
        echo "  2. Run: git add <filename> after each file"
        echo "  3. Run: git commit when all are resolved"
        ;;
    
    *)
        echo "Invalid choice"
        ;;
esac

echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Edit each conflicted file"
echo "2. Remove conflict markers (<<<<<<, ======, >>>>>>)"
echo "3. Keep PR #157's test improvements"
echo "4. Run: git add <filename> for each resolved file"
echo "5. Run: git commit to complete the merge"