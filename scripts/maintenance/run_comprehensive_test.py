#!/usr/bin/env python3
"""
Comprehensive AI System Test Runner
Tests all components of the AMAS AI Workflow System
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path



class AISystemTester:
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {},
        }

    def log_test(self, test_name, status, details=""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }
        self.test_results["tests"].append(result)

        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")

    def test_system_structure(self):
        """Test 1: System Structure Verification"""
        print("\n🧪 Test 1: System Structure Verification")
        print("=" * 50)

        # Check workflow files
        workflow_dir = Path(".github/workflows")
        if workflow_dir.exists():
            workflow_files = list(workflow_dir.glob("*.yml"))
            if len(workflow_files) >= 12:
                self.log_test(
                    "Workflow Files",
                    "PASS",
                    f"Found {len(workflow_files)} workflow files",
                )
            else:
                self.log_test(
                    "Workflow Files",
                    "FAIL",
                    f"Expected 12+, found {len(workflow_files)}",
                )
        else:
            self.log_test("Workflow Files", "FAIL", "Workflow directory not found")

        # Check AI scripts
        scripts_dir = Path(".github/scripts")
        if scripts_dir.exists():
            script_files = list(scripts_dir.glob("*.py"))
            if len(script_files) >= 12:
                self.log_test(
                    "AI Scripts", "PASS", f"Found {len(script_files)} AI script files"
                )
            else:
                self.log_test(
                    "AI Scripts", "FAIL", f"Expected 12+, found {len(script_files)}"
                )
        else:
            self.log_test("AI Scripts", "FAIL", "Scripts directory not found")

        # Check key files
        key_files = [
            ".github/workflows/ai-enhanced-workflow.yml",
            ".github/workflows/test-ai-workflow.yml",
            ".github/scripts/ai_code_analyzer.py",
            ".github/scripts/ai_security_scanner.py",
            ".github/scripts/multi_agent_orchestrator.py",
        ]

        for file_path in key_files:
            if Path(file_path).exists():
                self.log_test(f"Key File: {file_path}", "PASS")
            else:
                self.log_test(f"Key File: {file_path}", "FAIL", "File not found")

    def test_python_environment(self):
        """Test 2: Python Environment"""
        print("\n🐍 Test 2: Python Environment")
        print("=" * 50)

        # Test Python version
        try:
            result = subprocess.run(
                [sys.executable, "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log_test("Python Version", "PASS", version)
            else:
                self.log_test("Python Version", "FAIL", "Cannot determine version")
        except Exception as e:
            self.log_test("Python Version", "FAIL", str(e))

        # Test required modules
        required_modules = ["json", "os", "sys", "pathlib", "datetime"]
        for module in required_modules:
            try:
                __import__(module)
                self.log_test(f"Module: {module}", "PASS")
            except ImportError:
                self.log_test(f"Module: {module}", "FAIL", "Module not available")

    def test_workflow_syntax(self):
        """Test 3: Workflow YAML Syntax"""
        print("\n📄 Test 3: Workflow YAML Syntax")
        print("=" * 50)

        workflow_dir = Path(".github/workflows")
        if workflow_dir.exists():
            for yml_file in workflow_dir.glob("*.yml"):
                try:
                    # Basic YAML syntax check
                    with open(yml_file, "r") as f:
                        content = f.read()

                    # Check for basic YAML structure
                    if "name:" in content and "on:" in content and "jobs:" in content:
                        self.log_test(f"YAML Syntax: {yml_file.name}", "PASS")
                    else:
                        self.log_test(
                            f"YAML Syntax: {yml_file.name}",
                            "FAIL",
                            "Missing required sections",
                        )

                except Exception as e:
                    self.log_test(f"YAML Syntax: {yml_file.name}", "FAIL", str(e))

    def test_ai_script_syntax(self):
        """Test 4: AI Script Python Syntax"""
        print("\n🐍 Test 4: AI Script Python Syntax")
        print("=" * 50)

        scripts_dir = Path(".github/scripts")
        if scripts_dir.exists():
            for py_file in scripts_dir.glob("*.py"):
                try:
                    # Compile Python file to check syntax
                    with open(py_file, "r") as f:
                        compile(f.read(), str(py_file), "exec")
                    self.log_test(f"Python Syntax: {py_file.name}", "PASS")
                except SyntaxError as e:
                    self.log_test(
                        f"Python Syntax: {py_file.name}", "FAIL", f"Syntax error: {e}"
                    )
                except Exception as e:
                    self.log_test(f"Python Syntax: {py_file.name}", "FAIL", str(e))

    def test_api_key_configuration(self):
        """Test 5: API Key Configuration"""
        print("\n🔑 Test 5: API Key Configuration")
        print("=" * 50)

        api_keys = {
            "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
            "GLM_API_KEY": os.getenv("GLM_API_KEY"),
            "GROK_API_KEY": os.getenv("GROK_API_KEY"),
            "KIMI_API_KEY": os.getenv("KIMI_API_KEY"),
            "QWEN_API_KEY": os.getenv("QWEN_API_KEY"),
            "GPTOSS_API_KEY": os.getenv("GPTOSS_API_KEY"),
        }

        configured_keys = 0
        for key_name, key_value in api_keys.items():
            if key_value:
                configured_keys += 1
                # Validate key format
                if key_name == "DEEPSEEK_API_KEY" and key_value.startswith("sk-"):
                    self.log_test(f"API Key: {key_name}", "PASS", "Valid format")
                elif key_name in [
                    "GLM_API_KEY",
                    "GROK_API_KEY",
                    "KIMI_API_KEY",
                    "QWEN_API_KEY",
                    "GPTOSS_API_KEY",
                ] and key_value.startswith("sk-or-v1-"):
                    self.log_test(f"API Key: {key_name}", "PASS", "Valid format")
                else:
                    self.log_test(
                        f"API Key: {key_name}", "WARN", "Configured but format unclear"
                    )
            else:
                self.log_test(f"API Key: {key_name}", "FAIL", "Not configured")

        self.log_test("API Key Summary", "INFO", f"{configured_keys}/6 keys configured")

    def test_workflow_configuration(self):
        """Test 6: Workflow Configuration"""
        print("\n⚙️ Test 6: Workflow Configuration")
        print("=" * 50)

        # Check key workflow files for proper configuration
        key_workflows = [
            ".github/workflows/ai-enhanced-workflow.yml",
            ".github/workflows/test-ai-workflow.yml",
        ]

        for workflow_file in key_workflows:
            if Path(workflow_file).exists():
                try:
                    with open(workflow_file, "r") as f:
                        content = f.read()

                    # Check for required elements
                    checks = [
                        ("workflow_dispatch", "Manual trigger"),
                        ("python-version", "Python version specified"),
                        ("DEEPSEEK_API_KEY", "DeepSeek API key"),
                        ("GLM_API_KEY", "GLM API key"),
                        ("GROK_API_KEY", "Grok API key"),
                    ]

                    for check, description in checks:
                        if check in content:
                            self.log_test(f"{workflow_file}: {description}", "PASS")
                        else:
                            self.log_test(
                                f"{workflow_file}: {description}",
                                "FAIL",
                                f"Missing {check}",
                            )

                except Exception as e:
                    self.log_test(f"Workflow Config: {workflow_file}", "FAIL", str(e))
            else:
                self.log_test(
                    f"Workflow Config: {workflow_file}", "FAIL", "File not found"
                )

    def test_ai_script_functionality(self):
        """Test 7: AI Script Functionality"""
        print("\n🤖 Test 7: AI Script Functionality")
        print("=" * 50)

        # Test key AI scripts for basic functionality
        key_scripts = [
            ".github/scripts/ai_code_analyzer.py",
            ".github/scripts/ai_security_scanner.py",
            ".github/scripts/multi_agent_orchestrator.py",
        ]

        for script_file in key_scripts:
            if Path(script_file).exists():
                try:
                    with open(script_file, "r") as f:
                        content = f.read()

                    # Check for required classes and methods
                    if "class" in content and "def __init__" in content:
                        self.log_test(
                            f"Script Structure: {script_file}",
                            "PASS",
                            "Has class and init method",
                        )
                    else:
                        self.log_test(
                            f"Script Structure: {script_file}",
                            "FAIL",
                            "Missing class or init method",
                        )

                    # Check for AI client initialization
                    if "OpenAI" in content and "api_key" in content:
                        self.log_test(
                            f"AI Integration: {script_file}",
                            "PASS",
                            "Has OpenAI integration",
                        )
                    else:
                        self.log_test(
                            f"AI Integration: {script_file}",
                            "FAIL",
                            "Missing OpenAI integration",
                        )

                except Exception as e:
                    self.log_test(
                        f"Script Functionality: {script_file}", "FAIL", str(e)
                    )
            else:
                self.log_test(
                    f"Script Functionality: {script_file}", "FAIL", "File not found"
                )

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📋 Generating Test Report...")
        print("=" * 50)

        # Calculate summary
        total_tests = len(self.test_results["tests"])
        passed_tests = sum(
            1 for test in self.test_results["tests"] if test["status"] == "PASS"
        )
        failed_tests = sum(
            1 for test in self.test_results["tests"] if test["status"] == "FAIL"
        )
        warning_tests = sum(
            1 for test in self.test_results["tests"] if test["status"] == "WARN"
        )

        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "warnings": warning_tests,
            "success_rate": (
                (passed_tests / total_tests * 100) if total_tests > 0 else 0
            ),
        }

        # Generate report
        report = f"""# 🧪 AI System Test Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Tests:** {total_tests}
