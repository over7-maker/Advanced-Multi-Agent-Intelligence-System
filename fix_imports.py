#!/usr/bin/env python3
"""
Fix import issues in AMAS codebase
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix imports that should be prefixed with 'amas.'
    replacements = [
        (r'from agents\.', 'from amas.agents.'),
        (r'from services\.', 'from amas.services.'),
        (r'from config\.', 'from amas.config.'),
        (r'from core\.', 'from amas.core.'),
        (r'from api\.', 'from amas.api.'),
        (r'from utils\.', 'from amas.utils.'),
        (r'import agents\.', 'import amas.agents.'),
        (r'import services\.', 'import amas.services.'),
        (r'import config\.', 'import amas.config.'),
        (r'import core\.', 'import amas.core.'),
        (r'import api\.', 'import amas.api.'),
        (r'import utils\.', 'import amas.utils.'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Only write if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Fixed imports in: {file_path}")
        return True
    return False

def main():
    """Main function to fix all imports"""
    print("Fixing imports in AMAS codebase...")
    
    # Find all Python files in src/amas
    src_path = Path(__file__).parent / "src" / "amas"
    python_files = list(src_path.rglob("*.py"))
    
    fixed_count = 0
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1
    
    print(f"\nFixed imports in {fixed_count} files")
    print("Import fixing complete!")

if __name__ == "__main__":
    main()