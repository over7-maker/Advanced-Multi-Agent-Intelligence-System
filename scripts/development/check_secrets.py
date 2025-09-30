#!/usr/bin/env python3
"""
AMAS Secret Detection Script

Scans code for potential secret leaks and security issues.
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class SecretScanner:
    """Scanner for detecting potential secrets in code"""

    # Common secret patterns
    SECRET_PATTERNS = {
        'api_key': re.compile(r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']([a-zA-Z0-9_-]{20,})["\']'),
        'password': re.compile(r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']([^"\']{8,})["\']'),
        'token': re.compile(r'(?i)(token|auth[_-]?token)\s*[=:]\s*["\']([a-zA-Z0-9_-]{20,})["\']'),
        'secret': re.compile(r'(?i)(secret|secret[_-]?key)\s*[=:]\s*["\']([a-zA-Z0-9_-]{20,})["\']'),
        'private_key': re.compile(r'-----BEGIN [A-Z ]+ PRIVATE KEY-----'),
        'aws_key': re.compile(r'AKIA[0-9A-Z]{16}'),
        'gcp_key': re.compile(r'AIza[0-9A-Za-z_-]{35}'),
        'github_token': re.compile(r'ghp_[a-zA-Z0-9]{36}'),
        'jwt': re.compile(r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*'),
    }

    # Files to exclude from scanning
    EXCLUDED_PATTERNS = [
        r'\.git/',
        r'__pycache__/',
        r'\.pyc$',
        r'\.example$',
        r'\.template$',
        r'/archive/',
        r'check_secrets\.py$',  # Don't scan this file itself
    ]

    # Allowed patterns (false positives)
    ALLOWED_PATTERNS = [
        r'your_.*_key_here',
        r'example_.*',
        r'dummy_.*',
        r'test_.*_key',
        r'placeholder_.*',
        r'<.*>',  # Template placeholders
        r'\$\{.*\}',  # Environment variable references
    ]

    def __init__(self):
        self.issues_found = []

    def is_excluded_file(self, file_path: str) -> bool:
        """Check if file should be excluded from scanning"""
        for pattern in self.EXCLUDED_PATTERNS:
            if re.search(pattern, file_path):
                return True
        return False

    def is_allowed_pattern(self, content: str) -> bool:
        """Check if content matches allowed patterns (false positives)"""
        for pattern in self.ALLOWED_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for secrets"""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')

                for pattern_name, pattern in self.SECRET_PATTERNS.items():
                    for match in pattern.finditer(content):
                        matched_text = match.group(0)

                        # Skip if it's an allowed pattern
                        if self.is_allowed_pattern(matched_text):
                            continue

                        # Find line number
                        line_num = content[:match.start()].count('\n') + 1

                        issues.append({
                            'file': str(file_path),
                            'line': line_num,
                            'pattern': pattern_name,
                            'matched_text': matched_text[:50] + '...' if len(matched_text) > 50 else matched_text,
                            'full_line': lines[line_num - 1].strip() if line_num <= len(lines) else ''
                        })

        except Exception as e:
            print(f"Warning: Could not scan {file_path}: {e}")

        return issues

    def scan_directory(self, directory: Path) -> List[Dict]:
        """Scan all files in directory recursively"""
        all_issues = []

        for file_path in directory.rglob('*'):
            if file_path.is_file() and not self.is_excluded_file(str(file_path)):
                # Only scan text files
                if file_path.suffix in ['.py', '.yml', '.yaml', '.json', '.md', '.txt', '.sh', '.env']:
                    issues = self.scan_file(file_path)
                    all_issues.extend(issues)

        return all_issues

    def format_report(self, issues: List[Dict]) -> str:
        """Format scan results as a report"""
        if not issues:
            return "✅ No potential secrets found!"

        report = f"🚨 Found {len(issues)} potential secret(s):\n\n"

        for issue in issues:
            report += f"📁 File: {issue['file']}\n"
            report += f"📍 Line: {issue['line']}\n"
            report += f"🔍 Pattern: {issue['pattern']}\n"
            report += f"💭 Content: {issue['matched_text']}\n"
            report += f"📝 Full line: {issue['full_line']}\n"
            report += "-" * 60 + "\n"

        return report


def main():
    """Main function"""
    scanner = SecretScanner()

    # Scan specific files if provided as arguments
    if len(sys.argv) > 1:
        issues = []
        for file_path in sys.argv[1:]:
            path = Path(file_path)
            if path.exists() and path.is_file():
                issues.extend(scanner.scan_file(path))
    else:
        # Scan entire project
        project_root = Path(__file__).parent.parent.parent
        issues = scanner.scan_directory(project_root)

    # Generate report
    report = scanner.format_report(issues)
    print(report)

    # Exit with error code if secrets found
    if issues:
        print("\n❌ Security check failed: Potential secrets detected!")
        print("Please review and remove any actual secrets before committing.")
        sys.exit(1)
    else:
        print("✅ Security check passed: No secrets detected!")
        sys.exit(0)


if __name__ == "__main__":
    main()