**Passed:** {passed_tests}
**Failed:** {failed_tests}
**Warnings:** {warning_tests}
**Success Rate:** {self.test_results['summary']['success_rate']:.1f}%

## Test Results

"""

        for test in self.test_results["tests"]:
            status_emoji = (
                "✅"
                if test["status"] == "PASS"
                else "❌" if test["status"] == "FAIL" else "⚠️"
            )
            report += f"- {status_emoji} **{test['test']}**: {test['status']}\n"
            if test["details"]:
                report += f"  - Details: {test['details']}\n"

        report += f"""
## Summary

### System Status
- **Overall Result**: {'✅ PASS' if failed_tests == 0 else '❌ FAIL'}
- **Success Rate**: {self.test_results['summary']['success_rate']:.1f}%
- **Critical Issues**: {failed_tests}
- **Warnings**: {warning_tests}

### Recommendations

"""

        if failed_tests > 0:
            report += """
1. **Fix Critical Issues**: Address all failed tests
2. **Configure API Keys**: Add missing API keys to GitHub Secrets
3. **Verify Dependencies**: Ensure all required modules are available
4. **Test Workflows**: Run manual workflow dispatch tests
"""
        else:
            report += """
1. **Configure API Keys**: Add 6 API keys to GitHub Secrets
2. **Test Workflows**: Run manual workflow dispatch
3. **Monitor Performance**: Check workflow execution
4. **Verify Integration**: Test cross-workflow functionality
"""

        report += """
