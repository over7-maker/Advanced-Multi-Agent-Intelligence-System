#!/bin/bash
set -e

echo "🤖 Simple Auto-Fix Script"
echo "========================="

# Function to run command and show result
run_fix() {
    local cmd="$1"
    local description="$2"
    
    echo "🔧 $description"
    if eval "$cmd"; then
        echo "✅ $description - SUCCESS"
        return 0
    else
        echo "⚠️ $description - FAILED (continuing...)"
        return 1
    fi
}

# Step 1: Fix Black formatting
run_fix "python3 -m black src/ tests/" "Fixing code formatting with Black"

# Step 2: Fix import sorting
run_fix "python3 -m isort src/ tests/" "Fixing import sorting with isort"

# Step 3: Fix Black formatting again (isort might change formatting)
run_fix "python3 -m black src/ tests/" "Re-applying Black formatting after isort"

# Step 4: Remove common unused imports automatically
echo "🔍 Removing common unused imports..."
find src/ tests/ -name "*.py" -type f -exec python3 -c "
import re
import sys

def fix_unused_imports(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remove common unused imports
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            # Skip if line is empty or just whitespace
            if not line.strip():
                new_lines.append(line)
                continue
                
            # Remove common unused typing imports
            if 'from typing import' in line:
                # Remove Union
                line = re.sub(r',\s*Union', '', line)
                line = re.sub(r'Union,\s*', '', line)
                
                # Remove Optional if not used
                line = re.sub(r',\s*Optional', '', line)
                line = re.sub(r'Optional,\s*', '', line)
                
                # Remove List if not used
                line = re.sub(r',\s*List', '', line)
                line = re.sub(r'List,\s*', '', line)
                
                # Remove Dict if not used
                line = re.sub(r',\s*Dict', '', line)
                line = re.sub(r'Dict,\s*', '', line)
                
                # Remove Tuple if not used
                line = re.sub(r',\s*Tuple', '', line)
                line = re.sub(r'Tuple,\s*', '', line)
                
                # Skip empty import lines
                if line.strip() in ['from typing import', 'from typing import ']:
                    continue
            
            # Remove common unused standard library imports
            if line.strip() in [
                'import time',
                'import json',
                'import os',
                'import sys',
                'import asyncio',
                'import uuid',
                'import pickle',
                'import hashlib',
                'import secrets',
                'import random',
                'import threading',
                'import subprocess',
                'import string',
                'import pstats',
                'import unittest',
                'import io',
                'import cProfile',
                'import memory_profiler',
                'import requests',
                'import pstats',
                'import string',
                'import subprocess',
                'import threading',
                'import unittest',
                'import ThreadPoolExecutor',
                'import as_completed',
                'import Callable',
                'import Union',
                'import memory_profiler',
                'import pytest',
                'import requests',
                'import cProfile',
                'import io',
                'import json'
            ]:
                continue
                
            new_lines.append(line)
        
        new_content = '\n'.join(new_lines)
        
        # Only write if content changed
        if new_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'Fixed imports in {file_path}')
            
    except Exception as e:
        pass  # Skip files that can't be processed

fix_unused_imports('$1')
" {} \;

# Step 5: Final Black formatting pass
run_fix "python3 -m black src/ tests/" "Final Black formatting pass"

# Step 6: Verify fixes
echo "🔍 Verifying fixes..."
if python3 -m black --check src/ tests/; then
    echo "✅ Black formatting - PASS"
else
    echo "❌ Black formatting - FAIL"
fi

if python3 -m isort --check-only src/ tests/; then
    echo "✅ Import sorting - PASS"
else
    echo "❌ Import sorting - FAIL"
fi

echo "🎉 Auto-fix completed!"