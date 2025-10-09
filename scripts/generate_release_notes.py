#!/usr/bin/env python3
"""
Generate Release Notes for AMAS Releases
Enhanced with AI integration for intelligent release note generation
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, List

import requests


class AIReleaseNotesGenerator:
    """AI-powered release notes generator"""

    def __init__(self, github_token: str, repo_name: str):
        self.github_token = github_token
        self.repo_name = repo_name
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json",
            }
        )

    def get_commits_since_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get commits since the last tag"""
        try:
            # Get the tag's commit SHA
            tag_url = (
                f"https://api.github.com/repos/{self.repo_name}/git/refs/tags/{tag}"
            )
            tag_response = self.session.get(tag_url)

            if tag_response.status_code == 404:
                # If tag doesn't exist, get all commits
                commits_url = f"https://api.github.com/repos/{self.repo_name}/commits"
            else:
                tag_sha = tag_response.json()["object"]["sha"]
                commits_url = f"https://api.github.com/repos/{self.repo_name}/commits?since={tag_sha}"

            response = self.session.get(commits_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Warning: Could not fetch commits: {e}")
            return []

    def get_pull_requests_since_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get merged pull requests since the last tag"""
        try:
            # Get commits first
            commits = self.get_commits_since_tag(tag)
            pr_numbers = set()

            # Extract PR numbers from commit messages
            for commit in commits:
                message = commit.get("commit", {}).get("message", "")
                pr_match = re.search(r"#(\d+)", message)
                if pr_match:
                    pr_numbers.add(pr_match.group(1))

            # Get PR details
            prs = []
            for pr_num in pr_numbers:
                pr_url = f"https://api.github.com/repos/{self.repo_name}/pulls/{pr_num}"
                response = self.session.get(pr_url)
                if response.status_code == 200:
                    pr_data = response.json()
                    if pr_data.get("state") == "closed" and pr_data.get("merged_at"):
                        prs.append(pr_data)

            return prs
        except Exception as e:
            print(f"Warning: Could not fetch pull requests: {e}")
            return []

    def categorize_changes(
        self, commits: List[Dict], prs: List[Dict]
    ) -> Dict[str, List[str]]:
        """Categorize changes using AI-like pattern matching"""
        categories = {
            "features": [],
            "fixes": [],
            "improvements": [],
            "breaking": [],
            "docs": [],
            "security": [],
            "performance": [],
        }

        # Keywords for categorization
        feature_keywords = ["feat", "feature", "add", "new", "implement"]
        fix_keywords = ["fix", "bug", "issue", "resolve", "correct"]
        improvement_keywords = ["improve", "enhance", "optimize", "refactor", "update"]
        breaking_keywords = ["break", "remove", "deprecate", "change"]
        doc_keywords = ["doc", "readme", "comment", "documentation"]
        security_keywords = [
            "security",
            "vulnerability",
            "auth",
            "permission",
            "access",
        ]
        performance_keywords = ["perf", "performance", "speed", "memory", "optimize"]

        # Process commits
        for commit in commits:
            message = commit.get("commit", {}).get("message", "").lower()
            author = commit.get("commit", {}).get("author", {}).get("name", "")

            # Skip merge commits and automated commits
            if any(
                skip in message
                for skip in ["merge", "revert", "chore", "ci:", "build:"]
            ):
                continue

            # Categorize based on keywords
            if any(keyword in message for keyword in feature_keywords):
                categories["features"].append(f"- {message.split('\\n')[0]} ({author})")
            elif any(keyword in message for keyword in fix_keywords):
                categories["fixes"].append(f"- {message.split('\\n')[0]} ({author})")
            elif any(keyword in message for keyword in improvement_keywords):
                categories["improvements"].append(
                    f"- {message.split('\\n')[0]} ({author})"
                )
            elif any(keyword in message for keyword in breaking_keywords):
                categories["breaking"].append(f"- {message.split('\\n')[0]} ({author})")
            elif any(keyword in message for keyword in doc_keywords):
                categories["docs"].append(f"- {message.split('\\n')[0]} ({author})")
            elif any(keyword in message for keyword in security_keywords):
                categories["security"].append(f"- {message.split('\\n')[0]} ({author})")
            elif any(keyword in message for keyword in performance_keywords):
                categories["performance"].append(
                    f"- {message.split('\\n')[0]} ({author})"
                )
            else:
                categories["improvements"].append(
                    f"- {message.split('\\n')[0]} ({author})"
                )

        # Process pull requests
        for pr in prs:
            title = pr.get("title", "").lower()
            body = pr.get("body", "").lower()
            author = pr.get("user", {}).get("login", "")
            pr_number = pr.get("number", "")

            pr_text = f"- {pr.get('title', '')} (#{pr_number}) by @{author}"

            if any(keyword in title or keyword in body for keyword in feature_keywords):
                categories["features"].append(pr_text)
            elif any(keyword in title or keyword in body for keyword in fix_keywords):
                categories["fixes"].append(pr_text)
            elif any(
                keyword in title or keyword in body for keyword in improvement_keywords
            ):
                categories["improvements"].append(pr_text)
            elif any(
                keyword in title or keyword in body for keyword in breaking_keywords
            ):
                categories["breaking"].append(pr_text)
            elif any(keyword in title or keyword in body for keyword in doc_keywords):
                categories["docs"].append(pr_text)
            elif any(
                keyword in title or keyword in body for keyword in security_keywords
            ):
                categories["security"].append(pr_text)
            elif any(
                keyword in title or keyword in body for keyword in performance_keywords
            ):
                categories["performance"].append(pr_text)
            else:
                categories["improvements"].append(pr_text)

        return categories

    def generate_ai_insights(
        self, categories: Dict[str, List[str]], version: str
    ) -> str:
        """Generate AI-powered insights about the release"""
        insights = []

        total_changes = sum(len(changes) for changes in categories.values())

        if total_changes == 0:
            insights.append(
                "🤖 **AI Analysis**: This appears to be a maintenance or configuration release with minimal code changes."
            )
        else:
            insights.append(
                f"🤖 **AI Analysis**: This release contains {total_changes} significant changes across multiple categories."
            )

            if categories["breaking"]:
                insights.append(
                    "⚠️ **Breaking Changes Detected**: This release includes breaking changes that may require user action."
                )

            if categories["security"]:
                insights.append(
                    "🔒 **Security Updates**: This release includes important security improvements."
                )

            if categories["performance"]:
                insights.append(
                    "⚡ **Performance Improvements**: This release includes performance optimizations."
                )

            if len(categories["features"]) > 5:
                insights.append(
                    "🚀 **Feature-Rich Release**: This is a major feature release with significant new functionality."
                )
            elif len(categories["fixes"]) > 5:
                insights.append(
                    "🐛 **Bug Fix Release**: This release focuses primarily on bug fixes and stability improvements."
                )

        return "\\n\\n".join(insights)


def generate_release_notes(
    version: str, github_token: str, repo_name: str, output_file: str
) -> str:
    """Generate comprehensive release notes"""

    generator = AIReleaseNotesGenerator(github_token, repo_name)

    # Get previous tag (assuming semantic versioning)
    try:
        # Try to get the previous version
        version_parts = version.lstrip("v").split(".")
        if len(version_parts) >= 3:
            major, minor, patch = version_parts[:3]
            if patch != "0":
                prev_patch = str(int(patch) - 1)
                prev_tag = f"v{major}.{minor}.{prev_patch}"
            elif minor != "0":
                prev_minor = str(int(minor) - 1)
                prev_tag = f"v{major}.{prev_minor}.0"
            else:
                prev_major = str(int(major) - 1)
                prev_tag = f"v{prev_major}.0.0"
        else:
            prev_tag = "v0.0.0"
    except:
        prev_tag = "v0.0.0"

    print(f"📋 Generating release notes for {version} (since {prev_tag})")

    # Get changes
    commits = generator.get_commits_since_tag(prev_tag)
    prs = generator.get_pull_requests_since_tag(prev_tag)

    print(f"📊 Found {len(commits)} commits and {len(prs)} pull requests")

    # Categorize changes
    categories = generator.categorize_changes(commits, prs)

    # Generate AI insights
    ai_insights = generator.generate_ai_insights(categories, version)

    # Build release notes
    timestamp = datetime.now().strftime("%Y-%m-%d")

    release_notes = f"""# 🚀 AMAS {version} Release Notes

**Release Date**: {timestamp}  
**Generated by**: AI-Enhanced Release System

{ai_insights}

## 📋 What's New

"""

    # Add categorized changes
    if categories["features"]:
        release_notes += "### ✨ New Features\\n\\n"
        for feature in categories["features"][:10]:  # Limit to 10 items
            release_notes += f"{feature}\\n"
        if len(categories["features"]) > 10:
            release_notes += (
                f"- ... and {len(categories['features']) - 10} more features\\n"
            )
        release_notes += "\\n"

    if categories["improvements"]:
        release_notes += "### 🔧 Improvements\\n\\n"
        for improvement in categories["improvements"][:10]:
            release_notes += f"{improvement}\\n"
        if len(categories["improvements"]) > 10:
            release_notes += (
                f"- ... and {len(categories['improvements']) - 10} more improvements\\n"
            )
        release_notes += "\\n"

    if categories["fixes"]:
        release_notes += "### 🐛 Bug Fixes\\n\\n"
        for fix in categories["fixes"][:10]:
            release_notes += f"{fix}\\n"
        if len(categories["fixes"]) > 10:
            release_notes += f"- ... and {len(categories['fixes']) - 10} more fixes\\n"
        release_notes += "\\n"

    if categories["security"]:
        release_notes += "### 🔒 Security Updates\\n\\n"
        for security in categories["security"]:
            release_notes += f"{security}\\n"
        release_notes += "\\n"

    if categories["performance"]:
        release_notes += "### ⚡ Performance Improvements\\n\\n"
        for perf in categories["performance"]:
            release_notes += f"{perf}\\n"
        release_notes += "\\n"

    if categories["breaking"]:
        release_notes += "### ⚠️ Breaking Changes\\n\\n"
        for breaking in categories["breaking"]:
            release_notes += f"{breaking}\\n"
        release_notes += "\\n"

    if categories["docs"]:
        release_notes += "### 📚 Documentation Updates\\n\\n"
        for doc in categories["docs"][:5]:
            release_notes += f"{doc}\\n"
        if len(categories["docs"]) > 5:
            release_notes += (
                f"- ... and {len(categories['docs']) - 5} more documentation updates\\n"
            )
        release_notes += "\\n"

    # Add statistics
    release_notes += f"""## 📊 Release Statistics

- **Total Commits**: {len(commits)}
- **Pull Requests**: {len(prs)}
- **Contributors**: {len(set(commit.get('commit', {}).get('author', {}).get('name', '') for commit in commits))}
- **Files Changed**: {sum(commit.get('stats', {}).get('total', 0) for commit in commits)}

## 🔗 Links

- [Full Changelog](https://github.com/{repo_name}/compare/{prev_tag}...{version})
- [Documentation](https://github.com/{repo_name}/docs)
- [Issues](https://github.com/{repo_name}/issues)

---

*This release was automatically generated using AI-enhanced tools.*
"""

    return release_notes


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Generate AI-enhanced release notes")
    parser.add_argument(
        "--version", required=True, help="Release version (e.g., v1.0.0)"
    )
    parser.add_argument("--output", default="RELEASE_NOTES.md", help="Output file path")
    parser.add_argument(
        "--github-token", help="GitHub token (or use GITHUB_TOKEN env var)"
    )
    parser.add_argument("--repo", help="Repository name (or use REPO_NAME env var)")

    args = parser.parse_args()

    # Get GitHub token and repo name
    github_token = args.github_token or os.environ.get("GITHUB_TOKEN")
    repo_name = args.repo or os.environ.get("REPO_NAME")

    if not github_token:
        print("❌ Error: GitHub token is required")
        print("Set GITHUB_TOKEN environment variable or use --github-token")
        sys.exit(1)

    if not repo_name:
        print("❌ Error: Repository name is required")
        print("Set REPO_NAME environment variable or use --repo")
        sys.exit(1)

    try:
        print(f"🤖 AI-Enhanced Release Notes Generator")
        print(f"📦 Repository: {repo_name}")
        print(f"🏷️ Version: {args.version}")
        print(f"📄 Output: {args.output}")
        print("=" * 50)

        # Generate release notes
        release_notes = generate_release_notes(
            args.version, github_token, repo_name, args.output
        )

        # Write to file
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(release_notes)

        print(f"✅ Release notes generated successfully: {args.output}")
        print(f"📊 File size: {len(release_notes)} characters")

        return True

    except Exception as e:
        print(f"❌ Error generating release notes: {e}")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error generating release notes: {e}")
        sys.exit(1)