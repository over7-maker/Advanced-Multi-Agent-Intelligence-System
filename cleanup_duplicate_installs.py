#!/usr/bin/env python3
"""
Cleanup Duplicate Install Commands
Remove duplicate pip install commands that were created by the fix
"""

import os
import re
from pathlib import Path

def cleanup_duplicate_installs(file_path):
    """Clean up duplicate install commands in a workflow file"""
    print(f"🔧 Cleaning up duplicates in {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # Fix 1: Remove duplicate Cython numpy installations
        # Look for patterns like:
        # pip install Cython numpy
        # pip install Cython numpy
        # pip install scikit-learn pandas matplotlib
        
        # Replace multiple consecutive Cython numpy lines with single one
        content = re.sub(
            r'(pip install Cython numpy\n\s*){2,}',
            'pip install Cython numpy\n        ',
            content
        )
        
        # Fix 2: Clean up the build section to be more organized
        if "# Install build dependencies for Cython packages" in content:
            # Find and replace the entire build section
            build_section = """# Install build dependencies for Cython packages
        pip install --upgrade pip setuptools wheel
        pip install Cython numpy
        pip install scikit-learn pandas matplotlib"""
            
            # Replace any variations of this pattern
            content = re.sub(
                r'# Install build dependencies for Cython packages\n\s*pip install --upgrade pip setuptools wheel\n\s*pip install Cython numpy\n\s*pip install Cython numpy\n\s*pip install scikit-learn pandas matplotlib',
                build_section,
                content
            )
            
            changes_made.append("Cleaned up duplicate Cython installations")
        
        # Fix 3: Ensure proper spacing and formatting
        content = re.sub(
            r'(\s+)pip install Cython numpy\n\s+pip install Cython numpy',
            r'\1pip install Cython numpy',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Cleaned {file_path}: {', '.join(changes_made)}")
            return True
        else:
            print(f"ℹ️  No duplicates in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error cleaning {file_path}: {e}")
        return False

def main():
    """Main function to clean up all workflow files"""
    print("🚀 CLEANING UP DUPLICATE INSTALL COMMANDS")
    print("=" * 50)
    print("Removing duplicate pip install commands...")
    print("")
    
    # Find all workflow files
    workflow_dir = Path(".github/workflows")
    workflow_files = list(workflow_dir.glob("*.yml"))
    
    cleaned_count = 0
    total_count = len(workflow_files)
    
    for workflow_file in workflow_files:
        if cleanup_duplicate_installs(workflow_file):
            cleaned_count += 1
    
    print(f"\n🎉 CLEANUP COMPLETED!")
    print("=" * 30)
    print(f"✅ Files processed: {total_count}")
    print(f"✅ Files cleaned: {cleaned_count}")
    print(f"✅ Files unchanged: {total_count - cleaned_count}")
    
    if cleaned_count > 0:
        print("\n🔧 CHANGES MADE:")
        print("• Removed duplicate Cython numpy installations")
        print("• Cleaned up build section formatting")
        print("• Ensured proper spacing and organization")
        print("\n✅ All workflows now have clean, organized install commands!")
    else:
        print("\nℹ️  No duplicates found")
    
    print("\n📱 Ready for mobile viewing!")

if __name__ == "__main__":
    main()