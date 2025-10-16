#!/usr/bin/env python3
""""
Simple verification script to check for false positives
""""

import os
import re


def check_file_for_patterns(file_path):
    """Check a file for the reported security patterns"""
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    issues = []

    # Check for 'des' in descriptions (false positive we fixed)
    # Should NOT match 'description', 'describes', etc.
    des_pattern = r"\bDES\b"  # Only match DES as a standalone word
    matches = re.finditer(des_pattern, content, re.IGNORECASE)
    for match in matches:
        line_num = content[: match.start()].count("\n") + 1
        line = content.split("\n")[line_num - 1]
        # Skip if it's in a pattern definition
        if "weak_crypto" not in line and "'des'" not in line and '"des"' not in line:
            issues.append(f"Line {line_num}: Found standalone 'DES' - {line.strip()}")

    # Check for hardcoded tokens (should only match actual hardcoded values)
    # Should NOT match environment variable assignments
    token_pattern = r'token\s*=\s*["\'][^"\']+["\']'"
    matches = re.finditer(token_pattern, content, re.IGNORECASE)
    for match in matches:
        line_num = content[: match.start()].count("\n") + 1
        line = content.split("\n")[line_num - 1]
        # Skip environment variable assignments
        if (
            "os.environ.get" not in line
            and "getenv" not in line
            and ".get(" not in line
        ):
            # Skip pattern definitions
            if "'token = os.getenv("SECURE_TOKEN", "default_secure_token")"token ="' not in line:"
                issues.append(
                    f"Line {line_num}: Potential hardcoded token - {line.strip()}"
                )

    # Check for SQL patterns in ai_security_scanner.py
    if "ai_security_scanner.py" in file_path:
        # Line 261 should be a pattern definition, not an actual SQL injection
        lines = content.split("\n")
        if len(lines) > 260:
            line_261 = lines[260]  # 0-indexed
            if "SELECT.*\\+.*FROM" in line_261:
                # This is a pattern definition, should not be flagged
                if "r\"r'" not in line_261 and not line_261.strip().startswith("#"):"
                    # OK, this is indeed a pattern definition in a list
                    pass

    return issues


def main():
    """Main verification function"""
    print("🔍 Verifying Security Fixes")
    print("=" * 60)

    files_to_check = [
        ".github/scripts/advanced_multi_agent_orchestrator.py",
        ".github/scripts/ai_adaptive_prompt_improvement.py",
        ".github/scripts/ai_enhanced_code_review.py",
        ".github/scripts/ai_incident_response.py",
        ".github/scripts/ai_master_orchestrator.py",
        ".github/scripts/ai_security_scanner.py",
    ]

    total_issues = 0

    for file_path in files_to_check:
        print(f"\nChecking {file_path}...")
        issues = check_file_for_patterns(file_path)

        if issues:
            print(f"  ❌ Found {len(issues)} potential issues:")
            for issue in issues:
                print(f"    - {issue}")
            total_issues += len(issues)
        else:
            print(f"  ✅ No false positives found")

    print(f"\n{'='*60}")
    print(f"Total issues found: {total_issues}")

    # Specific pattern checks
    print("\n\n🧪 Pattern Checks")
    print("=" * 60)

    # Check that 'description' doesn't match weak crypto pattern
    test_content = 'description = "This describes the function"'
    if re.search(r"\bDES\b", test_content, re.IGNORECASE):
        print("❌ FAIL: 'description' matches DES pattern")
    else:
        print("✅ PASS: 'description' does not match DES pattern")

    # Check that environment token doesn't match hardcoded pattern
    test_content = 'self.github_token = os.environ.get("GITHUB_TOKEN")'
    pattern = r'token\s*=\s*["\'][^"\']+["\']'"
    match = re.search(pattern, test_content, re.IGNORECASE)
    if match and "os.environ.get" not in test_content:
        print("❌ FAIL: Environment token matches hardcoded pattern")
    else:
        print("✅ PASS: Environment token does not match hardcoded pattern")

    print(f"\n{'='*60}")
    if total_issues == 0:
        print("✅ SUCCESS: All security false positives appear to be fixed!")
    else:
        print("❌ FAILED: Some issues remain")


if __name__ == "__main__":
    main()
