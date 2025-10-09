#!/usr/bin/env python3
"""
AI Code Analyzer Script
Performs intelligent code analysis using AI models
"""

import difflib
import json
import os
import subprocess
from typing import Any, Dict, List, Optional

import requests
from openai import OpenAI


class AICodeAnalyzer:
    def __init__(self):
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
        self.glm_key = os.environ.get("GLM_API_KEY")
        self.grok_key = os.environ.get("GROK_API_KEY")
        self.kimi_key = os.environ.get("KIMI_API_KEY")
        self.qwen_key = os.environ.get("QWEN_API_KEY")
        self.gptoss_key = os.environ.get("GPTOSS_API_KEY")
        self.claude_key = os.environ.get("CLAUDE_API_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.gpt4_key = os.environ.get("GPT4_API_KEY")
        self.repo_name = os.environ.get("REPO_NAME")
        self.pr_number = os.environ.get("PR_NUMBER")
        self.commit_sha = os.environ.get("COMMIT_SHA")

        # Get changed files
        changed_files_str = os.environ.get("CHANGED_FILES", "")
        self.changed_files = changed_files_str.split() if changed_files_str else []

        # Initialize AI clients with intelligent fallback priority
        self.ai_clients = []

        # Priority order: DeepSeek (most reliable), Claude, GPT-4, GLM, Grok, Kimi, Qwen, Gemini, GPTOSS
        if self.deepseek_key:
            try:
                self.ai_clients.append(
                    {
                        "name": "DeepSeek",
                        "client": OpenAI(
                            base_url="https://api.deepseek.com/v1",
                            api_key=self.deepseek_key,
                        ),
                        "model": "deepseek-chat",
                        "priority": 1,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize DeepSeek client: {e}")

        if self.claude_key:
            try:
                self.ai_clients.append(
                    {
                        "name": "Claude",
                        "client": OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=self.claude_key,
                        ),
                        "model": "anthropic/claude-3.5-sonnet",
                        "priority": 2,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize Claude client: {e}")

        if self.gpt4_key:
            try:
                self.ai_clients.append(
                    {
                        "name": "GPT-4",
                        "client": OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=self.gpt4_key,
                        ),
                        "model": "openai/gpt-4o",
                        "priority": 3,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize GPT-4 client: {e}")

        if self.glm_key:
            try:
                self.ai_clients.append(
                    {
                        "name": "GLM",
                        "client": OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=self.glm_key,
                        ),
                        "model": "z-ai/glm-4.5-air:free",
                        "priority": 4,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize GLM client: {e}")

        if self.grok_key:
            try:
                self.ai_clients.append(
                    {
                        "name": "Grok",
                        "client": OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=self.grok_key,
                        ),
                        "model": "x-ai/grok-4-fast:free",
                        "priority": 5,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize Grok client: {e}")

        if self.kimi_key:
            try:
                self.ai_clients.append(
                    {
                        "name": "Kimi",
                        "client": OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=self.kimi_key,
                        ),
                        "model": "moonshot/moonshot-v1-8k:free",
                        "priority": 6,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize Kimi client: {e}")

        if self.qwen_key:
            try:
                self.ai_clients.append(
                    {
                        "name": "Qwen",
                        "client": OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=self.qwen_key,
                        ),
                        "model": "qwen/qwen-2.5-7b-instruct:free",
                        "priority": 7,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize Qwen client: {e}")

        if self.gemini_key:
            try:
                self.ai_clients.append(
                    {
                        "name": "Gemini",
                        "client": OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=self.gemini_key,
                        ),
                        "model": "google/gemini-pro-1.5",
                        "priority": 8,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize Gemini client: {e}")

        if self.gptoss_key:
            try:
                self.ai_clients.append(
                    {
                        "name": "GPTOSS",
                        "client": OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=self.gptoss_key,
                        ),
                        "model": "openai/gpt-3.5-turbo:free",
                        "priority": 9,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize GPTOSS client: {e}")

        # Sort by priority
        self.ai_clients.sort(key=lambda x: x["priority"])

        if not self.ai_clients:
            print("⚠️ No AI clients available - analysis will be limited")
        else:
            print(
                f"🤖 Initialized {len(self.ai_clients)} AI clients with fallback support"
            )

    def read_file_content(self, file_path: str) -> Optional[str]:
        """Read file content safely"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None

    def get_file_diff(self, file_path: str) -> Optional[str]:
        """Get git diff for a specific file"""
        try:
            result = subprocess.run(
                ["git", "diff", "HEAD~1", "HEAD", "--", file_path],
                capture_output=True,
                text=True,
            )
            return result.stdout if result.returncode == 0 else None
        except Exception as e:
            print(f"Error getting diff for {file_path}: {e}")
            return None

    def analyze_code_with_ai(
        self, file_path: str, content: str, diff: str = None
    ) -> Optional[Dict[str, Any]]:
        """Analyze code using AI models with fallback"""
        if not self.ai_clients:
            return None

        file_extension = os.path.splitext(file_path)[1]

        # Create analysis prompt based on file type
        system_prompt = """
You are an expert code reviewer for the AMAS (Advanced Multi-Agent Intelligence System) project.
This is a multi-agent AI system focused on intelligence analysis, OSINT, and cybersecurity.

Analyze the code for:
1. Code quality and best practices
2. Security vulnerabilities
3. Performance optimization opportunities
4. Integration with AMAS architecture
5. Documentation and maintainability
6. Error handling and edge cases

Provide specific, actionable feedback. Focus on critical issues first.
"""

        analysis_prompt = f"""
File: {file_path}
File Type: {file_extension}

{'=== RECENT CHANGES ===' if diff else '=== FULL FILE ==='}
{diff if diff else content[:3000]}  # Limit content to avoid token limits
{'...[truncated]' if len(content) > 3000 else ''}

Please provide a structured code review with:
1. **Overall Assessment** (Good/Needs Improvement/Critical Issues)
2. **Security Analysis** (any vulnerabilities or concerns)
3. **Code Quality** (readability, maintainability, best practices)
4. **AMAS Integration** (how well it fits the project architecture)
5. **Specific Recommendations** (numbered list of actionable items)

Keep the analysis concise but thorough.
"""

        # Try each AI client in order of preference
        for client_info in self.ai_clients:
            try:
                print(f"🤖 Trying {client_info['name']} for analysis...")

                extra_headers = {}
                if "openrouter.ai" in str(client_info["client"].base_url):
                    extra_headers = {
                        "HTTP-Referer": f"https://github.com/{self.repo_name}",
                        "X-Title": "AMAS Code Analysis",
                    }

                response = client_info["client"].chat.completions.create(
                    extra_headers=extra_headers if extra_headers else None,
                    model=client_info["model"],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": analysis_prompt},
                    ],
                    temperature=0.3,  # Lower temperature for more consistent analysis
                    max_tokens=1500,
                )

                print(f"✅ Successfully analyzed with {client_info['name']}")
                return {
                    "file_path": file_path,
                    "analysis": response.choices[0].message.content,
                    "model_used": f"{client_info['name']} ({client_info['model']})",
                }

            except Exception as e:
                print(f"❌ {client_info['name']} failed: {e}")
                continue

        print("❌ All AI clients failed")
        return None

    def analyze_security_issues(self, file_path: str, content: str) -> List[str]:
        """Basic security issue detection with context awareness"""
        security_issues = []

        # Skip security scanner files to avoid false positives on pattern definitions
        if any(
            scanner_file in file_path.lower()
            for scanner_file in [
                "security_scanner",
                "security_false_positive",
                "ai_code_analyzer",
            ]
        ):
            return security_issues

        lines = content.split("\n")

        # Common security patterns to flag with regex for better accuracy
        import re

        security_patterns = {
            "hardcoded_secrets": [
                (r'password\s*=\s*["\'][^"\']+["\']', "hardcoded password"),
                (r'api_key\s*=\s*["\'][^"\']+["\']', "hardcoded API key"),
                (r'secret\s*=\s*["\'][^"\']+["\']', "hardcoded secret"),
                (r'(?<!github_)token\s*=\s*["\'][^"\']+["\']', "hardcoded token"),
            ],
            "sql_injection": [
                (r"execute\s*\([^)]*\+", "SQL injection via string concatenation"),
                (r"query\s*\([^)]*\+", "SQL injection via string concatenation"),
                (r"SELECT.*FROM.*\+", "SQL injection via string concatenation"),
            ],
            "xss_vulnerabilities": [
                (r"innerHTML\s*=", "XSS via innerHTML"),
                (r"dangerouslySetInnerHTML", "XSS via React dangerouslySetInnerHTML"),
                (r"eval\s*\(", "XSS/code injection via eval"),
            ],
            "insecure_random": [
                (r"random\.random\s*\(\)", "insecure random for cryptography"),
                (r"Math\.random\s*\(\)", "insecure random for cryptography"),
            ],
            "weak_crypto": [
                (r"\bmd5\s*\(", "weak MD5 hashing"),
                (r"\bsha1\s*\(", "weak SHA1 hashing"),
                (
                    r"\bDES\b",
                    "weak DES encryption",
                ),  # Only match DES as a standalone word
            ],
            "unsafe_deserialization": [
                (r"pickle\.loads", "unsafe pickle deserialization"),
                (
                    r"yaml\.load\s*\((?!.*Loader=)",
                    "unsafe yaml.load without safe loader",
                ),
            ],
        }

        for issue_type, patterns in security_patterns.items():
            for pattern, description in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1

                    # Skip if it's getting value from environment variable
                    line = lines[line_num - 1] if line_num <= len(lines) else ""
                    if (
                        "os.environ.get" in line
                        or "getenv" in line
                        or "= os.environ.get" in line
                    ):
                        continue

                    # Skip if it's in a comment
                    if line.strip().startswith("#") or line.strip().startswith("//"):
                        continue

                    # Skip if it's a pattern definition
                    if any(
                        pat in line
                        for pat in [
                            "'password =",
                            '"password =',
                            "'token =",
                            '"token =',
                            "'api_key =",
                            '"api_key =',
                            "'secret =",
                            '"secret =',
                        ]
                    ):
                        continue

                    # Skip obvious placeholders
                    matched_text = match.group(0).lower()
                    if any(
                        placeholder in matched_text
                        for placeholder in [
                            "example",
                            "placeholder",
                            "your_",
                            "xxx",
                            "dummy",
                            "test",
                            "sample",
                        ]
                    ):
                        continue

                    # Skip if in description or similar context
                    if "description" in line.lower():
                        continue

                    security_issues.append(
                        f"Potential {description}: Found '{pattern}'"
                    )

        return security_issues

    def post_pr_comment(self, comment: str) -> bool:
        """Post comment to pull request"""
        if not self.pr_number:
            print("No PR number available, skipping comment")
            return False

        url = f"https://api.github.com/repos/{self.repo_name}/issues/{self.pr_number}/comments"

        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }

        # Add AI signature
        ai_comment = f"""{comment}

---
🤖 **AMAS AI Code Reviewer**
🔍 *Powered by your integrated AI models*
📊 *Automated analysis for better code quality*
"""

        data = {"body": ai_comment}

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            print(f"✅ Posted AI code review to PR #{self.pr_number}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to post PR comment: {e}")
            return False

    def run(self):
        """Main execution function"""
        if not self.changed_files:
            print("No files to analyze")
            return

        print(f"🔍 Analyzing {len(self.changed_files)} changed files...")

        all_analyses = []
        security_summary = []

        for file_path in self.changed_files[:5]:  # Limit to 5 files to avoid API limits
            print(f"Analyzing: {file_path}")

            # Read file content
            content = self.read_file_content(file_path)
            if not content:
                continue

            # Get diff if this is a PR
            diff = self.get_file_diff(file_path) if self.pr_number else None

            # AI analysis
            ai_analysis = self.analyze_code_with_ai(file_path, content, diff)
            if ai_analysis:
                all_analyses.append(ai_analysis)

            # Security analysis
            security_issues = self.analyze_security_issues(file_path, content)
            if security_issues:
                security_summary.extend(
                    [f"**{file_path}:**"]
                    + [f"  - {issue}" for issue in security_issues]
                )

        # Generate comprehensive report
        if all_analyses or security_summary:
            report = self.generate_analysis_report(all_analyses, security_summary)

            if self.pr_number:
                self.post_pr_comment(report)
            else:
                print("📋 Analysis Report:")
                print(report)
        else:
            print("No significant issues found in the analyzed files.")

    def generate_analysis_report(
        self, analyses: List[Dict[str, Any]], security_issues: List[str]
    ) -> str:
        """Generate comprehensive analysis report"""
        report = ["# 🤖 AI Code Analysis Report\n"]

        if security_issues:
            report.append("## 🚨 Security Analysis")
            report.extend(security_issues)
            report.append("")

        if analyses:
            report.append("## 📊 Detailed Code Review")
            for i, analysis in enumerate(analyses, 1):
                report.append(f"### {i}. {analysis['file_path']}")
                report.append(analysis["analysis"])
                report.append("")

        # Add summary recommendations
        report.append("## 💡 Next Steps")
        if security_issues:
            report.append("- ⚠️ **Priority**: Address security issues immediately")
        report.append("- 📝 Review and implement the specific recommendations above")
        report.append("- 🧪 Add unit tests for any new functionality")
        report.append("- 📚 Update documentation if needed")

        return "\n".join(report)


if __name__ == "__main__":
    analyzer = AICodeAnalyzer()
    analyzer.run()
