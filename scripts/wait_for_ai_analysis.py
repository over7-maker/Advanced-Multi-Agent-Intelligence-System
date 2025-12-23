#!/usr/bin/env python3
"""
Wait for AI Analysis and Show Results
Automatically monitors PR for BULLETPROOF REAL AI Analysis completion
after commits and displays results when ready.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

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


def get_pr_number() -> Optional[str]:
    """Get current PR number from git branch or user input"""
    try:
        # Try to get PR number from branch name
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True
        )
        branch = result.stdout.strip()
        
        # Check if branch name contains PR number
        if "pr-" in branch.lower() or "pull" in branch.lower():
            # Extract number from branch name
            import re
            match = re.search(r'(\d+)', branch)
            if match:
                return match.group(1)
        
        # Try to get from git remote
        result = subprocess.run(
            ["git", "log", "--oneline", "-1", "--grep", "#"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout:
            match = re.search(r'#(\d+)', result.stdout)
            if match:
                return match.group(1)
        
        return None
    except Exception:
        return None


def get_pr_comments_api(pr_number: str, repo: str = "over7-maker/Advanced-Multi-Agent-Intelligence-System") -> List[Dict]:
    """Get PR comments using GitHub API"""
    token = os.environ.get("GITHUB_TOKEN")
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    headers["Accept"] = "application/vnd.github.v3+json"
    
    comments = []
    
    # Get PR review comments
    try:
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        comments.extend(response.json())
    except requests.RequestException as e:
        print(f"⚠️  Error fetching PR comments: {e}")
    
    # Get issue comments (PR comments are also issue comments)
    try:
        url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        comments.extend(response.json())
    except requests.RequestException as e:
        print(f"⚠️  Error fetching issue comments: {e}")
    
    return comments


def get_pr_comments_gh_cli(pr_number: str) -> List[Dict]:
    """Get PR comments using GitHub CLI"""
    try:
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            ["gh", "pr", "view", pr_number, "--json", "comments"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env,
            check=True
        )
        
        if result.stdout is None or not result.stdout.strip():
            return []
        
        pr_data = json.loads(result.stdout)
        return pr_data.get("comments", [])
    except Exception as e:
        print(f"⚠️  Error fetching comments via CLI: {e}")
        return []


def get_pr_comments(pr_number: str) -> List[Dict]:
    """Get PR comments using best available method (CLI or API)"""
    # Try GitHub CLI first
    if check_gh_cli():
        try:
            comments = get_pr_comments_gh_cli(pr_number)
            if comments:
                return comments
        except Exception:
            pass
    
    # Fallback to GitHub API
    return get_pr_comments_api(pr_number)


def get_workflow_runs(pr_number: str) -> List[Dict]:
    """Get workflow runs for PR"""
    # Only works with GitHub CLI
    if not check_gh_cli():
        return []
    
    try:
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            ["gh", "run", "list", "--limit", "10", "--json", "databaseId,name,status,conclusion,headBranch"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env,
            check=True
        )
        
        if result.stdout is None or not result.stdout.strip():
            return []
        
        runs = json.loads(result.stdout)
        # Filter for AI analysis workflows
        ai_workflows = [
            run for run in runs
            if any(keyword in run.get("name", "").lower() for keyword in ["ai", "analysis", "bulletproof"])
        ]
        return ai_workflows
    except Exception as e:
        print(f"⚠️  Error fetching workflows: {e}")
        return []


def has_ai_analysis_comment(comments: List[Dict]) -> bool:
    """Check if PR has BULLETPROOF REAL AI Analysis comment"""
    for comment in comments:
        body = comment.get("body", "").lower()
        if "bulletproof real ai analysis" in body or "bulletproof" in body:
            return True
    return False


def find_ai_analysis_comments(comments: List[Dict]) -> List[Dict]:
    """Find all AI analysis comments"""
    ai_comments = []
    for comment in comments:
        body = comment.get("body", "")
        if "BULLETPROOF REAL AI Analysis" in body or "bulletproof" in body.lower():
            ai_comments.append(comment)
    return ai_comments


def display_ai_analysis(comments: List[Dict]):
    """Display AI analysis comments in a formatted way"""
    if not comments:
        print("\n❌ No AI analysis comments found yet.")
        return
    
    print("\n" + "="*80)
    print("🤖 BULLETPROOF REAL AI Analysis Results")
    print("="*80)
    
    for i, comment in enumerate(comments, 1):
        # Handle both GitHub CLI format (author.login) and API format (user.login)
        author_obj = comment.get("author") or comment.get("user", {})
        author = author_obj.get("login", "Unknown") if isinstance(author_obj, dict) else "Unknown"
        
        # Handle both createdAt (CLI) and created_at (API)
        created = comment.get("createdAt") or comment.get("created_at", "")
        body = comment.get("body", "")
        
        print(f"\n📊 Analysis #{i}")
        print(f"👤 Author: {author}")
        print(f"🕐 Created: {created}")
        print("-"*80)
        
        # Extract key sections
        lines = body.split('\n')
        in_section = False
        section_lines = []
        
        for line in lines:
            if "##" in line or "**" in line or "✅" in line or "❌" in line or "⚠️" in line:
                if section_lines:
                    print('\n'.join(section_lines))
                    section_lines = []
                print(line)
                in_section = True
            elif in_section or line.strip():
                section_lines.append(line)
        
        if section_lines:
            print('\n'.join(section_lines))
        
        print("-"*80)
    
    print("\n" + "="*80)


def wait_for_ai_analysis(pr_number: str, max_wait_minutes: int = 30, check_interval: int = 30):
    """
    Wait for AI analysis to complete and show results
    
    Args:
        pr_number: PR number to monitor
        max_wait_minutes: Maximum time to wait in minutes
        check_interval: Check interval in seconds
    """
    print(f"\n🔍 Monitoring PR #{pr_number} for AI Analysis...")
    print(f"⏱️  Will check every {check_interval} seconds (max {max_wait_minutes} minutes)")
    print("Press Ctrl+C to stop monitoring and show current status\n")
    
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60
    last_comment_count = 0
    
    try:
        while True:
            elapsed = time.time() - start_time
            
            if elapsed > max_wait_seconds:
                print(f"\n⏰ Timeout reached ({max_wait_minutes} minutes)")
                break
            
            # Check for comments
            comments = get_pr_comments(pr_number)
            ai_comments = find_ai_analysis_comments(comments)
            
            # Check if new comments appeared
            if len(ai_comments) > last_comment_count:
                print(f"\n✅ New AI Analysis Found! ({len(ai_comments)} total)")
                display_ai_analysis(ai_comments)
                
                # Check if analysis is complete
                workflow_runs = get_workflow_runs(pr_number)
                completed = [r for r in workflow_runs if r.get("status") == "completed"]
                
                if completed:
                    print(f"\n✅ Workflow completed! Found {len(completed)} completed AI analysis runs.")
                    print("\n📋 Summary:")
                    for run in completed:
                        conclusion = run.get("conclusion", "unknown")
                        status_icon = "✅" if conclusion == "success" else "❌" if conclusion == "failure" else "⚠️"
                        print(f"  {status_icon} {run.get('name', 'Unknown')}: {conclusion}")
                
                print("\n🎯 AI Analysis Complete! Review the results above.")
                return True
            
            # Check workflow status
            workflow_runs = get_workflow_runs(pr_number)
            running = [r for r in workflow_runs if r.get("status") == "in_progress" or r.get("status") == "queued"]
            
            if running:
                print(f"⏳ AI workflows running: {len(running)} active workflows...")
            elif ai_comments:
                print(f"✅ AI Analysis comments found ({len(ai_comments)}), but still checking for updates...")
            else:
                print(f"⏳ Waiting for AI Analysis... ({int(elapsed)}s elapsed)")
            
            time.sleep(check_interval)
            last_comment_count = len(ai_comments)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped by user")
        # Show current status
        comments = get_pr_comments(pr_number)
        ai_comments = find_ai_analysis_comments(comments)
        
        if ai_comments:
            print("\n📊 Current AI Analysis Status:")
            display_ai_analysis(ai_comments)
        else:
            print("\n⚠️  No AI analysis comments found yet.")
            print("💡 You can check manually with: python scripts/view_pr_comments.py", pr_number)
        
        return False


def main():
    """Main entry point"""
    # Check if we have GitHub CLI or API token
    has_cli = check_gh_cli()
    has_token = bool(os.environ.get("GITHUB_TOKEN"))
    
    if not has_cli and not has_token:
        print("⚠️  GitHub CLI (gh) not found and GITHUB_TOKEN not set.")
        print("   Will use public GitHub API (rate limited: 60 requests/hour)")
        print("\n💡 For better experience, install GitHub CLI OR set GITHUB_TOKEN:")
        print("   Option 1 - Install GitHub CLI (Recommended):")
        print("      Windows: winget install --id GitHub.cli")
        print("      Or visit: https://cli.github.com/")
        print("\n   Option 2 - Set GitHub API Token (Higher rate limit):")
        print("      Set environment variable: GITHUB_TOKEN=your_token_here")
        print("      Or create .env file with: GITHUB_TOKEN=your_token_here")
        print("\n   Proceeding with public API (may hit rate limits)...\n")
    elif has_cli:
        print("✅ Using GitHub CLI")
    elif has_token:
        print("✅ Using GitHub API (GITHUB_TOKEN)")
        print("⚠️  Note: Install GitHub CLI for better experience: https://cli.github.com/")
    
    # Check if user wants to wait or just show current status
    wait_mode = "--wait" in sys.argv or "-w" in sys.argv
    
    # Get PR number (filter out flags)
    pr_number = None
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--") and not arg.startswith("-")]
    
    if args:
        pr_number = args[0]
    else:
        # Try to auto-detect
        pr_number = get_pr_number()
        if not pr_number:
            pr_number = input("Enter PR number: ").strip()
    
    if not pr_number:
        print("❌ PR number required")
        print("   Usage: python scripts/wait_for_ai_analysis.py <PR_NUMBER> [--wait]")
        sys.exit(1)
    
    # Get current comments
    comments = get_pr_comments(pr_number)
    ai_comments = find_ai_analysis_comments(comments)
    
    if ai_comments:
        print(f"\n✅ Found {len(ai_comments)} AI Analysis comment(s) for PR #{pr_number}")
        display_ai_analysis(ai_comments)
        
        if wait_mode:
            print("\n🔄 Continuing to monitor for new analysis updates...")
            wait_for_ai_analysis(pr_number)
        else:
            print("\n💡 Use --wait flag to continue monitoring for updates")
    else:
        print(f"\n⏳ No AI Analysis comments found for PR #{pr_number}")
        
        if wait_mode:
            wait_for_ai_analysis(pr_number)
        else:
            print("\n💡 Use --wait flag to monitor for AI analysis:")
            print(f"   python scripts/wait_for_ai_analysis.py {pr_number} --wait")
            print("\n   Or check manually:")
            print(f"   python scripts/view_pr_comments.py {pr_number} --ai-only")


if __name__ == "__main__":
    main()

