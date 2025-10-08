#!/usr/bin/env python3
"""
Comprehensive Test Runner for AMAS
Runs all tests and measures meaningful coverage
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=300
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": "Command timed out",
            "success": False,
        }
    except Exception as e:
        return {"returncode": -1, "stdout": "", "stderr": str(e), "success": False}


def install_test_dependencies():
    """Install test dependencies"""
    print("📦 Installing test dependencies...")

    dependencies = [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
        "pytest-mock>=3.10.0",
        "aiohttp>=3.8.0",
        "beautifulsoup4>=4.11.0",
    ]

    for dep in dependencies:
        print(f"  Installing {dep}...")
        result = run_command(f"pip install {dep}")
        if not result["success"]:
            print(f"  ❌ Failed to install {dep}: {result['stderr']}")
        else:
            print(f"  ✅ Installed {dep}")


def run_tests_with_coverage():
    """Run tests with coverage measurement"""
    print("\n🧪 Running comprehensive test suite...")

    # Test files to run
    test_files = [
        "tests/test_unified_orchestrator_real.py",
        "tests/test_minimal_config_real.py",
        "tests/test_services.py",
        "tests/test_security_fixes.py",
    ]

    # Run tests with coverage
    cmd = [
        "python",
        "-m",
        "pytest",
        "--cov=src/amas",
        "--cov-report=json:coverage.json",
        "--cov-report=html:htmlcov",
        "--cov-report=term-missing",
        "-v",
        "--tb=short",
    ] + test_files

    print(f"Running: {' '.join(cmd)}")
    result = run_command(" ".join(cmd))

    return result


def analyze_coverage():
    """Analyze test coverage results"""
    print("\n📊 Analyzing test coverage...")

    coverage_file = Path("coverage.json")
    if not coverage_file.exists():
        print("❌ Coverage file not found")
        return None

    try:
        with open(coverage_file, "r") as f:
            coverage_data = json.load(f)

        total_lines = coverage_data["totals"]["num_statements"]
        covered_lines = coverage_data["totals"]["covered_lines"]
        missing_lines = coverage_data["totals"]["missing_lines"]
        coverage_percent = coverage_data["totals"]["percent_covered"]

        print(f"📈 Coverage Summary:")
        print(f"  Total lines: {total_lines}")
        print(f"  Covered lines: {covered_lines}")
        print(f"  Missing lines: {missing_lines}")
        print(f"  Coverage: {coverage_percent:.1f}%")

        # Analyze by module
        print(f"\n📋 Coverage by Module:")
        for module, data in coverage_data["files"].items():
            if "src/amas" in module:
                module_name = module.replace("src/amas/", "")
                percent = data["summary"]["percent_covered"]
                print(f"  {module_name}: {percent:.1f}%")

        return {
            "total_lines": total_lines,
            "covered_lines": covered_lines,
            "missing_lines": missing_lines,
            "coverage_percent": coverage_percent,
            "files": coverage_data["files"],
        }

    except Exception as e:
        print(f"❌ Error analyzing coverage: {e}")
        return None


def run_environment_validation():
    """Run environment validation"""
    print("\n🔍 Running environment validation...")

    result = run_command("python validate_environment.py")

    if result["success"]:
        print("✅ Environment validation passed")
        print(result["stdout"])
    else:
        print("❌ Environment validation failed")
        print(result["stderr"])

    return result["success"]


def run_unified_orchestrator_demo():
    """Run unified orchestrator demo"""
    print("\n🚀 Running unified orchestrator demo...")

    result = run_command("python start_amas_unified.py")

    if result["success"]:
        print("✅ Unified orchestrator demo completed")
    else:
        print("❌ Unified orchestrator demo failed")
        print(result["stderr"])

    return result["success"]


def generate_test_report(test_result, coverage_data, env_validation, demo_result):
    """Generate comprehensive test report"""
    print("\n📋 Generating test report...")

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_execution": {
            "success": test_result["success"],
            "returncode": test_result["returncode"],
            "stdout_lines": len(test_result["stdout"].split("\n")),
            "stderr_lines": len(test_result["stderr"].split("\n")),
        },
        "coverage": coverage_data,
        "environment_validation": env_validation,
        "unified_orchestrator_demo": demo_result,
        "overall_status": (
            "PASS"
            if all(
                [
                    test_result["success"],
                    coverage_data and coverage_data["coverage_percent"] >= 80,
                    env_validation,
                    demo_result,
                ]
            )
            else "FAIL"
        ),
    }

    # Save report
    with open("test_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"📄 Test report saved to test_report.json")

    return report


def main():
    """Main test runner function"""
    print("🧪 AMAS Comprehensive Test Suite")
    print("=" * 50)

    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    # Install dependencies
    install_test_dependencies()

    # Run environment validation
    env_validation = run_environment_validation()

    # Run tests with coverage
    test_result = run_tests_with_coverage()

    # Analyze coverage
    coverage_data = analyze_coverage()

    # Run unified orchestrator demo
    demo_result = run_unified_orchestrator_demo()

    # Generate report
    report = generate_test_report(
        test_result, coverage_data, env_validation, demo_result
    )

    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    print(f"Test Execution: {'✅ PASS' if test_result['success'] else '❌ FAIL'}")

    if coverage_data:
        coverage_status = (
            "✅ PASS" if coverage_data["coverage_percent"] >= 80 else "❌ FAIL"
        )
        print(
            f"Test Coverage: {coverage_status} ({coverage_data['coverage_percent']:.1f}%)"
        )
    else:
        print("Test Coverage: ❌ FAIL (No data)")

    print(f"Environment Validation: {'✅ PASS' if env_validation else '❌ FAIL'}")
    print(f"Unified Orchestrator Demo: {'✅ PASS' if demo_result else '❌ FAIL'}")

    print(f"\nOverall Status: {report['overall_status']}")

    if report["overall_status"] == "PASS":
        print("\n🎉 All tests passed! AMAS is ready for production.")
    else:
        print("\n⚠️  Some tests failed. Please review the results above.")

    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Test execution interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
