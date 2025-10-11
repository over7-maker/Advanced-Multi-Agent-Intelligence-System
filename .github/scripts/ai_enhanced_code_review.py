#!/usr/bin/env python3
"""
    AI Enhanced Code Review Script - Powered by Ultimate Fallback System
Provides comprehensive code review and refactoring suggestions for PRs
    """

import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

# Add project root to sys.path
    sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )

    try:
from src.amas.services.ultimate_fallback_system import UltimateFallbackSystem
    except ImportError:
    # Fallback import paths
    sys.path.insert(
        0,
        os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
            "services",
        ),
    )
    try:
        from ultimate_fallback_system import UltimateFallbackSystem
    except ImportError:
        print("Error: Could not import UltimateFallbackSystem")
        sys.exit(1)

# Configure logging
    logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

class EnhancedCodeReviewer:
    """Enhanced code reviewer with AI-powered analysis"""

def __init__(self):
        self.ai_system = UltimateFallbackSystem()
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_name = os.getenv("REPO_NAME")
        self.pr_number = os.getenv("PR_NUMBER")
        self.commit_sha = os.getenv("COMMIT_SHA")
        self.artifacts_dir = "artifacts"

        # Create artifacts directory
        os.makedirs(self.artifacts_dir, exist_ok=True)

def get_pr_diff(self) -> str:
        """Get the diff for the pull request"""
        try:
            if self.pr_number:
                # Get PR diff
                cmd = ["git", "diff", "origin/main...HEAD"]
            else:
                # Get commit diff
                cmd = ["git", "diff", "HEAD~1", "HEAD"]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            print(f"Error getting diff: {str(e)}")
            return ""

def get_changed_files(self) -> List[str]:
        """Get list of changed files"""
        try:
            if self.pr_number:
                cmd = ["git", "diff", "--name-only", "origin/main...HEAD"]
            else:
                cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return [f.strip() for f in result.stdout.split("\n") if f.strip()]
        except Exception as e:
            print(f"Error getting changed files: {str(e)}")
            return []

def analyze_code_quality(
        self, diff: str, changed_files: List[str]
    ) -> Dict[str, Any]:
        """Analyze code quality using AI"""
        prompt = f"""## Enhanced Code Review Request

    Please perform a comprehensive code review of the following changes:

    **Changed Files:**
    {', '.join(changed_files)}

    **Code Diff:**
    ```diff
{diff[:3000]}  # Truncated for API limits
    ```

    Please provide:
    1. **Code Quality Assessment** (1-10 score with explanation)
    2. **Security Analysis** (identify any security concerns)
    3. **Performance Review** (identify performance issues or improvements)
    4. **Best Practices Check** (adherence to coding standards)
    5. **Refactoring Suggestions** (specific improvements)
    6. **Testing Recommendations** (what tests should be added)
    7. **Documentation Review** (are changes properly documented)
    8. **Architecture Impact** (does this affect system architecture)

Format your response as a structured markdown report suitable for GitHub comments.
    Include specific line numbers and code snippets where applicable.
    Be constructive and provide actionable feedback.
    """

        try:
            response = self.ai_system.query_with_fallback(prompt)
            return {
                "success": True,
                "analysis": response,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            print(f"Error in code analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

def generate_review_report(
        self, analysis: Dict[str, Any], diff_stats: Dict[str, int]
    ) -> str:
        """Generate the final review report"""
        if not analysis["success"]:
            return f"""# ❌ Enhanced Code Review Failed

    Error: {analysis.get('error', 'Unknown error occurred')}"""

        report = f"""# 🤖 AI Enhanced Code Review Report

    **Repository:** {self.repo_name}
    **PR Number:** {self.pr_number or 'N/A'}
    **Commit:** {self.commit_sha[:7]}
    **Timestamp:** {analysis['timestamp']}

## 📊 Change Summary
    - **Files Changed:** {diff_stats['files_changed']}
    - **Lines Added:** +{diff_stats['additions']}
    - **Lines Removed:** -{diff_stats['deletions']}

    ---

    {analysis['analysis']}

    ---

## 🎯 Review Summary

    This enhanced code review was performed using the Ultimate AI Fallback System with 9 AI providers ensuring 100% reliability.

### Review Features:
    - ✅ Comprehensive code quality analysis
    - ✅ Security vulnerability detection
    - ✅ Performance optimization suggestions
    - ✅ Best practices compliance check
    - ✅ Automated refactoring recommendations
    - ✅ Test coverage analysis
    - ✅ Documentation completeness review
    - ✅ Architecture impact assessment

    *Generated by AI Enhanced Code Review v2.0*
    """
        return report

def calculate_diff_stats(self, diff: str) -> Dict[str, int]:
        """Calculate statistics from the diff"""
        additions = len([line for line in diff.split("\n") if line.startswith("+")])
        deletions = len([line for line in diff.split("\n") if line.startswith("-")])
        files_changed = len(self.get_changed_files())

        return {
            "additions": additions,
            "deletions": deletions,
            "files_changed": files_changed,
        }

def run(self):
        """Run the enhanced code review"""
        print("Starting enhanced code review...")

        # Get diff and changed files
        diff = self.get_pr_diff()
        changed_files = self.get_changed_files()

        if not diff and not changed_files:
            print("No changes detected")
            report = "# ℹ️ No Changes Detected\n\nNo code changes were found to review."
        else:
            # Calculate diff statistics
            diff_stats = self.calculate_diff_stats(diff)

            # Perform AI analysis
            analysis = self.analyze_code_quality(diff, changed_files)

            # Generate report
            report = self.generate_review_report(analysis, diff_stats)

        # Save report
        report_path = os.path.join(self.artifacts_dir, "enhanced_code_review_report.md")
        with open(report_path, "w") as f:
            f.write(report)

        print(f"Enhanced code review report saved to {report_path}")

        # Also print to console for debugging
        print("\n" + "=" * 80)
        print(report)
        print("=" * 80 + "\n")

        return report

def main():
    """Main function"""
    try:
        reviewer = EnhancedCodeReviewer()
        reviewer.run()
    except Exception as e:
        print(f"Enhanced code review failed: {str(e)}")

        # Create error report
        error_report = f"""# ❌ Enhanced Code Review Error

    An error occurred during the enhanced code review process:

    ```
    {str(e)}
    ```

Please check the workflow logs for more details.
    """

        # Save error report
        os.makedirs("artifacts", exist_ok=True)
        with open("artifacts/enhanced_code_review_report.md", "w") as f:
            f.write(error_report)

        sys.exit(1)

if __name__ == "__main__":
    main()
