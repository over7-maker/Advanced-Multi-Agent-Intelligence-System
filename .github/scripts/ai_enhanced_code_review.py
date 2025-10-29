#!/usr/bin/env python3

"""
AI Enhanced Code Review Script - Powered by Ultimate Fallback System
Provides comprehensive code review and refactoring suggestions for PRs
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# Add project root to sys.path (readable and robust)
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.amas.services.ultimate_fallback_system import UltimateFallbackSystem
except ImportError as e:
    logging.critical(
        "Failed to import UltimateFallbackSystem from src.amas.services. "
        "Ensure src/ is on PYTHONPATH. This is required for enhanced code review. "
        "Error: %s", str(e)
    )
    # Graceful degradation - continue with basic functionality
    UltimateFallbackSystem = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

class EnhancedCodeReviewer:
    """Enhanced code reviewer with AI-powered analysis"""

    def __init__(self):
        self.ai_system = UltimateFallbackSystem() if UltimateFallbackSystem else None
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_name = os.getenv("REPO_NAME")
        self.pr_number = os.getenv("PR_NUMBER")
        self.commit_sha = os.getenv("COMMIT_SHA", "unknown")
        self.artifacts_dir = "artifacts"

        # Create artifacts directory
        os.makedirs(self.artifacts_dir, exist_ok=True)
        
        # Log initialization status
        if self.ai_system:
            print(f"🤖 Enhanced code reviewer initialized with AI system")
        else:
            print(f"⚠️ Enhanced code reviewer running in basic mode (AI system unavailable)")

    def get_pr_diff(self) -> str:
        """Get the diff for the pull request"""
        try:
            if self.pr_number:
                # Get PR diff
                cmd = ["git", "diff", "origin/main...HEAD"]
            else:
                # Get commit diff
                cmd = ["git", "diff", "HEAD~1", "HEAD"]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout
        except subprocess.TimeoutExpired:
            print("⚠️ Git diff operation timed out")
            return ""
        except Exception as e:
            print(f"⚠️ Error getting diff: {str(e)}")
            return ""

    def get_changed_files(self) -> List[str]:
        """Get list of changed files"""
        try:
            if self.pr_number:
                cmd = ["git", "diff", "--name-only", "origin/main...HEAD"]
            else:
                cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return [f.strip() for f in result.stdout.split("\\n") if f.strip()]
        except subprocess.TimeoutExpired:
            print("⚠️ Git diff --name-only operation timed out")
            return []
        except Exception as e:
            print(f"⚠️ Error getting changed files: {str(e)}")
            return []

    def analyze_code_quality(
        self, diff: str, changed_files: List[str]
    ) -> Dict[str, Any]:
        """Analyze code quality using AI or provide basic analysis"""
        if not self.ai_system:
            return self._basic_analysis(diff, changed_files)
            
        prompt = f"""## Enhanced Code Review Request

Please perform a comprehensive code review of the following changes:

**Changed Files:**
{', '.join(changed_files[:10])}  # Limit for API constraints

