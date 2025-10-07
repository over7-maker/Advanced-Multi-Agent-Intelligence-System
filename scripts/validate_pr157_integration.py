#!/usr/bin/env python3
"""
Validation script for PR #157 integration
Ensures test suite fixes are properly integrated without regressions
"""

import asyncio
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class Colors:
    """ANSI color codes for terminal output"""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


class IntegrationValidator:
    """Validates PR #157 integration"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "pr_number": 157,
            "checks": {},
            "summary": {"total": 0, "passed": 0, "failed": 0, "warnings": 0},
        }
        self.project_root = Path(__file__).parent.parent

    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

    def print_status(self, check: str, status: str, message: str = ""):
        """Print check status"""
        if status == "PASS":
            symbol = f"{Colors.GREEN}✓{Colors.END}"
            status_color = Colors.GREEN
        elif status == "FAIL":
            symbol = f"{Colors.RED}✗{Colors.END}"
            status_color = Colors.RED
        else:  # WARNING
            symbol = f"{Colors.YELLOW}⚠{Colors.END}"
            status_color = Colors.YELLOW

        print(f"{symbol} {check:.<50} {status_color}{status}{Colors.END}")
        if message:
            print(f"  {Colors.YELLOW}{message}{Colors.END}")

    def run_command(self, cmd: List[str], check: bool = True) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_root, check=check
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout, e.stderr
        except Exception as e:
            return -1, "", str(e)

    async def check_async_fixtures(self) -> Dict[str, any]:
        """Check for async fixture warnings"""
        self.print_header("Checking Async Fixtures")

        cmd = [
            "python",
            "-m",
            "pytest",
            "tests/conftest.py",
            "-v",
            "-W",
            "error::RuntimeWarning",
            "--tb=short",
        ]
        returncode, stdout, stderr = self.run_command(cmd, check=False)

        check_result = {
            "status": "PASS" if returncode == 0 else "FAIL",
            "details": {
                "command": " ".join(cmd),
                "returncode": returncode,
                "warnings_found": "coroutine was never awaited" in stderr,
            },
        }

        if returncode != 0 and "coroutine was never awaited" in stderr:
            check_result["message"] = "Async fixture warnings detected!"
            self.print_status("Async Fixtures Check", "FAIL", check_result["message"])
        else:
            self.print_status("Async Fixtures Check", "PASS")

        self.results["checks"]["async_fixtures"] = check_result
        return check_result

    async def check_task_structure(self) -> Dict[str, any]:
        """Verify new task structure is properly implemented"""
        self.print_header("Checking Task Structure")

        # Check for old submit_task signatures
        cmd = ["grep", "-r", "submit_task.*title=", "tests/", "--include=*.py"]
        returncode, stdout, stderr = self.run_command(cmd, check=False)

        check_result = {"status": "PASS", "details": {"old_signatures_found": []}}

        if returncode == 0 and stdout.strip():
            # Found old signatures
            old_sigs = stdout.strip().split("\n")
            check_result["status"] = "FAIL"
            check_result["details"]["old_signatures_found"] = old_sigs[:5]  # First 5
            check_result["message"] = (
                f"Found {len(old_sigs)} old submit_task signatures"
            )
            self.print_status("Task Structure Check", "FAIL", check_result["message"])
        else:
            self.print_status("Task Structure Check", "PASS")

        self.results["checks"]["task_structure"] = check_result
        return check_result

    async def check_imports(self) -> Dict[str, any]:
        """Verify all necessary imports are present"""
        self.print_header("Checking Imports")

        critical_imports = [
            ("tests/conftest.py", "TaskPriority"),
            ("src/amas/core/unified_orchestrator_v2.py", "AgentConfig"),
            ("tests/test_integration.py", "TaskPriority"),
        ]

        check_result = {"status": "PASS", "details": {"missing_imports": []}}

        for filepath, import_name in critical_imports:
            full_path = self.project_root / filepath
            if full_path.exists():
                with open(full_path, "r") as f:
                    content = f.read()
                    if import_name not in content:
                        check_result["details"]["missing_imports"].append(
                            {"file": filepath, "import": import_name}
                        )

        if check_result["details"]["missing_imports"]:
            check_result["status"] = "FAIL"
            check_result["message"] = (
                f"Missing {len(check_result['details']['missing_imports'])} critical imports"
            )
            self.print_status("Import Check", "FAIL", check_result["message"])
        else:
            self.print_status("Import Check", "PASS")

        self.results["checks"]["imports"] = check_result
        return check_result

    async def run_test_suite(self) -> Dict[str, any]:
        """Run the test suite and check for issues"""
        self.print_header("Running Test Suite")

        test_commands = [
            (
                "Unit Tests",
                ["python", "-m", "pytest", "tests/unit/", "-v", "--tb=short"],
            ),
            (
                "Integration Tests",
                ["python", "-m", "pytest", "tests/test_integration.py", "-v"],
            ),
            ("Agent Tests", ["python", "-m", "pytest", "tests/test_agents.py", "-v"]),
        ]

        check_result = {"status": "PASS", "details": {"test_results": {}}}

        for test_name, cmd in test_commands:
            print(f"\nRunning {test_name}...")
            returncode, stdout, stderr = self.run_command(cmd, check=False)

            # Parse pytest output for pass/fail counts
            passed = failed = 0
            for line in stdout.split("\n"):
                if " passed" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed" and i > 0:
                            try:
                                passed = int(parts[i - 1])
                            except:
                                pass
                if " failed" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "failed" and i > 0:
                            try:
                                failed = int(parts[i - 1])
                            except:
                                pass

            test_result = {
                "returncode": returncode,
                "passed": passed,
                "failed": failed,
                "success": returncode == 0,
            }

            check_result["details"]["test_results"][test_name] = test_result

            if returncode != 0:
                check_result["status"] = "FAIL"
                self.print_status(test_name, "FAIL", f"{failed} tests failed")
            else:
                self.print_status(test_name, "PASS", f"{passed} tests passed")

        self.results["checks"]["test_suite"] = check_result
        return check_result

    async def check_coverage(self) -> Dict[str, any]:
        """Check test coverage"""
        self.print_header("Checking Test Coverage")

        cmd = ["python", "-m", "pytest", "--cov=amas", "--cov-report=term", "--quiet"]
        returncode, stdout, stderr = self.run_command(cmd, check=False)

        check_result = {"status": "PASS", "details": {"coverage_percentage": 0}}

        # Parse coverage percentage
        for line in stdout.split("\n"):
            if "TOTAL" in line and "%" in line:
                parts = line.split()
                for part in parts:
                    if part.endswith("%"):
                        try:
                            coverage = float(part.rstrip("%"))
                            check_result["details"]["coverage_percentage"] = coverage
                            break
                        except:
                            pass

        coverage = check_result["details"]["coverage_percentage"]
        if coverage < 80:
            check_result["status"] = "WARNING"
            check_result["message"] = f"Coverage {coverage}% is below 80% threshold"
            self.print_status("Coverage Check", "WARNING", check_result["message"])
        else:
            self.print_status("Coverage Check", "PASS", f"Coverage: {coverage}%")

        self.results["checks"]["coverage"] = check_result
        return check_result

    def generate_summary(self):
        """Generate and print summary"""
        self.print_header("Validation Summary")

        # Count results
        for check_name, check_data in self.results["checks"].items():
            self.results["summary"]["total"] += 1
            if check_data["status"] == "PASS":
                self.results["summary"]["passed"] += 1
            elif check_data["status"] == "FAIL":
                self.results["summary"]["failed"] += 1
            else:
                self.results["summary"]["warnings"] += 1

        # Print summary
        total = self.results["summary"]["total"]
        passed = self.results["summary"]["passed"]
        failed = self.results["summary"]["failed"]
        warnings = self.results["summary"]["warnings"]

        print(f"Total Checks: {total}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {failed}{Colors.END}")
        print(f"{Colors.YELLOW}Warnings: {warnings}{Colors.END}")

        # Overall status
        if failed > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ VALIDATION FAILED{Colors.END}")
            print("Please address the failures before merging.")
            self.results["overall_status"] = "FAILED"
        elif warnings > 0:
            print(
                f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  VALIDATION PASSED WITH WARNINGS{Colors.END}"
            )
            print("Consider addressing warnings, but merge is acceptable.")
            self.results["overall_status"] = "PASSED_WITH_WARNINGS"
        else:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ VALIDATION PASSED{Colors.END}")
            print("PR #157 is ready to merge!")
            self.results["overall_status"] = "PASSED"

        # Save results
        results_file = self.project_root / "pr157_validation_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\nDetailed results saved to: {results_file}")

    async def run_validation(self):
        """Run all validation checks"""
        print(f"{Colors.BOLD}PR #157 Integration Validation{Colors.END}")
        print(f"Started at: {self.results['timestamp']}")

        # Run all checks
        await self.check_async_fixtures()
        await self.check_task_structure()
        await self.check_imports()
        await self.run_test_suite()
        await self.check_coverage()

        # Generate summary
        self.generate_summary()

        # Return exit code based on results
        return 0 if self.results["summary"]["failed"] == 0 else 1


async def main():
    """Main entry point"""
    validator = IntegrationValidator()
    exit_code = await validator.run_validation()
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
