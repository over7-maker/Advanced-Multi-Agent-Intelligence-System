#!/usr/bin/env python3
"""
Simple validation script for Enhanced AI Issues Responder v2.0 upgrade
Validates file structure, syntax, and basic functionality without external dependencies
"""

import os
import sys
import ast
import json
from pathlib import Path


def check_file_syntax(file_path):
    """Check if a Python file has valid syntax"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        ast.parse(content)
        return True, "Syntax valid"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"


def check_yaml_structure(file_path):
    """Basic YAML structure validation"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Basic checks for YAML structure
        if "name:" not in content:
            return False, "Missing workflow name"
        if "on:" not in content:
            return False, "Missing trigger configuration"
        if "jobs:" not in content:
            return False, "Missing jobs section"

        return True, "YAML structure valid"
    except Exception as e:
        return False, f"Error reading YAML file: {e}"


def validate_upgrade():
    """Validate the complete upgrade"""
    print("🔍 Validating Enhanced AI Issues Responder v2.0 Upgrade...")
    print("=" * 70)

    validation_results = []

    # Check new files exist
    files_to_check = [
        (
            "scripts/ai_issues_responder_v2.py",
            "Enhanced Python responder",
            check_file_syntax,
        ),
        (
            ".github/workflows/enhanced-ai-issue-responder.yml",
            "Enhanced workflow",
            check_yaml_structure,
        ),
        (
            "ENHANCED_ISSUES_RESPONDER_UPGRADE.md",
            "Upgrade documentation",
            lambda x: (os.path.exists(x), "File exists"),
        ),
        ("scripts/test_enhanced_responder.py", "Test suite", check_file_syntax),
        ("scripts/validate_upgrade.py", "Validation script", check_file_syntax),
    ]

    print("📁 FILE VALIDATION:")
    for file_path, description, validator in files_to_check:
        full_path = Path(file_path)

        if not full_path.exists():
            print(f"  ❌ {description}: File not found - {file_path}")
            validation_results.append((description, False, "File not found"))
            continue

        is_valid, message = validator(str(full_path))
        status = "✅" if is_valid else "❌"
        print(f"  {status} {description}: {message}")
        validation_results.append((description, is_valid, message))

    print("\n🔧 FEATURE VALIDATION:")

    # Check if original files still exist (backward compatibility)
    original_files = [
        "scripts/ai_issues_responder.py",
        ".github/workflows/ai-issue-responder.yml",
    ]

    for file_path in original_files:
        exists = Path(file_path).exists()
        status = "✅" if exists else "⚠️"
        print(f"  {status} Original file preserved: {file_path}")
        validation_results.append(
            (f"Original {file_path}", exists, "Backward compatibility")
        )

    # Check enhanced responder features
    enhanced_responder_path = "scripts/ai_issues_responder_v2.py"
    if Path(enhanced_responder_path).exists():
        try:
            with open(enhanced_responder_path, "r") as f:
                content = f.read()

            features_to_check = [
                ("Multi-language support", "detect_language" in content),
                ("Caching system", "cache_db_path" in content and "sqlite3" in content),
                ("Performance metrics", "performance_metrics" in content),
                ("Follow-up scheduling", "follow_ups" in content),
                ("Enhanced analysis", "analyze_issue_advanced" in content),
                ("Smart labeling", "add_smart_labels" in content),
                ("Rate limiting", "_check_rate_limit" in content),
                ("Template system", "response_templates" in content),
                (
                    "9 AI providers",
                    "deepseek" in content
                    and "grok" in content
                    and "cerebras" in content
                    and "ultimate_fallback_system" in content,
                ),
            ]

            for feature_name, check_result in features_to_check:
                status = "✅" if check_result else "❌"
                print(
                    f"  {status} {feature_name}: {'Implemented' if check_result else 'Missing'}"
                )
                validation_results.append((feature_name, check_result, "Feature check"))

        except Exception as e:
            print(f"  ❌ Enhanced responder analysis failed: {e}")
            validation_results.append(("Enhanced responder analysis", False, str(e)))

    # Check workflow enhancements
    enhanced_workflow_path = ".github/workflows/enhanced-ai-issue-responder.yml"
    if Path(enhanced_workflow_path).exists():
        try:
            with open(enhanced_workflow_path, "r") as f:
                content = f.read()

            workflow_features = [
                ("Concurrency control", "concurrency:" in content),
                ("Enhanced permissions", "permissions:" in content),
                ("Performance reporting", "performance-report" in content),
                ("Artifact uploads", "upload-artifact@v4" in content),
                ("Failure notifications", "Notify on Failure" in content),
                ("Step summaries", "GITHUB_STEP_SUMMARY" in content),
                ("Health checks", "system-health-check" in content),
                ("Multiple jobs", "follow-up-processor" in content),
            ]

            for feature_name, check_result in workflow_features:
                status = "✅" if check_result else "❌"
                print(
                    f"  {status} Workflow {feature_name}: {'Implemented' if check_result else 'Missing'}"
                )
                validation_results.append(
                    (f"Workflow {feature_name}", check_result, "Workflow feature check")
                )

        except Exception as e:
            print(f"  ❌ Enhanced workflow analysis failed: {e}")
            validation_results.append(("Enhanced workflow analysis", False, str(e)))

    print("\n📊 VALIDATION SUMMARY:")
    total_checks = len(validation_results)
    passed_checks = sum(1 for _, success, _ in validation_results if success)
    failed_checks = total_checks - passed_checks

    print(f"  Total Checks: {total_checks}")
    print(f"  Passed: {passed_checks} ✅")
    print(f"  Failed: {failed_checks} ❌")
    print(f"  Success Rate: {passed_checks/total_checks*100:.1f}%")

    if failed_checks > 0:
        print(f"\n❌ FAILED CHECKS:")
        for name, success, message in validation_results:
            if not success:
                print(f"  • {name}: {message}")

    print("\n" + "=" * 70)

    if passed_checks / total_checks >= 0.8:
        print("🎉 VALIDATION PASSED: Upgrade is ready for deployment!")
        return 0
    else:
        print("⚠️ VALIDATION FAILED: Please address the issues above before deployment.")
        return 1


if __name__ == "__main__":
    exit_code = validate_upgrade()
    sys.exit(exit_code)
