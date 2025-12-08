#!/usr/bin/env python3
"""
Sync Local Changes to GitHub
Commits and pushes local changes to GitHub repository.
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

def run_command(cmd: List[str], check: bool = True) -> Tuple[int, str, str]:
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr

def check_git_status() -> bool:
    """Check if we're in a git repository."""
    returncode, _, _ = run_command(["git", "status"], check=False)
    return returncode == 0

def get_current_branch() -> str:
    """Get current git branch."""
    returncode, stdout, _ = run_command(["git", "branch", "--show-current"], check=False)
    if returncode == 0:
        return stdout.strip()
    return "unknown"

def get_uncommitted_files() -> List[str]:
    """Get list of uncommitted files."""
    returncode, stdout, _ = run_command(["git", "status", "--porcelain"], check=False)
    if returncode == 0:
        files = [line.strip().split()[-1] for line in stdout.split('\n') if line.strip()]
        return files
    return []

def stage_files(files: List[str] = None) -> bool:
    """Stage files for commit."""
    if files is None:
        # Stage all changes
        returncode, stdout, stderr = run_command(["git", "add", "."], check=False)
    else:
        # Stage specific files
        returncode, stdout, stderr = run_command(["git", "add"] + files, check=False)
    
    if returncode == 0:
        print("✅ Files staged successfully")
        return True
    else:
        print(f"❌ Failed to stage files: {stderr}")
        return False

def commit_changes(message: str = None) -> bool:
    """Commit staged changes."""
    if message is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Local development updates - {timestamp}"
    
    returncode, stdout, stderr = run_command(
        ["git", "commit", "-m", message],
        check=False
    )
    
    if returncode == 0:
        print(f"✅ Changes committed: {message}")
        return True
    else:
        print(f"⚠️  Commit status: {stderr}")
        return False

def push_to_github(branch: str = None) -> bool:
    """Push changes to GitHub."""
    if branch is None:
        branch = get_current_branch()
    
    print(f"📤 Pushing to origin/{branch}...")
    returncode, stdout, stderr = run_command(
        ["git", "push", "origin", branch],
        check=False
    )
    
    if returncode == 0:
        print("✅ Successfully pushed to GitHub")
        return True
    else:
        print(f"❌ Failed to push: {stderr}")
        return False

def check_remote_status() -> bool:
    """Check if local is ahead/behind remote."""
    returncode, stdout, _ = run_command(["git", "status"], check=False)
    if returncode == 0:
        if "Your branch is ahead" in stdout:
            print("📍 Local branch is ahead of remote")
            return True
        elif "Your branch is behind" in stdout:
            print("⚠️  Warning: Local branch is behind remote. Consider pulling first.")
            return False
        else:
            print("📍 Local and remote are in sync")
            return True
    return False

def main():
    """Main synchronization function."""
    print("=" * 60)
    print("🚀 Sync Local Changes to GitHub")
    print("=" * 60)
    
    # Check if we're in a git repository
    if not check_git_status():
        print("❌ Error: Not in a git repository!")
        sys.exit(1)
    
    # Show current branch
    branch = get_current_branch()
    print(f"📍 Current branch: {branch}")
    
    # Check for uncommitted files
    uncommitted = get_uncommitted_files()
    if not uncommitted:
        print("✅ No uncommitted changes")
        # Still check if we need to push
        if check_remote_status():
            response = input("\nPush existing commits? (y/n): ").strip().lower()
            if response == 'y':
                push_to_github()
        sys.exit(0)
    
    print(f"\n📋 Found {len(uncommitted)} uncommitted files:")
    for file in uncommitted[:10]:  # Show first 10
        print(f"   - {file}")
    if len(uncommitted) > 10:
        print(f"   ... and {len(uncommitted) - 10} more")
    
    # Ask for confirmation
    response = input("\nStage and commit these changes? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Aborted by user")
        sys.exit(0)
    
    # Stage files
    if not stage_files():
        print("❌ Failed to stage files")
        sys.exit(1)
    
    # Get commit message
    print("\n💬 Commit message:")
    print("   (Press Enter for auto-generated message, or type custom message)")
    message = input("   Message: ").strip()
    if not message:
        message = None
    
    # Commit
    if not commit_changes(message):
        print("⚠️  Commit had issues, but continuing...")
    
    # Ask about pushing
    response = input("\nPush to GitHub? (y/n): ").strip().lower()
    if response == 'y':
        if not push_to_github():
            print("❌ Failed to push. You may need to:")
            print("   1. Pull latest changes first: git pull origin " + branch)
            print("   2. Resolve any conflicts")
            print("   3. Try pushing again")
            sys.exit(1)
    else:
        print("✅ Changes committed locally. Push manually when ready.")
    
    print("\n✅ Synchronization complete!")

if __name__ == "__main__":
    main()


