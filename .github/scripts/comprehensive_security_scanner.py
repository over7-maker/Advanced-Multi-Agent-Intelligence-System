#!/usr/bin/env python3
"""
Comprehensive Security Scanner Script
Performs advanced security analysis using multiple techniques
"""

import os
import json
import re
import requests
import subprocess
from openai import OpenAI
from typing import Dict, List, Any, Optional
from pathlib import Path

class ComprehensiveSecurityScanner:
    def __init__(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.openrouter_key = os.environ.get('OPENROUTER_API_KEY')
        self.deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
        self.repo_name = os.environ.get('REPO_NAME')
        
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
    
    def scan_for_secrets_advanced(self, content: str, file_path: str) -> List[Dict[str, str]]:
        """Advanced secret scanning with more patterns"""
        secrets_found = []
        
        # Enhanced secret patterns
        secret_patterns = {
            'api_key': r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
            'secret_key': r'(?i)(secret[_-]?key|secretkey)\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
            'password': r'(?i)(password|pwd|pass)\s*[=:]\s*["\']?([^\s"\'>]{8,})["\']?',
            'token': r'(?i)(token|auth[_-]?token)\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
            'aws_access_key': r'AKIA[0-9A-Z]{16}',
            'aws_secret_key': r'[A-Za-z0-9/+=]{40}',
            'github_token': r'ghp_[a-zA-Z0-9]{36}',
            'github_app_token': r'ghs_[a-zA-Z0-9]{36}',
            'openrouter_key': r'sk-or-v1-[a-zA-Z0-9]{64}',
            'openai_key': r'sk-[a-zA-Z0-9]{48}',
            'private_key': r'-----BEGIN (RSA |EC |DSA |)?PRIVATE KEY-----',
            'jwt_secret': r'(?i)(jwt[_-]?secret|jwt[_-]?key)\s*[=:]\s*["\']?([a-zA-Z0-9_-]{32,})["\']?',
            'database_url': r'(?i)(database[_-]?url|db[_-]?url)\s*[=:]\s*["\']?([^\s"\'>]{20,})["\']?',
            'redis_url': r'(?i)(redis[_-]?url)\s*[=:]\s*["\']?([^\s"\'>]{20,})["\']?',
            'mongodb_url': r'(?i)(mongodb[_-]?url)\s*[=:]\s*["\']?([^\s"\'>]{20,})["\']?'
        }
        
        for secret_type, pattern in secret_patterns.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                # Skip obvious examples or placeholders
                matched_text = match.group(0).lower()
                if any(placeholder in matched_text for placeholder in 
                       ['example', 'placeholder', 'your_', 'xxx', 'dummy', 'test', 'sample', '<', '>', 'TODO']):
                    continue
                
                secrets_found.append({
                    'type': secret_type,
                    'file': file_path,
                    'line': content[:match.start()].count('\n') + 1,
                    'match': match.group(0)[:50] + '...' if len(match.group(0)) > 50 else match.group(0),
                    'severity': 'high' if secret_type in ['private_key', 'aws_secret_key'] else 'medium'
                })
        
        return secrets_found
    
    def scan_for_vulnerabilities_advanced(self, content: str, file_path: str) -> List[Dict[str, str]]:
        """Advanced vulnerability scanning"""
        vulnerabilities = []
        
        # Enhanced vulnerability patterns
        vuln_patterns = {
            'sql_injection': {
                'patterns': [
                    r'execute\s*\([^)]*\+', 
                    r'query\s*\([^)]*\+', 
                    r'SELECT.*\+.*FROM',
                    r'INSERT.*\+.*INTO',
                    r'UPDATE.*\+.*SET',
                    r'DELETE.*\+.*FROM'
                ],
                'description': 'Potential SQL injection vulnerability',
                'severity': 'high'
            },
            'xss': {
                'patterns': [
                    r'innerHTML\s*=', 
                    r'dangerouslySetInnerHTML', 
                    r'eval\s*\(',
                    r'document\.write\s*\(',
                    r'\.html\s*\('
                ],
                'description': 'Potential XSS vulnerability',
                'severity': 'high'
            },
            'path_traversal': {
                'patterns': [
                    r'\.\./', 
                    r'os\.path\.join\([^)]*input', 
                    r'open\([^)]*input',
                    r'file\s*\([^)]*input'
                ],
                'description': 'Potential path traversal vulnerability',
                'severity': 'medium'
            },
            'weak_crypto': {
                'patterns': [
                    r'\bmd5\b', 
                    r'\bsha1\b', 
                    r'\bdes\b', 
                    r'random\.random\(',
                    r'Math\.random\('
                ],
                'description': 'Usage of weak cryptographic functions',
                'severity': 'medium'
            },
            'command_injection': {
                'patterns': [
                    r'os\.system\s*\([^)]*input', 
                    r'subprocess\.[^\s]*\([^)]*shell\s*=\s*True',
                    r'exec\s*\([^)]*input',
                    r'eval\s*\([^)]*input'
                ],
                'description': 'Potential command injection vulnerability',
                'severity': 'high'
            },
            'insecure_deserialization': {
                'patterns': [
                    r'pickle\.loads\s*\(',
                    r'yaml\.load\s*\(',
                    r'json\.loads\s*\([^)]*input',
                    r'marshal\.loads\s*\('
                ],
                'description': 'Potential insecure deserialization',
                'severity': 'high'
            },
            'ssrf': {
                'patterns': [
                    r'requests\.get\s*\([^)]*input',
                    r'urllib\.request\.urlopen\s*\([^)]*input',
                    r'fetch\s*\([^)]*input'
                ],
                'description': 'Potential Server-Side Request Forgery (SSRF)',
                'severity': 'high'
            }
        }
        
        for vuln_type, vuln_info in vuln_patterns.items():
            for pattern in vuln_info['patterns']:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    vulnerabilities.append({
                        'type': vuln_type,
                        'file': file_path,
                        'line': line_num,
                        'description': vuln_info['description'],
                        'severity': vuln_info['severity'],
                        'code_snippet': self.get_code_snippet(content, line_num)
                    })
        
        return vulnerabilities
    
    def get_code_snippet(self, content: str, line_num: int, context: int = 3) -> str:
        """Get code snippet around a specific line"""
        lines = content.split('\n')
        start = max(0, line_num - context - 1)
        end = min(len(lines), line_num + context)
        
        snippet_lines = []
        for i in range(start, end):
            marker = '>>> ' if i == line_num - 1 else '    '
            snippet_lines.append(f"{marker}{i+1}: {lines[i]}")
        
        return '\n'.join(snippet_lines)
    
    def run_bandit_scan(self) -> Dict[str, Any]:
        """Run Bandit security scanner"""
        try:
            result = subprocess.run([
                'bandit', '-r', '.', '-f', 'json', '-o', 'bandit-report.json'
            ], capture_output=True, text=True, timeout=300)
            
            if os.path.exists('bandit-report.json'):
                with open('bandit-report.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Bandit scan failed: {e}")
        
        return {'results': []}
    
    def run_safety_scan(self) -> Dict[str, Any]:
        """Run Safety dependency scanner"""
        try:
            result = subprocess.run([
                'safety', 'check', '--json', '--output', 'safety-report.json'
            ], capture_output=True, text=True, timeout=300)
            
            if os.path.exists('safety-report.json'):
                with open('safety-report.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Safety scan failed: {e}")
        
        return {'vulnerabilities': []}
    
    def analyze_with_ai(self, security_issues: List[Dict[str, Any]]) -> Optional[str]:
        """Get AI analysis of security issues"""
        if not self.ai_client or not security_issues:
            return None
        
        system_prompt = """
You are a cybersecurity expert analyzing code for the AMAS Intelligence System.
Focus on critical security vulnerabilities that could compromise the system.

Provide:
1. Risk assessment (Critical/High/Medium/Low)
2. Exploitation scenarios
3. Specific remediation steps
4. Best practices for secure coding
5. Priority order for fixing issues

Be concise but thorough. Focus on actionable recommendations.
"""
        
        security_prompt = f"""
Security Issues Found:
"""
        
        for issue in security_issues[:10]:  # Limit to first 10 issues
            security_prompt += f"\n**{issue.get('type', 'Unknown')}** in {issue.get('file', 'Unknown')}"
            security_prompt += f"\n- Severity: {issue.get('severity', 'Unknown')}"
            security_prompt += f"\n- Description: {issue.get('description', 'No description')}"
            if 'code_snippet' in issue:
                security_prompt += f"\n- Code: {issue['code_snippet'][:200]}..."
        
        security_prompt += "\n\nPlease analyze these security issues and provide specific remediation guidance."
        
        try:
            model = "deepseek/deepseek-chat-v3.1:free" if self.openrouter_key else "deepseek-chat"
            
            extra_headers = {}
            if self.openrouter_key:
                extra_headers = {
                    "HTTP-Referer": f"https://github.com/{self.repo_name}",
                    "X-Title": "AMAS Security Analysis",
                }
            
            response = self.ai_client.chat.completions.create(
                extra_headers=extra_headers if self.openrouter_key else None,
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": security_prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error getting AI security analysis: {e}")
            return None
    
    def generate_comprehensive_report(self, scan_results: Dict[str, Any]) -> str:
        """Generate comprehensive security report"""
        report = ["# 🔒 Comprehensive Security Analysis Report\n"]
        
        # Summary
        total_secrets = len(scan_results.get('secrets', []))
        total_vulns = len(scan_results.get('vulnerabilities', []))
        bandit_issues = len(scan_results.get('bandit_results', []))
        safety_issues = len(scan_results.get('safety_vulnerabilities', []))
        
        report.append(f"**Analysis Date**: {scan_results.get('timestamp', 'Unknown')}")
        report.append(f"**Repository**: {self.repo_name}")
        report.append("")
        
        if total_secrets > 0 or total_vulns > 0 or bandit_issues > 0 or safety_issues > 0:
            report.append("🚨 **SECURITY ISSUES DETECTED**\n")
            report.append(f"- **{total_secrets}** potential secrets/API keys")
            report.append(f"- **{total_vulns}** code vulnerabilities")
            report.append(f"- **{bandit_issues}** Bandit security issues")
            report.append(f"- **{safety_issues}** dependency vulnerabilities\n")
        else:
            report.append("✅ **No critical security issues detected**\n")
        
        # Secrets section
        if scan_results.get('secrets'):
            report.append("## 🔑 Potential Secrets")
            for secret in scan_results['secrets']:
                report.append(f"- **{secret['type']}** in {secret['file']} (Line {secret['line']})")
                report.append(f"  - Severity: {secret['severity']}")
                report.append(f"  - Match: `{secret['match']}`")
            report.append("")
        
        # Vulnerabilities section
        if scan_results.get('vulnerabilities'):
            report.append("## ⚠️ Code Vulnerabilities")
            for vuln in scan_results['vulnerabilities']:
                report.append(f"- **{vuln['description']}** in {vuln['file']} (Line {vuln['line']})")
                report.append(f"  - Severity: {vuln['severity']}")
                report.append(f"  - Type: {vuln['type']}")
            report.append("")
        
        # Bandit results
        if scan_results.get('bandit_results'):
            report.append("## 🔍 Bandit Security Analysis")
            for result in scan_results['bandit_results'][:5]:  # Show first 5
                report.append(f"- **{result.get('issue_severity', 'Unknown')}**: {result.get('issue_text', 'No description')}")
                report.append(f"  - File: {result.get('filename', 'Unknown')}")
                report.append(f"  - Line: {result.get('line_number', 'Unknown')}")
            report.append("")
        
        # Safety results
        if scan_results.get('safety_vulnerabilities'):
            report.append("## 📦 Dependency Vulnerabilities")
            for vuln in scan_results['safety_vulnerabilities'][:5]:  # Show first 5
                report.append(f"- **{vuln.get('package', 'Unknown')}**: {vuln.get('vulnerability', 'Unknown')}")
                report.append(f"  - Severity: {vuln.get('severity', 'Unknown')}")
            report.append("")
        
        # AI Analysis
        if scan_results.get('ai_analysis'):
            report.append("## 🤖 AI Security Analysis")
            report.append(scan_results['ai_analysis'])
            report.append("")
        
        # Remediation guidelines
        if total_secrets > 0 or total_vulns > 0 or bandit_issues > 0 or safety_issues > 0:
            report.append("## 🛠️ Immediate Actions Required")
            if total_secrets > 0:
                report.append("- ⚠️ **Remove all hardcoded secrets immediately**")
                report.append("- 🔄 **Rotate any exposed API keys**")
                report.append("- 📝 **Use environment variables or secret management**")
            if total_vulns > 0:
                report.append("- 🔍 **Review and fix security vulnerabilities**")
                report.append("- 🧪 **Add input validation and sanitization**")
                report.append("- 📊 **Run additional security testing**")
            if bandit_issues > 0:
                report.append("- 🐍 **Address Python security issues found by Bandit**")
            if safety_issues > 0:
                report.append("- 📦 **Update vulnerable dependencies**")
                report.append("- 🔄 **Run `pip install --upgrade` for affected packages**")
        
        return "\n".join(report)
    
    def run(self):
        """Main execution function"""
        print("🔒 Starting comprehensive security scan...")
        
        scan_results = {
            'timestamp': str(subprocess.run(['date'], capture_output=True, text=True).stdout.strip()),
            'secrets': [],
            'vulnerabilities': [],
            'bandit_results': [],
            'safety_vulnerabilities': [],
            'ai_analysis': None
        }
        
        # Scan all Python files
        python_files = list(Path('.').rglob('*.py'))
        print(f"Scanning {len(python_files)} Python files...")
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Scan for secrets
                secrets = self.scan_for_secrets_advanced(content, str(file_path))
                scan_results['secrets'].extend(secrets)
                
                # Scan for vulnerabilities
                vulns = self.scan_for_vulnerabilities_advanced(content, str(file_path))
                scan_results['vulnerabilities'].extend(vulns)
                
            except Exception as e:
                print(f"Error scanning {file_path}: {e}")
        
        # Run Bandit scan
        print("Running Bandit security scanner...")
        bandit_results = self.run_bandit_scan()
        scan_results['bandit_results'] = bandit_results.get('results', [])
        
        # Run Safety scan
        print("Running Safety dependency scanner...")
        safety_results = self.run_safety_scan()
        scan_results['safety_vulnerabilities'] = safety_results.get('vulnerabilities', [])
        
        # Get AI analysis
        all_issues = scan_results['secrets'] + scan_results['vulnerabilities']
        if all_issues and self.ai_client:
            print("Getting AI security analysis...")
            scan_results['ai_analysis'] = self.analyze_with_ai(all_issues)
        
        # Generate report
        report = self.generate_comprehensive_report(scan_results)
        
        # Save report
        with open('security-analysis-report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("📋 Security Analysis Report:")
        print(report)
        
        return scan_results

if __name__ == "__main__":
    scanner = ComprehensiveSecurityScanner()
    scanner.run()