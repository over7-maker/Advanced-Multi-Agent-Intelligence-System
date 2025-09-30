#!/usr/bin/env python3
"""
AI Security Scanner Script
Performs intelligent security analysis using AI models
"""

import os
import json
import re
import requests
from openai import OpenAI
from typing import Dict, List, Any, Optional

class AISecurityScanner:
    def __init__(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
        self.glm_key = os.environ.get('GLM_API_KEY')
        self.grok_key = os.environ.get('GROK_API_KEY')
        self.kimi_key = os.environ.get('KIMI_API_KEY')
        self.qwen_key = os.environ.get('QWEN_API_KEY')
        self.gptoss_key = os.environ.get('GPTOSS_API_KEY')
        self.claude_key = os.environ.get('CLAUDE_API_KEY')
        self.gemini_key = os.environ.get('GEMINI_API_KEY')
        self.gpt4_key = os.environ.get('GPT4_API_KEY')
        self.repo_name = os.environ.get('REPO_NAME')
        self.pr_number = os.environ.get('PR_NUMBER')
        
        # Get changed files
        changed_files_str = os.environ.get('CHANGED_FILES', '')
        self.changed_files = changed_files_str.split() if changed_files_str else []
        
        # Initialize AI clients with intelligent fallback priority
        self.ai_clients = []
        
        # Priority order: DeepSeek (most reliable), Claude, GPT-4, GLM, Grok, Kimi, Qwen, Gemini, GPTOSS
        if self.deepseek_key:
            try:
                self.ai_clients.append({
                    'name': 'DeepSeek',
                    'client': OpenAI(
                        base_url="https://api.deepseek.com/v1",
                        api_key=self.deepseek_key,
                    ),
                    'model': 'deepseek-chat',
                    'priority': 1
                })
            except Exception as e:
                print(f"Failed to initialize DeepSeek client: {e}")
        
        if self.claude_key:
            try:
                self.ai_clients.append({
                    'name': 'Claude',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.claude_key,
                    ),
                    'model': 'anthropic/claude-3.5-sonnet',
                    'priority': 2
                })
            except Exception as e:
                print(f"Failed to initialize Claude client: {e}")
        
        if self.gpt4_key:
            try:
                self.ai_clients.append({
                    'name': 'GPT-4',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.gpt4_key,
                    ),
                    'model': 'openai/gpt-4o',
                    'priority': 3
                })
            except Exception as e:
                print(f"Failed to initialize GPT-4 client: {e}")
        
        if self.glm_key:
            try:
                self.ai_clients.append({
                    'name': 'GLM',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.glm_key,
                    ),
                    'model': 'z-ai/glm-4.5-air:free',
                    'priority': 4
                })
            except Exception as e:
                print(f"Failed to initialize GLM client: {e}")
        
        if self.grok_key:
            try:
                self.ai_clients.append({
                    'name': 'Grok',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.grok_key,
                    ),
                    'model': 'x-ai/grok-4-fast:free',
                    'priority': 5
                })
            except Exception as e:
                print(f"Failed to initialize Grok client: {e}")
        
        if self.kimi_key:
            try:
                self.ai_clients.append({
                    'name': 'Kimi',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.kimi_key,
                    ),
                    'model': 'moonshot/moonshot-v1-8k:free',
                    'priority': 6
                })
            except Exception as e:
                print(f"Failed to initialize Kimi client: {e}")
        
        if self.qwen_key:
            try:
                self.ai_clients.append({
                    'name': 'Qwen',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.qwen_key,
                    ),
                    'model': 'qwen/qwen-2.5-7b-instruct:free',
                    'priority': 7
                })
            except Exception as e:
                print(f"Failed to initialize Qwen client: {e}")
        
        if self.gemini_key:
            try:
                self.ai_clients.append({
                    'name': 'Gemini',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.gemini_key,
                    ),
                    'model': 'google/gemini-pro-1.5',
                    'priority': 8
                })
            except Exception as e:
                print(f"Failed to initialize Gemini client: {e}")
        
        if self.gptoss_key:
            try:
                self.ai_clients.append({
                    'name': 'GPTOSS',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.gptoss_key,
                    ),
                    'model': 'openai/gpt-3.5-turbo:free',
                    'priority': 9
                })
            except Exception as e:
                print(f"Failed to initialize GPTOSS client: {e}")
        
        # Sort by priority
        self.ai_clients.sort(key=lambda x: x['priority'])
        
        if not self.ai_clients:
            print("⚠️ No AI clients available - security analysis will be limited")
        else:
            print(f"🤖 Initialized {len(self.ai_clients)} AI clients for security analysis")
    
    def scan_for_secrets(self, content: str, file_path: str) -> List[Dict[str, str]]:
        """Scan for potential secrets and API keys"""
        secrets_found = []
        
        # Patterns for different types of secrets
        secret_patterns = {
            'api_key': r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
            'secret_key': r'(?i)(secret[_-]?key|secretkey)\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
            'password': r'(?i)(password|pwd)\s*[=:]\s*["\']?([^\s"\'>]{8,})["\']?',
            'token': r'(?i)(token|auth)\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
            'aws_key': r'AKIA[0-9A-Z]{16}',
            'github_token': r'ghp_[a-zA-Z0-9]{36}',
            'openrouter_key': r'sk-or-v1-[a-zA-Z0-9]{64}',
            'private_key': r'-----BEGIN (RSA |EC |DSA |)?PRIVATE KEY-----'
        }
        
        for secret_type, pattern in secret_patterns.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                # Don't flag obvious examples or placeholders
                matched_text = match.group(0).lower()
                if any(placeholder in matched_text for placeholder in 
                       ['example', 'placeholder', 'your_', 'xxx', 'dummy', 'test', 'sample', '<', '>']):
                    continue
                
                secrets_found.append({
                    'type': secret_type,
                    'file': file_path,
                    'line': content[:match.start()].count('\n') + 1,
                    'match': match.group(0)[:50] + '...' if len(match.group(0)) > 50 else match.group(0)
                })
        
        return secrets_found
    
    def _is_pattern_definition_file(self, content: str, file_path: str) -> bool:
        """Check if file contains only pattern definitions (not actual vulnerabilities)"""
        # Check if file is a security scanner or pattern definition file
        if any(keyword in file_path.lower() for keyword in ['security_scanner', 'ai_code_analyzer', 'ai_security']):
            # Look for pattern definition indicators
            pattern_indicators = [
                'vuln_patterns', 'security_patterns', 'detection_patterns',
                'hardcoded_secrets', 'sql_injection', 'xss_vulnerabilities',
                'weak_crypto', 'insecure_random', 'unsafe_deserialization',
                'patterns =', 'description =', 'vulnerability patterns',
                'path_traversal', 'command_injection'
            ]
            
            # Count pattern definition indicators vs actual code
            pattern_count = sum(1 for indicator in pattern_indicators if indicator in content)
            total_lines = len(content.split('\n'))
            
            # If more than 15% of content contains pattern indicators, likely a pattern file
            return pattern_count > (total_lines * 0.15)
        
        return False
    
    def _is_pattern_definition_line(self, line: str, context_lines: list) -> bool:
        """Check if a specific line is a pattern definition rather than actual vulnerable code"""
        import re
        line_lower = line.lower().strip()
        
        # Check for pattern definition indicators
        pattern_indicators = [
            'patterns =', 'description =', 'vuln_patterns', 'security_patterns',
            'hardcoded_secrets', 'sql_injection', 'xss_vulnerabilities',
            'weak_crypto', 'insecure_random', 'unsafe_deserialization',
            'path_traversal', 'command_injection', 'insecure_random'
        ]
        
        # If line contains pattern indicators, it's likely a pattern definition
        if any(indicator in line_lower for indicator in pattern_indicators):
            return True
        
        # Check for regex pattern definitions (lines with r'...' or r"...")
        if ("r'" in line and "'" in line) or ('r"' in line and '"' in line):
            # Check if this is within a patterns definition context
            for context_line in context_lines:
                if 'patterns' in context_line.lower() and '=' in context_line:
                    return True
        
        # Check if line is part of a dictionary definition for patterns
        if any('{' in context_line and '}' in context_line for context_line in context_lines):
            if ':' in line and ('[' in line or ']' in line):
                return True
        
        # Check for specific pattern definition patterns
        # Look for patterns that are being defined as strings (within quotes)
        if re.search(r'''['"]\s*r?['"]\s*[a-zA-Z_\\.*+()]+\s*['"]\s*['"]\s*,?''', line):
            # This looks like a pattern string definition
            if any(keyword in line.lower() for keyword in ['sql', 'xss', 'injection', 'patterns', 'vulnerabil']):
                return True
        
        # Check if line contains regex pattern definitions
        pattern_definitions = [
            'execute\\\\s*\\\\(',  # SQL injection patterns
            'innerHTML\\\\s*=',  # XSS patterns
            'dangerouslySetInnerHTML',  # XSS patterns
            'eval\\\\s*\\\\(',  # XSS patterns
            'SELECT.*\\\\+.*FROM',  # SQL patterns
            'query\\\\s*\\\\([^)]*\\\\+',  # SQL patterns
        ]
        
        for pattern in pattern_definitions:
            if pattern in line:
                return True
        
        return False
    
    def scan_for_vulnerabilities(self, content: str, file_path: str) -> List[Dict[str, str]]:
        """Scan for common security vulnerabilities with context awareness"""
        vulnerabilities = []
        
        # Skip if this is a pattern definition file
        if self._is_pattern_definition_file(content, file_path):
            print(f"🔍 Skipping pattern definition file: {file_path}")
            return vulnerabilities
        
        # Vulnerability patterns
        vuln_patterns = {
            'sql_injection': {
                'patterns': [r'execute\s*\([^)]*\+', r'query\s*\([^)]*\+', r'SELECT.*\+.*FROM'],
                'description': 'Potential SQL injection vulnerability'
            },
            'xss': {
                'patterns': [r'innerHTML\s*=', r'dangerouslySetInnerHTML', r'eval\s*\('],
                'description': 'Potential XSS vulnerability'
            },
            'path_traversal': {
                'patterns': [r'\.\./', r'os\.path\.join\([^)]*input', r'open\([^)]*input'],
                'description': 'Potential path traversal vulnerability'
            },
            'weak_crypto': {
                'patterns': [r'\bmd5\b', r'\bsha1\b', r'\bdes\b', r'random\.random\('],
                'description': 'Usage of weak cryptographic functions'
            },
            'command_injection': {
                'patterns': [r'os\.system\s*\([^)]*input', r'subprocess\.[^\s]*\([^)]*shell\s*=\s*True'],
                'description': 'Potential command injection vulnerability'
            }
        }
        
        for vuln_type, vuln_info in vuln_patterns.items():
            for pattern in vuln_info['patterns']:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    
                    # Get context lines around the match
                    lines = content.split('\n')
                    start_line = max(0, line_num - 3)
                    end_line = min(len(lines), line_num + 3)
                    context_lines = lines[start_line:end_line]
                    
                    # Check if this is a pattern definition line
                    if self._is_pattern_definition_line(lines[line_num - 1], context_lines):
                        print(f"🔍 Skipping pattern definition line {line_num} in {file_path}")
                        continue
                    
                    vulnerabilities.append({
                        'type': vuln_type,
                        'file': file_path,
                        'line': line_num,
                        'description': vuln_info['description'],
                        'code_snippet': self.get_code_snippet(content, line_num)
                    })
        
        return vulnerabilities
    
    def get_code_snippet(self, content: str, line_num: int, context: int = 2) -> str:
        """Get code snippet around a specific line"""
        lines = content.split('\n')
        start = max(0, line_num - context - 1)
        end = min(len(lines), line_num + context)
        
        snippet_lines = []
        for i in range(start, end):
            marker = '>>> ' if i == line_num - 1 else '    '
            snippet_lines.append(f"{marker}{i+1}: {lines[i]}")
        
        return '\n'.join(snippet_lines)
    
    def analyze_security_with_ai(self, file_path: str, content: str, 
                                 secrets: List[Dict], vulns: List[Dict]) -> Optional[str]:
        """Get AI analysis of security issues with fallback"""
        if not self.ai_clients or (not secrets and not vulns):
            return None
        
        system_prompt = """
You are a cybersecurity expert analyzing code for the AMAS Intelligence System.
Focus on critical security vulnerabilities that could compromise the system.

Provide:
1. Risk assessment (Critical/High/Medium/Low)
2. Exploitation scenarios
3. Specific remediation steps
4. Best practices for secure coding

Be concise but thorough.
"""
        
        security_prompt = f"""
File: {file_path}

Detected Issues:
"""
        
        if secrets:
            security_prompt += "\n**Potential Secrets:**\n"
            for secret in secrets:
                security_prompt += f"- {secret['type']} at line {secret['line']}\n"
        
        if vulns:
            security_prompt += "\n**Vulnerabilities:**\n"
            for vuln in vulns:
                security_prompt += f"- {vuln['description']} at line {vuln['line']}\n"
                security_prompt += f"  Code: {vuln['code_snippet'].split('>>>', 1)[-1] if '>>>' in vuln['code_snippet'] else vuln['code_snippet']}\n"
        
        security_prompt += "\nPlease analyze these security issues and provide specific remediation guidance."
        
        # Try each AI client in order of preference
        for client_info in self.ai_clients:
            try:
                print(f"🤖 Trying {client_info['name']} for security analysis...")
                
                extra_headers = {}
                if 'openrouter.ai' in str(client_info['client'].base_url):
                    extra_headers = {
                        "HTTP-Referer": f"https://github.com/{self.repo_name}",
                        "X-Title": "AMAS Security Analysis",
                    }
                
                response = client_info['client'].chat.completions.create(
                    extra_headers=extra_headers if extra_headers else None,
                    model=client_info['model'],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": security_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=1000
                )
                
                print(f"✅ Successfully analyzed security with {client_info['name']}")
                return response.choices[0].message.content
                
            except Exception as e:
                print(f"❌ {client_info['name']} failed: {e}")
                continue
        
        print("❌ All AI clients failed for security analysis")
        return None
    
    def post_pr_comment(self, comment: str) -> bool:
        """Post security report to pull request"""
        if not self.pr_number or not self.github_token:
            print("No PR number or GitHub token available, skipping comment")
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
🔒 **AMAS AI Security Scanner**
🛡️ *Powered by your integrated AI models*
⚠️ *Please review and address security findings*
"""
        
        data = {'body': ai_comment}
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            print(f"✅ Posted security report to PR #{self.pr_number}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to post PR comment: {e}")
            return False
    
    def generate_security_report(self, scan_results: List[Dict[str, Any]]) -> str:
        """Generate comprehensive security report"""
        report = ["# 🔒 AI Security Scan Report\n"]
        
        total_secrets = sum(len(result['secrets']) for result in scan_results)
        total_vulns = sum(len(result['vulnerabilities']) for result in scan_results)
        
        # Summary
        if total_secrets > 0 or total_vulns > 0:
            report.append("🚨 **SECURITY ISSUES DETECTED**\n")
            report.append(f"- **{total_secrets}** potential secrets/API keys")
            report.append(f"- **{total_vulns}** potential vulnerabilities\n")
        else:
            report.append("✅ **No critical security issues detected**\n")
        
        # Detailed findings
        for result in scan_results:
            if result['secrets'] or result['vulnerabilities']:
                report.append(f"## {result['file']}")
                
                # Secrets section
                if result['secrets']:
                    report.append("### 🔑 Potential Secrets")
                    for secret in result['secrets']:
                        report.append(f"- **{secret['type']}** (Line {secret['line']}): `{secret['match']}`")
                    report.append("")
                
                # Vulnerabilities section
                if result['vulnerabilities']:
                    report.append("### ⚠️ Security Vulnerabilities")
                    for vuln in result['vulnerabilities']:
                        report.append(f"- **{vuln['description']}** (Line {vuln['line']})")
                        report.append(f"  ```\n{vuln['code_snippet']}\n  ```")
                    report.append("")
                
                # AI analysis
                if result['ai_analysis']:
                    report.append("### 🤖 AI Security Analysis")
                    report.append(result['ai_analysis'])
                    report.append("")
        
        # Remediation guidelines
        if total_secrets > 0 or total_vulns > 0:
            report.append("## 🛠️ Immediate Actions Required")
            if total_secrets > 0:
                report.append("- ⚠️ **Remove all hardcoded secrets immediately**")
                report.append("- 🔄 **Rotate any exposed API keys**")
                report.append("- 📝 **Use environment variables or secret management**")
            if total_vulns > 0:
                report.append("- 🔍 **Review and fix security vulnerabilities**")
                report.append("- 🧪 **Add input validation and sanitization**")
                report.append("- 📊 **Run additional security testing**")
        
        return "\n".join(report)
    
    def run(self):
        """Main execution function"""
        if not self.changed_files:
            print("No files to scan")
            return
        
        print(f"🔒 Security scanning {len(self.changed_files)} files...")
        
        scan_results = []
        
        for file_path in self.changed_files:
            # Only scan code files
            if not any(file_path.endswith(ext) for ext in ['.py', '.js', '.ts', '.java', '.php', '.rb', '.go', '.yml', '.yaml', '.json']):
                continue
            
            print(f"Scanning: {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
            
            # Perform scans
            secrets = self.scan_for_secrets(content, file_path)
            vulnerabilities = self.scan_for_vulnerabilities(content, file_path)
            
            # Get AI analysis if issues found
            ai_analysis = None
            if (secrets or vulnerabilities) and self.ai_clients:
                ai_analysis = self.analyze_security_with_ai(file_path, content, secrets, vulnerabilities)
            
            if secrets or vulnerabilities or ai_analysis:
                scan_results.append({
                    'file': file_path,
                    'secrets': secrets,
                    'vulnerabilities': vulnerabilities,
                    'ai_analysis': ai_analysis
                })
        
        # Generate and output report
        if scan_results:
            report = self.generate_security_report(scan_results)
            print("📋 Security Report:")
            print(report)
            
            # Post to PR if this is a pull request
            if self.pr_number:
                self.post_pr_comment(report)
        else:
            print("✅ No security issues detected in scanned files.")

if __name__ == "__main__":
    scanner = AISecurityScanner()
    scanner.run()
