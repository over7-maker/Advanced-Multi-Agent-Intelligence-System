#!/usr/bin/env python3
"""
Verification script to test that security false positives have been fixed
"""

import os
import subprocess
import sys



def test_files():
    """Test files that previously had false positives"""
    files_to_test = [
        ".github/scripts/advanced_multi_agent_orchestrator.py",
        ".github/scripts/ai_adaptive_prompt_improvement.py",
        ".github/scripts/ai_enhanced_code_review.py",
        ".github/scripts/ai_incident_response.py",
        ".github/scripts/ai_master_orchestrator.py",
        ".github/scripts/ai_security_scanner.py",
    ]

    print("🔍 Testing security scanners for false positives...")
    print("=" * 60)

    # Test with ai_code_analyzer.py
    print("\n📊 Testing with ai_code_analyzer.py...")
    sys.path.insert(0, ".github/scripts")
    from ai_code_analyzer import AICodeAnalyzer

    analyzer = AICodeAnalyzer()
    total_issues = 0

    for file_path in files_to_test:
        if os.path.exists(file_path):
            print(f"\nScanning {file_path}...")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                issues = analyzer.analyze_security_issues(file_path, content)
                if issues:
                    print(f"  ❌ Found {len(issues)} issues:")
                    for issue in issues:
                        print(f"    - {issue}")
                    total_issues += len(issues)
                else:
                    print(f"  ✅ No issues found")
            except Exception as e:
                print(f"  ⚠️ Error scanning file: {e}")

    print(f"\n{'='*60}")
    print(f"Total issues found: {total_issues}")

    if total_issues == 0:
        print("✅ SUCCESS: All false positives have been fixed!")
    else:
        print("❌ FAILED: Some false positives still exist")

    return total_issues == 0


def test_specific_patterns():
    """Test specific patterns that were causing false positives"""
    print("\n\n🧪 Testing specific patterns...")
    print("=" * 60)

    test_cases = [
        {
            "name": "Environment variable token assignment",
            "content": 'self.github_token = os.environ.get("GITHUB_TOKEN")',
            "should_flag": False,
        },
        {
            "name": 'Description with "des" word',
            "content": 'description = "This describes the function"',
            "should_flag": False,
        },
        {
            "name": "Pattern definition",
            "content": "'weak_crypto': ['md5', 'sha1', 'des']",
            "should_flag": False,
        },
        {
            "name": "Actual hardcoded password",
            "content": 'password = "secretpassword123"',
            "should_flag": True,
        },
        {
            "name": "Actual DES usage",
            "content": "cipher = DES.new(key, DES.MODE_ECB)",
            "should_flag": True,
        },
    ]

    sys.path.insert(0, ".github/scripts")
    from ai_code_analyzer import AICodeAnalyzer

    analyzer = AICodeAnalyzer()
    passed = 0
    failed = 0

    for test in test_cases:
        issues = analyzer.analyze_security_issues("test.py", test["content"])
        has_issues = len(issues) > 0

        if has_issues == test["should_flag"]:
            print(f"✅ PASS: {test['name']}")
            passed += 1
        else:
            print(f"❌ FAIL: {test['name']}")
            print(f"   Expected: {'flag' if test['should_flag'] else 'no flag'}")
            print(f"   Got: {'flagged' if has_issues else 'not flagged'}")
            if issues:
                print(f"   Issues: {issues}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Test Results: {passed} passed, {failed} failed")

    return failed == 0


if __name__ == "__main__":
    print("🔒 Security Fix Verification Tool")
    print("=" * 60)

    # Test all files
    files_ok = test_files()

    # Test specific patterns
    patterns_ok = test_specific_patterns()

    # Overall result
    print("\n\n📊 OVERALL RESULT")
    print("=" * 60)

    if files_ok and patterns_ok:
        print("✅ ALL TESTS PASSED - Security issues have been resolved!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - Please review the results above")
        sys.exit(1)
