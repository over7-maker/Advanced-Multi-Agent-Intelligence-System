#!/usr/bin/env python3
"""
View PR Comments and AI Analysis in Terminal
Fetch and display PR comments, especially AI analysis results from GitHub Actions
"""

import os
import sys
import json
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


def get_pr_info_gh_cli(pr_number: str) -> Optional[Dict]:
    """Get PR info using GitHub CLI"""
    try:
        # Use environment variable to force UTF-8 encoding
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            ["gh", "pr", "view", pr_number, "--json", "number,title,state,author,comments"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env,
            check=True
        )
        if result.stdout is None or not result.stdout.strip():
            return None
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError, TypeError) as e:
        print(f"⚠️  Error fetching PR info: {e}")
        return None
    except Exception as e:
        print(f"⚠️  Unexpected error: {e}")
        return None


def get_pr_comments_gh_cli(pr_number: str) -> str:
    """Get PR comments using GitHub CLI"""
    try:
        # Use environment variable to force UTF-8 encoding
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            ["gh", "pr", "view", pr_number, "--comments"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env,
            check=True
        )
        return result.stdout if result.stdout else ""
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error fetching PR comments: {e}")
        return ""
    except Exception as e:
        print(f"⚠️  Unexpected error: {e}")
        return ""


def get_pr_comments_api(pr_number: str, repo: str = "over7-maker/Advanced-Multi-Agent-Intelligence-System") -> List[Dict]:
    """Get PR comments using GitHub API"""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("⚠️  GITHUB_TOKEN not set. Using GitHub CLI or public API (rate limited)...")
        token = None
    
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    headers["Accept"] = "application/vnd.github.v3+json"
    
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Error fetching PR comments: {e}")
        return []


def get_issue_comments_api(pr_number: str, repo: str = "over7-maker/Advanced-Multi-Agent-Intelligence-System") -> List[Dict]:
    """Get issue comments (PR comments are also issue comments)"""
    token = os.environ.get("GITHUB_TOKEN")
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    headers["Accept"] = "application/vnd.github.v3+json"
    
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Error fetching issue comments: {e}")
        return []


def format_comment(comment: Dict) -> str:
    """Format a comment for display"""
    author = comment.get("user", {}).get("login", "Unknown")
    body = comment.get("body", "")
    created_at = comment.get("created_at", "")
    
    # Parse date
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except:
        time_str = created_at
    
    # Check if it's an AI analysis comment
    is_ai_analysis = "BULLETPROOF REAL AI Analysis" in body or "Bulletproof AI Analysis" in body
    is_github_actions = author == "github-actions[bot]"
    
    header = "🤖 AI ANALYSIS" if is_ai_analysis else "💬 COMMENT"
    if is_github_actions:
        header = "🤖 GITHUB ACTIONS"
    
    output = []
    output.append(f"\n{'='*80}")
    output.append(f"{header} - {author} ({time_str})")
    output.append(f"{'='*80}")
    output.append(body)
    output.append(f"{'='*80}\n")
    
    return "\n".join(output)


def filter_ai_comments(comments: List[Dict]) -> List[Dict]:
    """Filter comments to show only AI analysis"""
    ai_comments = []
    for comment in comments:
        body = comment.get("body", "")
        if "BULLETPROOF" in body or "Bulletproof AI" in body or "AI Analysis" in body:
            ai_comments.append(comment)
    return ai_comments