## Next Steps

1. **Configure API Keys**: Add all 6 API keys to GitHub Secrets
2. **Test Workflows**: Use manual dispatch to test workflows
3. **Monitor Execution**: Check for skipped jobs and errors
4. **Verify Results**: Check generated reports and artifacts

---
*Report generated by AI System Tester*
"""

        # Save report
        with open("ai_system_test_report.md", "w") as f:
            f.write(report)

        # Save JSON results
        with open("ai_system_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)

        print(f"✅ Test report saved to: ai_system_test_report.md")
        print(f"✅ Test results saved to: ai_system_test_results.json")

        return self.test_results["summary"]

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive AI System Test...")
        print("=" * 60)

        # Run all test phases
        self.test_system_structure()
        self.test_python_environment()
        self.test_workflow_syntax()
        self.test_ai_script_syntax()
        self.test_api_key_configuration()
        self.test_workflow_configuration()
        self.test_ai_script_functionality()

        # Generate report
        summary = self.generate_test_report()

        # Final summary
        print(f"\n📊 Test Summary")
        print("=" * 50)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Warnings: {summary['warnings']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")

        if summary["failed"] == 0:
            print("\n🎉 All tests passed! System is ready for configuration.")
        else:
            print(
                f"\n⚠️ {summary['failed']} tests failed. Please address the issues above."
            )

        return summary["failed"] == 0


def main():
    """Main test runner"""
    tester = AISystemTester()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
