#!/usr/bin/env python3
"""
GitHub Synchronization Script
Syncs local repository with GitHub, ensuring complete synchronization.
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import List, Tuple

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

def fetch_from_github() -> bool:
    """Fetch latest changes from GitHub."""
    print("🔄 Fetching latest changes from GitHub...")
    returncode, stdout, stderr = run_command(["git", "fetch", "origin"], check=False)
    if returncode == 0:
        print("✅ Successfully fetched from GitHub")
        return True
    else:
        print(f"❌ Failed to fetch: {stderr}")
        return False

def pull_latest_changes() -> bool:
    """Pull latest changes from current branch."""
    branch = get_current_branch()
    print(f"📥 Pulling latest changes from origin/{branch}...")
    returncode, stdout, stderr = run_command(["git", "pull", "origin", branch], check=False)
    if returncode == 0:
        print("✅ Successfully pulled latest changes")
        print(stdout)
        return True
    else:
        print(f"⚠️  Pull had conflicts or issues: {stderr}")
        return False

def get_remote_branches() -> List[str]:
    """Get list of remote branches."""
    returncode, stdout, _ = run_command(["git", "branch", "-r"], check=False)
    if returncode == 0:
        branches = [b.strip().replace("origin/", "") for b in stdout.split("\n") if b.strip()]
        return [b for b in branches if not b.startswith("HEAD")]
    return []

def sync_all_branches() -> bool:
    """Sync all remote branches locally."""
    print("🌿 Syncing all remote branches...")
    remote_branches = get_remote_branches()
    print(f"Found {len(remote_branches)} remote branches")
    
    for branch in remote_branches:
        if branch == "HEAD":
            continue
        print(f"  📦 Syncing branch: {branch}")
        returncode, _, stderr = run_command(
            ["git", "fetch", "origin", f"{branch}:refs/remotes/origin/{branch}"],
            check=False
        )
        if returncode != 0:
            print(f"    ⚠️  Warning: Could not sync {branch}: {stderr}")
    
    return True

def check_uncommitted_changes() -> bool:
    """Check if there are uncommitted changes."""
    returncode, stdout, _ = run_command(["git", "status", "--porcelain"], check=False)
    if returncode == 0:
        return len(stdout.strip()) > 0
    return False

def stash_changes() -> bool:
    """Stash uncommitted changes."""
    print("💾 Stashing uncommitted changes...")
    returncode, stdout, stderr = run_command(["git", "stash"], check=False)
    if returncode == 0:
        print("✅ Changes stashed")
        return True
    else:
        print(f"⚠️  Could not stash: {stderr}")
        return False

def main():
    """Main synchronization function."""
    print("=" * 60)
    print("🚀 GitHub Synchronization Script")
    print("=" * 60)
    
    # Check if we're in a git repository
    if not check_git_status():
        print("❌ Error: Not in a git repository!")
        sys.exit(1)
    
    # Show current branch
    branch = get_current_branch()
    print(f"📍 Current branch: {branch}")
    
    # Check for uncommitted changes
    if check_uncommitted_changes():
        print("⚠️  Warning: You have uncommitted changes!")
        response = input("Would you like to stash them? (y/n): ").strip().lower()
        if response == 'y':
            if not stash_changes():
                print("❌ Failed to stash changes. Aborting.")
                sys.exit(1)
        else:
            print("⚠️  Continuing with uncommitted changes...")
    
    # Fetch from GitHub
    if not fetch_from_github():
        print("⚠️  Warning: Could not fetch from GitHub. Continuing anyway...")
    
    # Sync all branches
    sync_all_branches()
    
    # Pull latest changes for current branch
    if not pull_latest_changes():
        print("⚠️  Warning: Could not pull latest changes. You may need to resolve conflicts manually.")
    
    # Show final status
    print("\n" + "=" * 60)
    print("📊 Final Status:")
    print("=" * 60)
    returncode, stdout, _ = run_command(["git", "status"], check=False)
    print(stdout)
    
    print("\n✅ Synchronization complete!")
    print("\n💡 Next steps:")
    print("   1. Review any conflicts or changes")
    print("   2. Install/update dependencies: pip install -r requirements.txt")
    print("   3. Run local workflow tests: python scripts/run_local_workflows.py")

if __name__ == "__main__":
    main()


