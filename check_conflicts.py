#!/usr/bin/env python3
"""
Check for merge conflict markers in workflow files
"""

import os
import re
from pathlib import Path

def check_conflicts():
    """Check for merge conflict markers in workflow files"""
    workflow_dir = Path(".github/workflows")
    conflict_markers = [
        "<<<<<<< ",
        "=======",
        ">>>>>>> "
    ]
    
    conflicts_found = []
    
    if workflow_dir.exists():
        for yml_file in workflow_dir.glob("*.yml"):
            try:
                with open(yml_file, 'r') as f:
                    content = f.read()
                
                for marker in conflict_markers:
                    if marker in content:
                        conflicts_found.append(f"{yml_file.name}: Contains {marker}")
                        
            except Exception as e:
                print(f"Error reading {yml_file}: {e}")
    
    if conflicts_found:
        print("❌ CONFLICTS FOUND:")
        for conflict in conflicts_found:
            print(f"  - {conflict}")
        return False
    else:
        print("✅ NO CONFLICTS FOUND - All files are clean!")
        return True

if __name__ == "__main__":
    check_conflicts()