#!/usr/bin/env python3
"""
Commit Missing Files - Add and commit missing script files
"""

import subprocess
import os

def run_command(cmd):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    """Main function"""
    print("🔍 Checking for missing script files...")
    
    # Check git status
    success, stdout, stderr = run_command("git status --porcelain")
    if success:
        print("Git status:")
        print(stdout)
    else:
        print(f"Error checking git status: {stderr}")
    
    # Check if the specific file exists
    success, stdout, stderr = run_command("ls -la .github/scripts/ai_quality_performance_final_summary.py")
    if success:
        print("File exists locally:")
        print(stdout)
    else:
        print(f"File doesn't exist: {stderr}")
    
    # Try to add the file
    success, stdout, stderr = run_command("git add .github/scripts/ai_quality_performance_final_summary.py")
    if success:
        print("Successfully added file to git")
    else:
        print(f"Error adding file: {stderr}")
    
    # Check status again
    success, stdout, stderr = run_command("git status --porcelain")
    if success:
        print("Git status after add:")
        print(stdout)
    else:
        print(f"Error checking git status: {stderr}")
    
    # Try to commit
    success, stdout, stderr = run_command("git commit -m 'Fix: Add missing ai_quality_performance_final_summary.py script'")
    if success:
        print("Successfully committed file")
    else:
        print(f"Error committing file: {stderr}")

if __name__ == "__main__":
    main()