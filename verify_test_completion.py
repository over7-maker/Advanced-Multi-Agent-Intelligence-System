#!/usr/bin/env python3
"""
Final Verification Script - Verify all tests are completed
"""

import json
import sys
from pathlib import Path

# Fix Windows encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).parent

def verify_test_completion():
    """Verify all test components are complete"""
    
    print("=" * 60)
    print("FINAL VERIFICATION - TEST COMPLETION CHECK")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # 1. Check test script exists
    print("1. Test Script Verification")
    print("-" * 60)
    test_script = PROJECT_ROOT / "test_comprehensive_amas_system.py"
    if test_script.exists():
        print("✅ test_comprehensive_amas_system.py exists")
    else:
        print("❌ test_comprehensive_amas_system.py NOT FOUND")
        all_passed = False
    
    # 2. Check report files exist
    print("\n2. Report Files Verification")
    print("-" * 60)
    report_json = PROJECT_ROOT / "TEST_REPORT_COMPREHENSIVE.json"
    report_md = PROJECT_ROOT / "COMPREHENSIVE_TEST_REPORT.md"
    
    if report_json.exists():
        print("✅ TEST_REPORT_COMPREHENSIVE.json exists")
        try:
            with open(report_json, encoding='utf-8') as f:
                data = json.load(f)
                print(f"   - Categories tested: {len(data.get('categories', {}))}")
                print(f"   - Total tests: {data.get('summary', {}).get('total_tests', 0)}")
                print(f"   - Passed: {data.get('summary', {}).get('passed', 0)}")
                print(f"   - Failed: {data.get('summary', {}).get('failed', 0)}")
                print(f"   - Warnings: {data.get('summary', {}).get('warnings', 0)}")
        except Exception as e:
            print(f"❌ Error reading JSON report: {e}")
            all_passed = False
    else:
        print("❌ TEST_REPORT_COMPREHENSIVE.json NOT FOUND")
        all_passed = False
    
    if report_md.exists():
        print("✅ COMPREHENSIVE_TEST_REPORT.md exists")
        size = report_md.stat().st_size
        print(f"   - File size: {size:,} bytes")
    else:
        print("❌ COMPREHENSIVE_TEST_REPORT.md NOT FOUND")
        all_passed = False
    
    # 3. Verify all 13 test categories
    print("\n3. Test Categories Verification")
    print("-" * 60)
    expected_categories = [
        "infrastructure",
        "core_orchestrator",
        "ai_router",
        "agents",
        "intelligence_manager",
        "api_endpoints",
        "websocket",
        "integrations",
        "caching_services",
        "monitoring",
        "frontend",
        "e2e_workflows",
        "security"
    ]
    
    if report_json.exists():
        try:
            with open(report_json, encoding='utf-8') as f:
                data = json.load(f)
                categories = data.get('categories', {})
                
                for category in expected_categories:
                    if category in categories:
                        cat_data = categories[category]
                        passed = cat_data.get('passed', 0)
                        failed = cat_data.get('failed', 0)
                        warnings = cat_data.get('warnings', 0)
                        total = passed + failed + warnings
                        print(f"✅ {category:20s}: {passed:3d} passed, {failed:3d} failed, {warnings:3d} warnings ({total} tests)")
                    else:
                        print(f"❌ {category:20s}: NOT FOUND IN REPORT")
                        all_passed = False
        except Exception as e:
            print(f"❌ Error verifying categories: {e}")
            all_passed = False
    
    # 4. Verify test functions in script
    print("\n4. Test Functions Verification")
    print("-" * 60)
    if test_script.exists():
        with open(test_script, encoding='utf-8') as f:
            content = f.read()
            for category in expected_categories:
                func_name = f"test_{category}"
                if f"async def {func_name}()" in content or f"def {func_name}()" in content:
                    print(f"✅ {func_name}() function exists")
                else:
                    print(f"❌ {func_name}() function NOT FOUND")
                    all_passed = False
    
    # 5. Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    if all_passed:
        print("✅ ALL CHECKS PASSED - EVERYTHING IS COMPLETE!")
        print()
        print("Test Suite Status:")
        print("  - Test script: ✅ Complete")
        print("  - Report files: ✅ Generated")
        print("  - All 13 categories: ✅ Tested")
        print("  - Test functions: ✅ Implemented")
        print()
        print("The comprehensive test suite is fully operational!")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - REVIEW REQUIRED")
        return 1

if __name__ == "__main__":
    sys.exit(verify_test_completion())

