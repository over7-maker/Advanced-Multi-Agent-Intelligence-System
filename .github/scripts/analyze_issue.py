#!/usr/bin/env python3
"""
Practical Issue Analyzer - Provides actionable feedback for GitHub issues and PRs
"""
import os
import sys
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import traceback

class PracticalAnalyzer:
    def __init__(self):
        self.results = {
            'code_analysis': [],
            'security_issues': [],
            'performance_tips': [],
            'actionable_fixes': [],
            'quick_wins': []
        }
        
    def analyze_code_quality(self, file_path: str) -> List[Dict]:
        """Analyze code quality and provide specific fixes"""
        issues = []
        
        try:
            # Run pylint with specific checks
            cmd = ['pylint', file_path, '--output-format=json', '--disable=all', 
                   '--enable=C0103,C0111,C0112,C0301,C0302,C0303,C0304,C0305,'
                   'W0611,W0612,W0613,W0614,E0401,E0601,E0602,E1101']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                try:
                    pylint_issues = json.loads(result.stdout)
                    for issue in pylint_issues[:10]:  # Limit to 10 issues per file
                        fix_suggestion = self.get_fix_suggestion(issue)
                        issues.append({
                            'file': issue.get('path', file_path),
                            'line': issue.get('line', 0),
                            'type': issue.get('type', 'warning'),
                            'message': issue.get('message', ''),
                            'code': issue.get('symbol', ''),
                            'fix': fix_suggestion
                        })
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"Error in pylint analysis: {e}")
            
        # Run flake8 for style issues
        try:
            cmd = ['flake8', file_path, '--max-line-length=100']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                for line in result.stdout.strip().split('\n')[:5]:  # Limit to 5 issues
                    if ':' in line:
                        parts = line.split(':', 3)
                        if len(parts) >= 4:
                            issues.append({
                                'file': parts[0],
                                'line': int(parts[1]) if parts[1].isdigit() else 0,
                                'type': 'style',
                                'message': parts[3].strip(),
                                'code': parts[3].split()[0] if parts[3].strip() else '',
                                'fix': self.get_style_fix(parts[3].split()[0] if parts[3].strip() else '')
                            })
        except Exception as e:
            print(f"Error in flake8 analysis: {e}")
            
        return issues
    
    def get_fix_suggestion(self, issue: Dict) -> str:
        """Generate specific fix suggestions based on issue type"""
        symbol = issue.get('symbol', '')
        message = issue.get('message', '')
        
        fixes = {
            'missing-module-docstring': '''Add module docstring at the top of the file:
"""
Module description here.

This module handles...
"""''',
            'missing-function-docstring': '''Add function docstring:
def function_name():
    """
    Brief description of function.
    
    Returns:
        Description of return value
    """''',
            'invalid-name': 'Rename to follow Python conventions:\n- Classes: CamelCase\n- Functions/variables: snake_case\n- Constants: UPPER_SNAKE_CASE',
            'line-too-long': '''Break long lines:
# Use parentheses for implicit line continuation
result = (very_long_function_call(param1, param2)
          .another_method(param3, param4))''',
            'unused-import': 'Remove the unused import or add # noqa comment if needed for side effects',
            'unused-variable': 'Remove the unused variable or use it in your code',
            'undefined-variable': 'Import or define the variable before using it'
        }
        
        return fixes.get(symbol, f'Fix: {message}')
    
    def get_style_fix(self, code: str) -> str:
        """Get style-specific fixes"""
        style_fixes = {
            'E501': 'Line too long - use parentheses or backslash to break it',
            'E302': 'Add 2 blank lines before class/function definition',
            'E303': 'Remove extra blank lines (max 2 consecutive)',
            'F401': 'Remove unused import',
            'E231': 'Add missing whitespace after comma',
            'E225': 'Add missing whitespace around operators',
            'W291': 'Remove trailing whitespace',
            'E501': '''Break long line:
# Before
very_long_line = function_call(param1, param2, param3, param4, param5)

# After
very_long_line = function_call(
    param1, param2, param3,
    param4, param5
)'''
        }
        
        return style_fixes.get(code, 'Fix code style issue')
    
    def analyze_security(self, file_path: str) -> List[Dict]:
        """Run security analysis with actionable fixes"""
        security_issues = []
        
        try:
            cmd = ['bandit', '-f', 'json', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                try:
                    bandit_results = json.loads(result.stdout)
                    for issue in bandit_results.get('results', [])[:5]:  # Limit to 5
                        security_issues.append({
                            'severity': issue.get('issue_severity', 'MEDIUM'),
                            'confidence': issue.get('issue_confidence', 'MEDIUM'),
                            'file': issue.get('filename', ''),
                            'line': issue.get('line_number', 0),
                            'issue': issue.get('issue_text', ''),
                            'fix': self.get_security_fix(issue)
                        })
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"Error in security analysis: {e}")
            
        return security_issues
    
    def get_security_fix(self, issue: Dict) -> str:
        """Get security-specific fixes"""
        test_id = issue.get('test_id', '')
        
        security_fixes = {
            'B201': '''Use production WSGI server:
# Instead of app.run()
# Use: gunicorn app:app --bind 0.0.0.0:8000''',
            'B301': '''Use defusedxml for XML parsing:
# Instead of: import xml.etree.ElementTree as ET
import defusedxml.ElementTree as ET''',
            'B303': '''Use SHA256 instead of MD5:
import hashlib
# Instead of: hashlib.md5(data)
hash_value = hashlib.sha256(data.encode()).hexdigest()''',
            'B306': '''Use mkstemp for temp files:
import tempfile
# Instead of: tempfile.mktemp()
fd, temp_path = tempfile.mkstemp()
os.close(fd)''',
            'B404': '''Avoid shell=True in subprocess:
# Instead of: subprocess.run(cmd, shell=True)
subprocess.run(["command", "arg1", "arg2"])''',
            'B608': '''Use parameterized SQL queries:
# Instead of: f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))'''
        }
        
        return security_fixes.get(test_id, 'Review and fix security issue')
    
    def analyze_performance(self, file_path: str) -> List[Dict]:
        """Analyze performance issues"""
        perf_tips = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Check for common performance issues
            for i, line in enumerate(lines, 1):
                # String concatenation in loops
                if 'for' in line and i < len(lines) - 2:
                    next_lines = '\n'.join(lines[i:i+3])
                    if '+=' in next_lines and ('str(' in next_lines or '"' in next_lines):
                        perf_tips.append({
                            'line': i,
                            'issue': 'String concatenation in loop',
                            'fix': '''Use list and join:
results = []
for item in items:
    results.append(str(item))
final_string = ''.join(results)'''
                        })
                
                # List membership test
                if ' in ' in line and ('[' in line or 'list(' in line):
                    perf_tips.append({
                        'line': i,
                        'issue': 'List membership test (O(n))',
                        'fix': '''Convert to set for O(1) lookup:
# Before: if item in my_list:
my_set = set(my_list)
if item in my_set:'''
                    })
                    
        except Exception as e:
            print(f"Error in performance analysis: {e}")
            
        return perf_tips[:3]  # Limit to 3 tips
    
    def get_quick_wins(self, file_path: str) -> List[Dict]:
        """Identify quick wins that can be fixed immediately"""
        quick_wins = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines, 1):
                # Trailing whitespace
                if line.rstrip() != line.rstrip('\n').rstrip('\r'):
                    quick_wins.append({
                        'line': i,
                        'issue': 'Trailing whitespace',
                        'fix': 'Remove whitespace at end of line'
                    })
                
                # TODO comments
                if 'TODO' in line or 'FIXME' in line:
                    quick_wins.append({
                        'line': i,
                        'issue': f'Unresolved {line.strip()}',
                        'fix': 'Address the TODO or create a GitHub issue to track it'
                    })
                
                # Print statements in production
                if 'print(' in line and not any(x in file_path.lower() for x in ['test', 'example', 'debug']):
                    quick_wins.append({
                        'line': i,
                        'issue': 'Print statement in production code',
                        'fix': '''Replace with logging:
import logging
logger = logging.getLogger(__name__)
logger.info("Your message here")'''
                    })
                    
        except Exception as e:
            print(f"Error finding quick wins: {e}")
            
        return quick_wins[:5]  # Limit to 5
    
    def analyze_file(self, file_path: str):
        """Run all analyses on a file"""
        if not os.path.exists(file_path):
            return
            
        if not file_path.endswith('.py'):
            return
            
        print(f"Analyzing {file_path}...")
        
        # Code quality
        code_issues = self.analyze_code_quality(file_path)
        self.results['code_analysis'].extend(code_issues)
        
        # Security
        security_issues = self.analyze_security(file_path)
        self.results['security_issues'].extend(security_issues)
        
        # Performance
        perf_tips = self.analyze_performance(file_path)
        self.results['performance_tips'].extend(perf_tips)
        
        # Quick wins
        quick_wins = self.get_quick_wins(file_path)
        self.results['quick_wins'].extend(quick_wins)
    
    def generate_report(self) -> str:
        """Generate practical markdown report"""
        report = "## 🔧 Practical Issue Analysis Report\n\n"
        
        # Quick Wins Section
        if self.results['quick_wins']:
            report += "### 🎯 Quick Wins (Fix These First!)\n\n"
            report += "These are simple fixes that take < 1 minute:\n\n"
            
            for win in self.results['quick_wins'][:5]:
                report += f"**Line {win['line']}**: {win['issue']}\n"
                if '\n' in win['fix']:
                    report += f"```python\n{win['fix']}\n```\n\n"
                else:
                    report += f"- {win['fix']}\n\n"
        
        # Critical Security Issues
        critical_security = [s for s in self.results['security_issues'] if s['severity'] == 'HIGH']
        if critical_security:
            report += "### 🚨 Critical Security Issues\n\n"
            report += "**Fix these immediately to prevent vulnerabilities:**\n\n"
            
            for issue in critical_security[:3]:
                report += f"**{issue['file']}:{issue['line']}** - {issue['issue']}\n"
                report += f"```python\n{issue['fix']}\n```\n\n"
        
        # Code Quality Issues
        if self.results['code_analysis']:
            report += "### 📊 Code Quality Issues\n\n"
            
            errors = [i for i in self.results['code_analysis'] if i['type'] == 'error']
            if errors:
                report += "**❌ Errors (Must Fix):**\n\n"
                for error in errors[:3]:
                    report += f"- **{error['file']}:{error['line']}** - {error['message']}\n"
                    report += f"  ```python\n  {error['fix']}\n  ```\n\n"
        
        # Performance Tips
        if self.results['performance_tips']:
            report += "### ⚡ Performance Optimizations\n\n"
            for tip in self.results['performance_tips'][:2]:
                report += f"**Line {tip['line']}**: {tip['issue']}\n"
                report += f"```python\n{tip['fix']}\n```\n\n"
        
        # Action Summary
        report += "### 📋 Action Summary\n\n"
        report += f"1. **🔴 Critical**: Fix {len(critical_security)} security issues\n"
        report += f"2. **🟡 Important**: Address {len(self.results['quick_wins'])} quick wins\n"
        report += f"3. **🟢 Good Practice**: Resolve {len(self.results['code_analysis'])} code quality issues\n\n"
        
        # Commands to run
        report += "### 🛠️ Fix Commands\n\n"
        report += "```bash\n"
        report += "# Auto-format code\n"
        report += "black . --line-length 100\n\n"
        report += "# Fix import sorting\n"
        report += "isort . --profile black\n\n"
        report += "# Security scan\n"
        report += "bandit -r . -ll\n\n"
        report += "# Type checking\n"
        report += "mypy . --ignore-missing-imports\n"
        report += "```\n\n"
        
        report += "💡 **Next Step**: Start with the quick wins above - they'll improve your code immediately!"
        
        return report
    
    def run(self):
        """Main analysis runner"""
        try:
            # Get files to analyze
            files_to_analyze = []
            
            # Check if this is a PR
            if os.environ.get('GITHUB_EVENT_NAME') == 'pull_request':
                # Get changed files in PR
                base_ref = os.environ.get('GITHUB_BASE_REF', 'main')
                cmd = f"git diff --name-only origin/{base_ref}...HEAD"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    files_to_analyze = [f for f in result.stdout.strip().split('\n') if f.endswith('.py')]
            
            # If no files from git or not a PR, analyze recent Python files
            if not files_to_analyze:
                cmd = "find . -name '*.py' -type f -not -path '*/\.*' | head -10"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    files_to_analyze = result.stdout.strip().split('\n')
            
            # Analyze files
            for file in files_to_analyze[:10]:  # Limit to 10 files
                if file and os.path.exists(file):
                    self.analyze_file(file)
            
            # Generate report
            report = self.generate_report()
            
            # Save report
            with open('analysis_report.md', 'w') as f:
                f.write(report)
            
            print("Analysis complete! Report saved to analysis_report.md")
                
        except Exception as e:
            print(f"Error in analysis: {e}")
            traceback.print_exc()
            
            # Create a simple report even on error
            fallback_report = """## 🔧 Practical Issue Analysis Report

### 📋 Quick Coding Best Practices

**1. Code Quality:**
- Use `black` for formatting
- Run `flake8` for style issues
- Add docstrings to all functions

**2. Common Python Fixes:**
```python
# Use f-strings instead of .format()
name = "user"
print(f"Hello {name}")  # Good
print("Hello {}".format(name))  # Avoid

# Use context managers for files
with open('file.txt') as f:
    content = f.read()  # File auto-closes

# Handle exceptions properly
try:
    risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
```

**3. Run These Commands:**
```bash
pip install black flake8 pylint
black .
flake8 .
```
"""
            with open('analysis_report.md', 'w') as f:
                f.write(fallback_report)

if __name__ == "__main__":
    analyzer = PracticalAnalyzer()
    analyzer.run()