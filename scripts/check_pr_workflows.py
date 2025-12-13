#!/usr/bin/env python3
"""
Check PR Workflow Status and Results
View workflow runs, check status, and see AI analysis results
"""

import os
import sys
import subprocess
import json
from typing import Optional

try:
    import requests
except ImportError:
    print("⚠️  Installing requests...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests


def check_gh_cli() -> bool:
    """Check if GitHub CLI is installed"""
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_pr_checks(pr_number: str) -> Optional[str]:
    """Get PR check status using GitHub CLI"""
    try:
        result = subprocess.run(
            ["gh", "pr", "checks", pr_number],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None


def get_workflow_runs(pr_number: Optional[str] = None) -> Optional[str]:
    """Get workflow runs"""
    try:
        cmd = ["gh", "run", "list"]
        if pr_number:
            cmd.extend(["--branch", f"pr-{pr_number}"])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None


def get_pr_info(pr_number: str) -> Optional[dict]:
    """Get PR information"""
    try:
        result = subprocess.run(
            ["gh", "pr", "view", pr_number, "--json", "number,title,state,url,mergeable"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def display_pr_workflow_status(pr_number: str):
    """Display PR workflow status"""
    print(f"\n{'='*80}")
    print(f"🔍 PR #{pr_number} - Workflow Status")
    print(f"{'='*80}\n")
    
    # Get PR info
    pr_info = get_pr_info(pr_number)
    if pr_info:
        print(f"📌 Title: {pr_info.get('title', 'N/A')}")
        print(f"📊 State: {pr_info.get('state', 'N/A')}")
        print(f"🔗 URL: {pr_info.get('url', 'N/A')}")
        print(f"✅ Mergeable: {pr_info.get('mergeable', 'N/A')}")
        print()
    
    # Get checks
    print("🔍 Checking PR status...")
    checks = get_pr_checks(pr_number)
    if checks:
        print(checks)
    else:
        print("⚠️  Could not fetch checks. Make sure GitHub CLI is authenticated.")
    
    # Show workflow runs
    print("\n📋 Recent Workflow Runs:")
    print("-" * 80)
    runs = get_workflow_runs()
    if runs:
        print(runs)
    else:
        print("⚠️  Could not fetch workflow runs")
    
    print("\n💡 To view detailed workflow logs:")
    print("   gh run view <RUN_ID>")
    print("   gh run watch <RUN_ID>")


def main():
    """Main function"""
    if len(sys.argv) < 2 or sys.argv[1] in ["--help", "-h", "help"]:
        print("Usage: python scripts/check_pr_workflows.py <PR_NUMBER>")
        print("\nExample:")
        print("  python scripts/check_pr_workflows.py 3542")
        print("\nThis will show:")
        print("  - PR information")
        print("  - All workflow check statuses")
        print("  - Recent workflow runs")
        print("\nRequirements:")
        print("  - GitHub CLI (gh) must be installed")
        print("  - Install: winget install --id GitHub.cli")
        print("  - Or download: https://cli.github.com/")
        sys.exit(0 if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "help"] else 1)
    
    pr_number = sys.argv[1]
    
    if not check_gh_cli():
        print("❌ GitHub CLI not found!")
        print("\n📥 Install GitHub CLI:")
        print("   Windows: winget install --id GitHub.cli")
        print("   Or download: https://cli.github.com/")
        sys.exit(1)
    
    display_pr_workflow_status(pr_number)


if __name__ == "__main__":
    main()

