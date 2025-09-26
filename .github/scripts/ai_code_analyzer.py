#!/usr/bin/env python3
"""
AI Code Analyzer Script
Performs intelligent code analysis using AI models
"""

import os
import json
import requests
from openai import OpenAI
from typing import Dict, List, Any, Optional
import subprocess
import difflib

class AICodeAnalyzer:
    def __init__(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.openrouter_key = os.environ.get('OPENROUTER_API_KEY')
        self.deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
        self.repo_name = os.environ.get('REPO_NAME')
        self.pr_number = os.environ.get('PR_NUMBER')
        self.commit_sha = os.environ.get('COMMIT_SHA')
        
        # Get changed files
        changed_files_str = os.environ.get('CHANGED_FILES', '')
        self.changed_files = changed_files_str.split() if changed_files_str else []
        
        # Initialize AI client
        self.ai_client = None
        if self.openrouter_key:
            self.ai_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_key,
            )
        elif self.deepseek_key:
            self.ai_client = OpenAI(
                base_url="https://api.deepseek.com/v1",
                api_key=self.deepseek_key,
            )
    
    def read_file_content(self, file_path: str) -> Optional[str]:
        """Read file content safely"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def get_file_diff(self, file_path: str) -> Optional[str]:
        """Get git diff for a specific file"""
        try:
            result = subprocess.run(
                ['git', 'diff', 'HEAD~1', 'HEAD', '--', file_path],
                capture_output=True,
                text=True
            )
            return result.stdout if result.returncode == 0 else None
        except Exception as e:
            print(f"Error getting diff for {file_path}: {e}")
            return None
    
    def analyze_code_with_ai(self, file_path: str, content: str, diff: str = None) -> Optional[Dict[str, Any]]:
        """Analyze code using AI models"""
        if not self.ai_client:
            return None
        
        file_extension = os.path.splitext(file_path)[1]
        
        # Create analysis prompt based on file type
        system_prompt = f"""
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
        
        try:
            # Use appropriate model based on availability
            model = "deepseek/deepseek-chat-v3.1:free" if self.openrouter_key else "deepseek-chat"
            
            extra_headers = {}
            if self.openrouter_key:
                extra_headers = {
                    "HTTP-Referer": f"https://github.com/{self.repo_name}",
                    "X-Title": "AMAS Code Analysis",
                }
            
            response = self.ai_client.chat.completions.create(
                extra_headers=extra_headers if self.openrouter_key else None,
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=1500
            )
            
            return {
                'file_path': file_path,
                'analysis': response.choices[0].message.content,
                'model_used': model
            }
            
        except Exception as e:
            print(f"Error analyzing {file_path} with AI: {e}")
            return None
    
    def analyze_security_issues(self, file_path: str, content: str) -> List[str]:
        """Basic security issue detection"""
        security_issues = []
        content_lower = content.lower()
        
        # Common security patterns to flag
        security_patterns = {
            'hardcoded_secrets': ['password =', 'api_key =', 'secret =', 'auth_token ='],
            'sql_injection': ['execute(', 'query(', 'raw sql'],
            'xss_vulnerabilities': ['innerHTML', 'dangerouslySetInnerHTML', 'eval('],
            'insecure_random': ['random.random()', 'math.random()'],
            'weak_crypto': ['md5', 'sha1', 'des'],
            'unsafe_deserialization': ['pickle.loads', 'yaml.load', 'eval(']
        }
        
        for issue_type, patterns in security_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    security_issues.append(f"Potential {issue_type.replace('_', ' ')}: Found '{pattern}'")
        
        return security_issues
    
    def post_pr_comment(self, comment: str) -> bool:
        """Post comment to pull request"""
        if not self.pr_number:
            print("No PR number available, skipping comment")
            return False
        
        url = f"https://api.github.com/repos/{self.repo_name}/issues/{self.pr_number}/comments"
        
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        # Add AI signature
        ai_comment = f"""{comment}

---
🤖 **AMAS AI Code Reviewer**
🔍 *Powered by your integrated AI models*
📊 *Automated analysis for better code quality*
"""
        
        data = {'body': ai_comment}
        
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
                security_summary.extend([
                    f"**{file_path}:**"
                ] + [f"  - {issue}" for issue in security_issues])
        
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
    
    def generate_analysis_report(self, analyses: List[Dict[str, Any]], security_issues: List[str]) -> str:
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
                report.append(analysis['analysis'])
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
