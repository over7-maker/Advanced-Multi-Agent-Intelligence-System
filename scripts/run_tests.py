#!/usr/bin/env python3
"""
AMAS Test Runner Script

This script provides a comprehensive test runner for the AMAS system with
support for different test types, coverage reporting, and performance testing.

Usage:
    python scripts/run_tests.py --unit                    # Run unit tests only
    python scripts/run_tests.py --integration             # Run integration tests
    python scripts/run_tests.py --all --coverage          # Run all tests with coverage
    python scripts/run_tests.py --benchmark               # Run performance benchmarks
    python scripts/run_tests.py --real                    # Run tests with real services
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def run_command(cmd: List[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n🔧 {description}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False


def run_unit_tests(verbose: bool = False) -> bool:
    """Run unit tests."""
    cmd = ["python", "-m", "pytest", "tests/test_unified_orchestrator.py"]
    if verbose:
        cmd.append("-v")
    cmd.extend(["-m", "unit"])
    return run_command(cmd, "Unit Tests")


def run_integration_tests(verbose: bool = False) -> bool:
    """Run integration tests."""
    cmd = ["python", "-m", "pytest", "tests/"]
    if verbose:
        cmd.append("-v")
    cmd.extend(["-m", "integration"])
    return run_command(cmd, "Integration Tests")


def run_all_tests(verbose: bool = False) -> bool:
    """Run all tests."""
    cmd = ["python", "-m", "pytest", "tests/"]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, "All Tests")


def run_tests_with_coverage(verbose: bool = False) -> bool:
    """Run tests with coverage reporting."""
    cmd = [
        "python", "-m", "pytest", "tests/",
        "--cov=src/amas",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=80"
    ]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, "Tests with Coverage")


def run_benchmark_tests(verbose: bool = False) -> bool:
    """Run benchmark tests."""
    cmd = ["python", "-m", "pytest", "tests/"]
    if verbose:
        cmd.append("-v")
    cmd.extend(["-m", "benchmark"])
    return run_command(cmd, "Benchmark Tests")


def run_real_tests(verbose: bool = False) -> bool:
    """Run tests with real external services."""
    cmd = ["python", "-m", "pytest", "tests/"]
    if verbose:
        cmd.append("-v")
    cmd.extend(["-m", "real"])
    return run_command(cmd, "Real Service Tests")


def run_specific_test(test_path: str, verbose: bool = False) -> bool:
    """Run a specific test file or test function."""
    cmd = ["python", "-m", "pytest", test_path]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, f"Specific Test: {test_path}")


def check_environment() -> bool:
    """Check if the environment is properly set up for testing."""
    print("🔍 Checking test environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    # Check if pytest is installed
    try:
        import pytest
        print(f"✅ pytest version: {pytest.__version__}")
    except ImportError:
        print("❌ pytest is not installed")
        return False
    
    # Check if test files exist
    test_dir = Path("tests")
    if not test_dir.exists():
        print("❌ Tests directory not found")
        return False
    
    # Check if main test file exists
    main_test_file = test_dir / "test_unified_orchestrator.py"
    if not main_test_file.exists():
        print("❌ Main test file not found")
        return False
    
    print("✅ Test environment is ready")
    return True


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="AMAS Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark tests")
    parser.add_argument("--real", action="store_true", help="Run tests with real services")
    parser.add_argument("--test", type=str, help="Run specific test file or function")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--check-env", action="store_true", help="Check test environment only")
    
    args = parser.parse_args()
    
    print("🧪 AMAS Test Runner")
    print("=" * 50)
    
    # Check environment first
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    if args.check_env:
        print("\n✅ Environment check completed successfully")
        return
    
    # Run tests based on arguments
    success = True
    
    if args.unit:
        success &= run_unit_tests(args.verbose)
    
    if args.integration:
        success &= run_integration_tests(args.verbose)
    
    if args.benchmark:
        success &= run_benchmark_tests(args.verbose)
    
    if args.real:
        success &= run_real_tests(args.verbose)
    
    if args.test:
        success &= run_specific_test(args.test, args.verbose)
    
    if args.coverage:
        success &= run_tests_with_coverage(args.verbose)
    
    if args.all or not any([args.unit, args.integration, args.benchmark, args.real, args.test, args.coverage]):
        success &= run_all_tests(args.verbose)
    
    # Print summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()