def display_pr_summary(pr_number: str, repo: str):
    """Display PR summary and all comments"""
    print(f"\n{'='*80}")
    print(f"📋 PR #{pr_number} - {repo}")
    print(f"{'='*80}\n")
    
    # Try GitHub CLI first
    if check_gh_cli():
        print("✅ Using GitHub CLI...\n")
        
        # Get PR info
        try:
            pr_info = get_pr_info_gh_cli(pr_number)
            if pr_info:
                print(f"📌 Title: {pr_info.get('title', 'N/A')}")
                print(f"📊 State: {pr_info.get('state', 'N/A')}")
                print(f"👤 Author: {pr_info.get('author', {}).get('login', 'N/A')}")
                print(f"💬 Comments: {len(pr_info.get('comments', []))}")
                print()
        except Exception as e:
            print(f"⚠️  Could not fetch PR info: {e}")
        
        # Get comments
        print("📝 Fetching comments...")
        try:
            comments_text = get_pr_comments_gh_cli(pr_number)
            if comments_text and comments_text.strip():
                print(comments_text)
            else:
                print("⚠️  No comments found or error fetching comments")
        except Exception as e:
            print(f"⚠️  Error fetching comments: {e}")
            print("\n💡 Trying alternative method...")
            # Fallback to API
            try:
                comments = get_issue_comments_api(pr_number, repo)
                if comments:
                    print(f"✅ Found {len(comments)} comments via API\n")
                    for comment in comments:
                        print(format_comment(comment))
            except Exception as e2:
                print(f"⚠️  API method also failed: {e2}")
        
        # Optionally open in browser
        print("\n💡 Tip: Use '--web' flag to open PR in browser")
    
    else:
        print("⚠️  GitHub CLI not found. Using GitHub API...\n")
        print("💡 Install GitHub CLI for better experience: https://cli.github.com/\n")
        
        # Get comments via API
        print("📝 Fetching PR comments...")
        comments = get_issue_comments_api(pr_number, repo)
        
        if comments:
            print(f"✅ Found {len(comments)} comments\n")
            
            # Show all comments
            for comment in comments:
                print(format_comment(comment))
            
            # Show AI-only summary
            ai_comments = filter_ai_comments(comments)
            if ai_comments:
                print(f"\n{'='*80}")
                print(f"🤖 AI ANALYSIS SUMMARY ({len(ai_comments)} comments)")
                print(f"{'='*80}\n")
                for comment in ai_comments:
                    print(format_comment(comment))
        else:
            print("⚠️  No comments found")


def main():
    """Main function"""
    if len(sys.argv) < 2 or sys.argv[1] in ["--help", "-h", "help"]:
        print("Usage: python scripts/view_pr_comments.py <PR_NUMBER> [OPTIONS]")
        print("\nExample:")
        print("  python scripts/view_pr_comments.py 3542")
        print("  python scripts/view_pr_comments.py 3542 --ai-only")
        print("  python scripts/view_pr_comments.py 3542 --web")
        print("\nOptions:")
        print("  --ai-only    Show only AI analysis comments")
        print("  --web        Open PR in browser")
        print("\nRequirements:")
        print("  - GitHub CLI (gh) OR GitHub API token in GITHUB_TOKEN env var")
        print("  - Install GitHub CLI: https://cli.github.com/")
        sys.exit(0 if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "help"] else 1)
    
    pr_number = sys.argv[1]
    
    # Check for flags
    ai_only = "--ai-only" in sys.argv
    open_web = "--web" in sys.argv
    
    repo = "over7-maker/Advanced-Multi-Agent-Intelligence-System"
    
    if open_web:
        if check_gh_cli():
            try:
                subprocess.run(
                    ["gh", "pr", "view", pr_number, "--web"],
                    encoding='utf-8',
                    errors='replace',
                    check=False
                )
            except Exception:
                pass
        else:
            url = f"https://github.com/{repo}/pull/{pr_number}"
            print(f"🌐 Opening: {url}")
            try:
                if sys.platform == "win32":
                    os.startfile(url)
                elif sys.platform == "darwin":
                    subprocess.run(["open", url])
                else:
                    subprocess.run(["xdg-open", url])
            except Exception as e:
                print(f"⚠️  Could not open browser: {e}")
                print(f"Please open manually: {url}")
        return
    
    display_pr_summary(pr_number, repo)
    
    # Show instructions
    print("\n" + "="*80)
    print("💡 TIPS:")
    print("  - Use 'gh pr view <PR_NUMBER> --web' to open in browser")
    print("  - Use 'gh pr view <PR_NUMBER> --comments' for plain text")
    print("  - Install GitLens extension in Cursor for PR integration")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

