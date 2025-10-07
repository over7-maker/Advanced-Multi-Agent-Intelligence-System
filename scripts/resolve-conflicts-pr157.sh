#!/bin/bash
# Script to help resolve merge conflicts for PR #157

echo "🔧 Merge Conflict Resolution Helper for PR #157"
echo "=============================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if we're in a merge conflict state
if ! git status | grep -q "You have unmerged paths"; then
    echo -e "${RED}No merge conflicts detected. Are you in the middle of a merge?${NC}"
    exit 1
fi

echo -e "${YELLOW}Found conflicts in the following files:${NC}"
git status --porcelain | grep "^UU" | awk '{print "  - " $2}'

echo ""
echo -e "${BLUE}Starting conflict resolution process...${NC}"
echo ""

# Function to show conflict details
show_conflict() {
    local file=$1
    echo -e "${YELLOW}Conflicts in $file:${NC}"
    grep -n "<<<<<<< HEAD" "$file" | cut -d: -f1 | while read line; do
        echo "  - Conflict starting at line $line"
    done
}

# Function to create backup
backup_file() {
    local file=$1
    cp "$file" "$file.backup"
    echo -e "${GREEN}✓ Created backup: $file.backup${NC}"
}

# Start resolution process
echo "📋 Conflict Resolution Strategy:"
echo ""
echo "Based on PR #157 (Test Suite Fixes):"
echo "- This PR updates task structures to use metadata field"
echo "- Fixes async fixture handling"
echo "- Updates TaskPriority enum usage"
echo "- Updates mock specifications"
echo ""
echo "General approach:"
echo "1. Keep PR changes for test-related modifications"
echo "2. Merge in new features from main branch"
echo "3. Ensure all imports are preserved"
echo ""

# Process each file
for file in README.md \
           src/amas/__init__.py \
           src/amas/agents/__init__.py \
           src/amas/agents/base/agent_communication.py \
           src/amas/config/settings.py \
           src/amas/core/integration_manager.py \
           src/amas/core/orchestrator.py \
           src/amas/main.py \
           src/amas/services/service_manager.py \
           tests/test_agents.py \
           tests/test_integration.py; do
    
    if [ -f "$file" ]; then
        echo ""
        echo -e "${BLUE}Processing: $file${NC}"
        show_conflict "$file"
        backup_file "$file"
    fi
done

echo ""
echo -e "${YELLOW}Manual resolution required. Here's what to do for each file:${NC}"
echo ""
echo "1. README.md"
echo "   - Keep both versions' content"
echo "   - Merge feature lists"
echo ""
echo "2. src/amas/__init__.py & src/amas/agents/__init__.py"
echo "   - Merge all imports from both versions"
echo "   - Preserve any new modules/classes"
echo ""
echo "3. src/amas/agents/base/agent_communication.py"
echo "   - Keep PR's async fixes"
echo "   - Merge any new methods from main"
echo ""
echo "4. src/amas/config/settings.py"
echo "   - Keep both configuration additions"
echo "   - Ensure no duplicate keys"
echo ""
echo "5. src/amas/core/integration_manager.py & orchestrator.py"
echo "   - Keep PR's task structure updates (metadata field)"
echo "   - Preserve any new features from main"
echo ""
echo "6. src/amas/main.py"
echo "   - Merge initialization code"
echo "   - Keep both versions' features"
echo ""
echo "7. src/amas/services/service_manager.py"
echo "   - Keep PR's async improvements"
echo "   - Merge new services from main"
echo ""
echo "8. tests/test_agents.py & tests/test_integration.py"
echo "   - IMPORTANT: Keep PR's test updates (new task structure)"
echo "   - Add any new tests from main"
echo "   - Ensure TaskPriority enum is used correctly"
echo ""

echo -e "${GREEN}Next steps:${NC}"
echo "1. Open each file in your editor"
echo "2. Look for conflict markers: <<<<<<< HEAD, =======, >>>>>>>"
echo "3. Resolve according to the guidelines above"
echo "4. After resolving, run: git add <filename>"
echo "5. When all resolved, run: git commit"
echo ""

# Offer automated resolution for specific patterns
echo -e "${BLUE}Would you like to try automated resolution helpers? (y/n)${NC}"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Running automated helpers..."
    
    # Create resolution helpers
    cat > resolve_imports.py << 'EOF'
#!/usr/bin/env python3
"""Helper to merge Python imports from conflict markers"""
import sys
import re

def merge_imports(content):
    # Find all imports from both sides of conflicts
    head_imports = set()
    branch_imports = set()
    
    in_head = False
    in_branch = False
    
    lines = content.split('\n')
    result_lines = []
    
    for line in lines:
        if '<<<<<<< HEAD' in line:
            in_head = True
            in_branch = False
            continue
        elif '=======' in line:
            in_head = False
            in_branch = True
            continue
        elif '>>>>>>>' in line:
            in_head = False
            in_branch = False
            continue
        
        if in_head or in_branch:
            if line.strip().startswith(('import ', 'from ')):
                if in_head:
                    head_imports.add(line.strip())
                else:
                    branch_imports.add(line.strip())
        else:
            result_lines.append(line)
    
    # Merge imports
    all_imports = sorted(head_imports.union(branch_imports))
    
    print("Found imports from HEAD:", len(head_imports))
    print("Found imports from branch:", len(branch_imports))
    print("Merged imports:", len(all_imports))
    
    return all_imports

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            imports = merge_imports(f.read())
            print("\nMerged imports:")
            for imp in imports:
                print(imp)
EOF
    
    chmod +x resolve_imports.py
    
    echo -e "${GREEN}✓ Created resolve_imports.py helper${NC}"
    echo "Use: ./resolve_imports.py <filename> to see merged imports"
fi

echo ""
echo -e "${BLUE}Quick reference for manual resolution:${NC}"
echo "- Remove <<<<<<< HEAD"
echo "- Remove ======="
echo "- Remove >>>>>>> branch-name"
echo "- Keep the code you want"
echo ""
echo -e "${YELLOW}Remember: This PR's main goal is fixing the test suite!${NC}"
echo "Prioritize preserving test-related changes while merging new features."

exit 0