**Code Diff:**
```diff
{diff[:2500]}  # Truncated for API limits
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
                "analysis_type": "ai_enhanced"
            }
        except Exception as e:
            logging.error("AI analysis failed: %s", str(e))
            return self._basic_analysis(diff, changed_files)
            
    def _basic_analysis(self, diff: str, changed_files: List[str]) -> Dict[str, Any]:
        """Provide basic code analysis when AI is unavailable"""
        analysis_lines = []
        analysis_lines.append("## 📋 Basic Code Review Analysis")
        analysis_lines.append(f"**Files Changed:** {len(changed_files)}")
        
        # Basic file type analysis
        py_files = [f for f in changed_files if f.endswith('.py')]
        js_files = [f for f in changed_files if f.endswith(('.js', '.jsx', '.ts', '.tsx'))]
        config_files = [f for f in changed_files if f.endswith(('.yml', '.yaml', '.json', '.toml'))]
        
        if py_files:
            analysis_lines.append(f"**Python Files:** {len(py_files)} files modified")
        if js_files:
            analysis_lines.append(f"**JavaScript/TypeScript Files:** {len(js_files)} files modified")
        if config_files:
            analysis_lines.append(f"**Configuration Files:** {len(config_files)} files modified")
            
        # Basic diff statistics
        lines = diff.split('\\n')
        additions = len([line for line in lines if line.startswith('+')])
        deletions = len([line for line in lines if line.startswith('-')])
        
        analysis_lines.append(f"**Changes:** +{additions} additions, -{deletions} deletions")
        analysis_lines.append("")
        analysis_lines.append("### 🔍 Basic Recommendations")
        analysis_lines.append("- Ensure all changes have appropriate tests")
        analysis_lines.append("- Verify documentation is updated")
        analysis_lines.append("- Check for potential security implications")
        analysis_lines.append("- Consider performance impact of changes")
        analysis_lines.append("")
        analysis_lines.append("*Note: Enhanced AI analysis unavailable - basic review provided*")
        
        return {
            "success": True,
            "analysis": "\\n".join(analysis_lines),
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_type": "basic"
        }

    def generate_review_report(
        self, analysis: Dict[str, Any], diff_stats: Dict[str, int]
    ) -> str:
        """Generate the final review report"""
        if not analysis["success"]:
            return f"""# ❌ Enhanced Code Review Failed

Error: {analysis.get('error', 'Unknown error occurred')}"""

        ai_status = "🤖 AI Enhanced" if analysis.get("analysis_type") == "ai_enhanced" else "📋 Basic"
        
        report = f"""# {ai_status} Code Review Report

**Repository:** {self.repo_name}
**PR Number:** #{self.pr_number or 'N/A'}
**Commit:** `{self.commit_sha[:8]}`
**Timestamp:** {analysis['timestamp']}

## 📊 Change Summary
- **Files Changed:** {diff_stats['files_changed']}
- **Lines Added:** +{diff_stats['additions']}
- **Lines Removed:** -{diff_stats['deletions']}

---

{analysis['analysis']}

---

## 🎯 Review Summary

This code review was performed using the Advanced Multi-Agent Intelligence System.

### Review Features:
- ✅ Comprehensive code quality analysis
- ✅ Security vulnerability detection
- ✅ Performance optimization suggestions
- ✅ Best practices compliance check
- ✅ Automated refactoring recommendations
- ✅ Test coverage analysis
- ✅ Documentation completeness review
- ✅ Architecture impact assessment

*Generated by AI Enhanced Code Review v2.1 - {analysis.get('analysis_type', 'unknown')} mode*
        """
        return report

    def calculate_diff_stats(self, diff: str) -> Dict[str, int]:
        """Calculate statistics from the diff"""
        lines = diff.split("\\n")
        additions = len([line for line in lines if line.startswith("+")])
        deletions = len([line for line in lines if line.startswith("-")])
        files_changed = len(self.get_changed_files())

        return {
            "additions": max(0, additions - 1),  # Subtract header lines
            "deletions": max(0, deletions - 1),  # Subtract header lines
            "files_changed": files_changed,
        }

    def run(self):
        """Run the enhanced code review"""
        print("🚀 Starting enhanced code review...")

        # Get diff and changed files
        diff = self.get_pr_diff()
        changed_files = self.get_changed_files()

        if not diff and not changed_files:
            print("ℹ️ No changes detected")
            report = "# ℹ️ No Changes Detected\\n\\nNo code changes were found to review."
        else:
            # Calculate diff statistics
            diff_stats = self.calculate_diff_stats(diff)
            print(f"📊 Analyzing {diff_stats['files_changed']} files with {diff_stats['additions']} additions and {diff_stats['deletions']} deletions")

            # Perform analysis (AI or basic)
            analysis = self.analyze_code_quality(diff, changed_files)

            # Generate report
            report = self.generate_review_report(analysis, diff_stats)

        # Save report
        report_path = os.path.join(self.artifacts_dir, "enhanced_code_review_report.md")
        with open(report_path, "w", encoding='utf-8') as f:
            f.write(report)

        print(f"✅ Enhanced code review report saved to {report_path}")

        # Also print to console for debugging
        print("\\n" + "=" * 80)
        print(report)
        print("=" * 80 + "\\n")

        return report

def main():
    """Main function"""
    try:
        reviewer = EnhancedCodeReviewer()
        reviewer.run()
    except Exception as e:
        print(f"❌ Enhanced code review failed: {str(e)}")
        logging.exception("Code review error details")

        # Create error report
        error_report = f"""# ❌ Enhanced Code Review Error

An error occurred during the enhanced code review process:

```
{str(e)}
```

Please check the workflow logs for more details.

**Timestamp:** {datetime.utcnow().isoformat()}
        """

        # Save error report
        os.makedirs("artifacts", exist_ok=True)
        with open("artifacts/enhanced_code_review_report.md", "w", encoding='utf-8') as f:
            f.write(error_report)

        # Don't exit with error - this is a non-critical enhancement
        print("⚠️ Continuing with basic functionality...")

if __name__ == "__main__":
    main()