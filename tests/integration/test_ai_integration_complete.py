#!/usr/bin/env python3
"""
Complete AI Integration Test - Tests all AI integrations and workflows
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config.ai_config import get_ai_config
from services.ai_service_manager import AIProvider, AIServiceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CompleteAIIntegrationTest:
    """Complete AI Integration Test Suite"""

    def __init__(self):
        self.ai_service = None
        self.config_manager = get_ai_config()
        self.test_results = {}

    async def initialize(self):
        """Initialize the test suite"""
        try:
            config = {
                "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY"),
                "glm_api_key": os.getenv("GLM_API_KEY"),
                "grok_api_key": os.getenv("GROK_API_KEY"),
                "kimi_api_key": os.getenv("KIMI_API_KEY"),
                "qwen_api_key": os.getenv("QWEN_API_KEY"),
                "gptoss_api_key": os.getenv("GPTOSS_API_KEY"),
            }

            self.ai_service = AIServiceManager(config)
            await self.ai_service.initialize()
            logger.info("Complete AI Integration Test initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing Complete AI Integration Test: {e}")
            raise

    async def test_ai_providers(self) -> Dict[str, Any]:
        """Test all AI providers"""
        try:
            logger.info("Testing AI providers...")

            provider_tests = {}
            for provider in AIProvider:
                logger.info(f"Testing {provider.value}...")

                try:
                    # Test with simple request
                    test_response = await self.ai_service.generate_response(
                        "Hello, this is a connectivity test. Respond with 'OK'.",
                        preferred_provider=provider,
                    )

                    provider_tests[provider.value] = {
                        "status": "success" if test_response.success else "failed",
                        "response_time": test_response.response_time,
                        "error": (
                            test_response.error if not test_response.success else None
                        ),
                        "provider_used": test_response.provider,
                        "content_length": (
                            len(test_response.content) if test_response.success else 0
                        ),
                    }

                    if test_response.success:
                        logger.info(f"✓ {provider.value} test successful")
                    else:
                        logger.warning(
                            f"✗ {provider.value} test failed: {test_response.error}"
                        )

                except Exception as e:
                    provider_tests[provider.value] = {
                        "status": "error",
                        "error": str(e),
                    }
                    logger.error(f"✗ {provider.value} test error: {e}")

            return {
                "provider_tests": provider_tests,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error testing AI providers: {e}")
            return {"error": str(e)}

    async def test_ai_capabilities(self) -> Dict[str, Any]:
        """Test all AI capabilities"""
        try:
            logger.info("Testing AI capabilities...")

            capabilities = {
                "code_generation": await self._test_code_generation(),
                "code_analysis": await self._test_code_analysis(),
                "code_improvement": await self._test_code_improvement(),
                "test_generation": await self._test_test_generation(),
                "documentation_generation": await self._test_documentation_generation(),
                "security_analysis": await self._test_security_analysis(),
                "performance_analysis": await self._test_performance_analysis(),
            }

            return {
                "capabilities": capabilities,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error testing AI capabilities: {e}")
            return {"error": str(e)}

    async def _test_code_generation(self) -> Dict[str, Any]:
        """Test code generation capability"""
        try:
            prompt = """Generate a simple Python function that calculates the factorial of a number.
Include proper error handling and documentation."""

            response = await self.ai_service.generate_code(prompt, "python")

            return {
                "success": response.success,
                "provider": response.provider,
                "response_time": response.response_time,
                "content_length": len(response.content) if response.success else 0,
                "error": response.error if not response.success else None,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_code_analysis(self) -> Dict[str, Any]:
        """Test code analysis capability"""
        try:
            code = """
def calculate_factorial(n):
    if n < 0:
        return None
    if n == 0:
        return 1
    return n * calculate_factorial(n-1)
"""

            response = await self.ai_service.analyze_code(code, "python")

            return {
                "success": response.success,
                "provider": response.provider,
                "response_time": response.response_time,
                "content_length": len(response.content) if response.success else 0,
                "error": response.error if not response.success else None,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_code_improvement(self) -> Dict[str, Any]:
        """Test code improvement capability"""
        try:
            code = """
def calc_fact(n):
    if n < 0:
        return None
    if n == 0:
        return 1
    return n * calc_fact(n-1)
"""

            response = await self.ai_service.improve_code(code, "python", "general")

            return {
                "success": response.success,
                "provider": response.provider,
                "response_time": response.response_time,
                "content_length": len(response.content) if response.success else 0,
                "error": response.error if not response.success else None,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_test_generation(self) -> Dict[str, Any]:
        """Test test generation capability"""
        try:
            code = """
def calculate_factorial(n):
    if n < 0:
        return None
    if n == 0:
        return 1
    return n * calculate_factorial(n-1)
"""

            response = await self.ai_service.generate_tests(code, "python")

            return {
                "success": response.success,
                "provider": response.provider,
                "response_time": response.response_time,
                "content_length": len(response.content) if response.success else 0,
                "error": response.error if not response.success else None,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_documentation_generation(self) -> Dict[str, Any]:
        """Test documentation generation capability"""
        try:
            prompt = """Generate comprehensive documentation for a Python function that calculates factorial.
Include function signature, parameters, return value, examples, and usage notes."""

            response = await self.ai_service.generate_response(prompt)

            return {
                "success": response.success,
                "provider": response.provider,
                "response_time": response.response_time,
                "content_length": len(response.content) if response.success else 0,
                "error": response.error if not response.success else None,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_security_analysis(self) -> Dict[str, Any]:
        """Test security analysis capability"""
        try:
            code = """
import os
import subprocess

def execute_command(user_input):
    command = f"ls {user_input}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout
"""

            prompt = f"""Analyze this Python code for security vulnerabilities:
1. Security score (1-10)
2. Vulnerabilities found
3. Security recommendations

Code:
```python
{code}
```"""

            response = await self.ai_service.generate_response(prompt)

            return {
                "success": response.success,
                "provider": response.provider,
                "response_time": response.response_time,
                "content_length": len(response.content) if response.success else 0,
                "error": response.error if not response.success else None,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_performance_analysis(self) -> Dict[str, Any]:
        """Test performance analysis capability"""
        try:
            code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""

            prompt = f"""Analyze this Python code for performance issues:
1. Performance score (1-10)
2. Performance bottlenecks
3. Optimization recommendations

Code:
```python
{code}
```"""

            response = await self.ai_service.generate_response(prompt)

            return {
                "success": response.success,
                "provider": response.provider,
                "response_time": response.response_time,
                "content_length": len(response.content) if response.success else 0,
                "error": response.error if not response.success else None,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def test_ai_scripts(self) -> Dict[str, Any]:
        """Test all AI scripts"""
        try:
            logger.info("Testing AI scripts...")

            scripts = [
                "ai_code_analyzer.py",
                "ai_code_improver.py",
                "ai_test_generator.py",
                "ai_documentation_generator.py",
                "ai_security_auditor.py",
                "ai_performance_analyzer.py",
                "ai_continuous_developer.py",
                "setup_ai_integration.py",
                "complete_ai_integration.py",
            ]

            script_tests = {}
            for script in scripts:
                script_path = Path(f"scripts/{script}")
                if script_path.exists():
                    try:
                        # Test script help
                        result = subprocess.run(
                            [sys.executable, str(script_path), "--help"],
                            capture_output=True,
                            text=True,
                            timeout=30,
                        )

                        script_tests[script] = {
                            "exists": True,
                            "help_works": result.returncode == 0,
                            "error": result.stderr if result.returncode != 0 else None,
                        }

                        if result.returncode == 0:
                            logger.info(f"✓ {script} help works")
                        else:
                            logger.warning(f"✗ {script} help failed: {result.stderr}")

                    except subprocess.TimeoutExpired:
                        script_tests[script] = {
                            "exists": True,
                            "help_works": False,
                            "error": "Timeout",
                        }
                        logger.warning(f"✗ {script} timed out")

                    except Exception as e:
                        script_tests[script] = {
                            "exists": True,
                            "help_works": False,
                            "error": str(e),
                        }
                        logger.error(f"✗ {script} error: {e}")
                else:
                    script_tests[script] = {
                        "exists": False,
                        "help_works": False,
                        "error": "File not found",
                    }
                    logger.error(f"✗ {script} not found")

            return {
                "script_tests": script_tests,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error testing AI scripts: {e}")
            return {"error": str(e)}

    def test_github_actions_workflow(self) -> Dict[str, Any]:
        """Test GitHub Actions workflow"""
        try:
            logger.info("Testing GitHub Actions workflow...")

            workflow_file = Path(".github/workflows/ai_development.yml")
            if not workflow_file.exists():
                return {"workflow_exists": False, "error": "Workflow file not found"}

            # Read workflow content
            with open(workflow_file, "r", encoding="utf-8") as f:
                workflow_content = f.read()

            # Check for required components
            required_components = [
                "ai_code_analysis",
                "ai_code_improvement",
                "ai_test_generation",
                "ai_documentation",
                "ai_security_audit",
                "ai_performance_optimization",
                "continuous_ai_development",
            ]

            component_tests = {}
            for component in required_components:
                component_tests[component] = component in workflow_content

            return {
                "workflow_exists": True,
                "component_tests": component_tests,
                "workflow_size": len(workflow_content),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error testing GitHub Actions workflow: {e}")
            return {"error": str(e)}

    def test_environment_setup(self) -> Dict[str, Any]:
        """Test environment setup"""
        try:
            logger.info("Testing environment setup...")

            # Check environment variables
            required_env_vars = [
                "DEEPSEEK_API_KEY",
                "GLM_API_KEY",
                "GROK_API_KEY",
                "KIMI_API_KEY",
                "QWEN_API_KEY",
                "GPTOSS_API_KEY",
            ]

            env_var_tests = {}
            for var in required_env_vars:
                value = os.getenv(var)
                env_var_tests[var] = {
                    "set": value is not None,
                    "length": len(value) if value else 0,
                    "starts_with_sk": value.startswith("sk-") if value else False,
                }

            # Check Python version
            python_version = sys.version_info
            python_compatible = python_version.major == 3 and python_version.minor >= 8

            # Check required files
            required_files = [
                "services/ai_service_manager.py",
                "config/ai_config.py",
                "scripts/setup_ai_integration.py",
                "scripts/complete_ai_integration.py",
                "AI_INTEGRATION_README.md",
            ]

            file_tests = {}
            for file_path in required_files:
                file_exists = Path(file_path).exists()
                file_tests[file_path] = file_exists

            return {
                "env_var_tests": env_var_tests,
                "python_compatible": python_compatible,
                "python_version": f"{python_version.major}.{python_version.minor}.{python_version.micro}",
                "file_tests": file_tests,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error testing environment setup: {e}")
            return {"error": str(e)}

    async def run_complete_test(self) -> Dict[str, Any]:
        """Run complete AI integration test"""
        try:
            logger.info("Running complete AI integration test...")

            # Test AI providers
            provider_tests = await self.test_ai_providers()

            # Test AI capabilities
            capability_tests = await self.test_ai_capabilities()

            # Test AI scripts
            script_tests = self.test_ai_scripts()

            # Test GitHub Actions workflow
            workflow_tests = self.test_github_actions_workflow()

            # Test environment setup
            environment_tests = self.test_environment_setup()

            # Generate comprehensive test report
            test_report = {
                "timestamp": datetime.now().isoformat(),
                "provider_tests": provider_tests,
                "capability_tests": capability_tests,
                "script_tests": script_tests,
                "workflow_tests": workflow_tests,
                "environment_tests": environment_tests,
                "summary": self._generate_test_summary(
                    provider_tests,
                    capability_tests,
                    script_tests,
                    workflow_tests,
                    environment_tests,
                ),
            }

            return test_report

        except Exception as e:
            logger.error(f"Error in complete test: {e}")
            return {"error": str(e)}

    def _generate_test_summary(
        self,
        provider_tests: Dict[str, Any],
        capability_tests: Dict[str, Any],
        script_tests: Dict[str, Any],
        workflow_tests: Dict[str, Any],
        environment_tests: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate test summary"""
        try:
            # Count successful providers
            provider_results = provider_tests.get("provider_tests", {})
            successful_providers = len(
                [p for p in provider_results.values() if p.get("status") == "success"]
            )

            # Count successful capabilities
            capability_results = capability_tests.get("capabilities", {})
            successful_capabilities = len(
                [c for c in capability_results.values() if c.get("success", False)]
            )

            # Count working scripts
            script_results = script_tests.get("script_tests", {})
            working_scripts = len(
                [s for s in script_results.values() if s.get("help_works", False)]
            )

            # Check workflow components
            workflow_components = workflow_tests.get("component_tests", {})
            working_components = len([c for c in workflow_components.values() if c])

            # Check environment variables
            env_results = environment_tests.get("env_var_tests", {})
            set_env_vars = len([e for e in env_results.values() if e.get("set", False)])

            return {
                "total_providers": len(provider_results),
                "successful_providers": successful_providers,
                "total_capabilities": len(capability_results),
                "successful_capabilities": successful_capabilities,
                "total_scripts": len(script_results),
                "working_scripts": working_scripts,
                "total_workflow_components": len(workflow_components),
                "working_workflow_components": working_components,
                "total_env_vars": len(env_results),
                "set_env_vars": set_env_vars,
                "python_compatible": environment_tests.get("python_compatible", False),
                "overall_status": (
                    "complete"
                    if successful_providers > 0 and successful_capabilities > 0
                    else "incomplete"
                ),
                "recommendations": self._generate_test_recommendations(
                    successful_providers,
                    successful_capabilities,
                    working_scripts,
                    working_components,
                    set_env_vars,
                ),
            }

        except Exception as e:
            logger.error(f"Error generating test summary: {e}")
            return {"error": str(e)}

    def _generate_test_recommendations(
        self,
        successful_providers: int,
        successful_capabilities: int,
        working_scripts: int,
        working_components: int,
        set_env_vars: int,
    ) -> List[str]:
        """Generate test recommendations"""
        recommendations = []

        if successful_providers == 0:
            recommendations.append(
                "No AI providers are working. Check API keys and network connectivity."
            )
        elif successful_providers < 6:
            recommendations.append(
                f"Only {successful_providers} AI providers are working. Consider adding more API keys."
            )

        if successful_capabilities < 7:
            recommendations.append(
                f"Only {successful_capabilities} AI capabilities are working. Check provider configurations."
            )

        if working_scripts < 9:
            recommendations.append(
                f"Only {working_scripts} AI scripts are working. Check script implementations."
            )

        if working_components < 7:
            recommendations.append(
                f"Only {working_components} workflow components are working. Check GitHub Actions workflow."
            )

        if set_env_vars < 6:
            recommendations.append(
                f"Only {set_env_vars} environment variables are set. Set all required API keys."
            )

        if (
            successful_providers > 0
            and successful_capabilities > 0
            and working_scripts > 0
        ):
            recommendations.append(
                "AI integration is working well! Consider running performance tests."
            )
            recommendations.append(
                "Monitor AI provider health and performance regularly."
            )

        return recommendations

    def save_test_report(self, report: Dict[str, Any], output_file: str):
        """Save test report to file"""
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Test report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving test report: {e}")

    async def shutdown(self):
        """Shutdown the test suite"""
        if self.ai_service:
            await self.ai_service.shutdown()


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Complete AI Integration Test")
    parser.add_argument(
        "--output",
        default="complete_ai_integration_test_report.json",
        help="Output file for test report",
    )
    parser.add_argument(
        "--providers-only", action="store_true", help="Only test AI providers"
    )
    parser.add_argument(
        "--capabilities-only", action="store_true", help="Only test AI capabilities"
    )
    parser.add_argument(
        "--scripts-only", action="store_true", help="Only test AI scripts"
    )
    parser.add_argument(
        "--workflow-only", action="store_true", help="Only test GitHub Actions workflow"
    )
    parser.add_argument(
        "--environment-only", action="store_true", help="Only test environment setup"
    )

    args = parser.parse_args()

    test_suite = CompleteAIIntegrationTest()

    try:
        await test_suite.initialize()

        if args.providers_only:
            # Only test AI providers
            results = await test_suite.test_ai_providers()
            print("\n" + "=" * 50)
            print("AI PROVIDER TEST RESULTS")
            print("=" * 50)
            for provider, test in results.get("provider_tests", {}).items():
                status = "✓" if test.get("status") == "success" else "✗"
                print(f"{status} {provider}: {test.get('status', 'unknown')}")
            print("=" * 50)

        elif args.capabilities_only:
            # Only test AI capabilities
            results = await test_suite.test_ai_capabilities()
            print("\n" + "=" * 50)
            print("AI CAPABILITY TEST RESULTS")
            print("=" * 50)
            for capability, test in results.get("capabilities", {}).items():
                status = "✓" if test.get("success") else "✗"
                print(f"{status} {capability}: {test.get('success', False)}")
            print("=" * 50)

        elif args.scripts_only:
            # Only test AI scripts
            results = test_suite.test_ai_scripts()
            print("\n" + "=" * 50)
            print("AI SCRIPT TEST RESULTS")
            print("=" * 50)
            for script, test in results.get("script_tests", {}).items():
                status = "✓" if test.get("help_works") else "✗"
                print(f"{status} {script}: {test.get('help_works', False)}")
            print("=" * 50)

        elif args.workflow_only:
            # Only test GitHub Actions workflow
            results = test_suite.test_github_actions_workflow()
            print("\n" + "=" * 50)
            print("GITHUB ACTIONS WORKFLOW TEST RESULTS")
            print("=" * 50)
            print(f"Workflow exists: {results.get('workflow_exists', False)}")
            for component, working in results.get("component_tests", {}).items():
                status = "✓" if working else "✗"
                print(f"{status} {component}: {working}")
            print("=" * 50)

        elif args.environment_only:
            # Only test environment setup
            results = test_suite.test_environment_setup()
            print("\n" + "=" * 50)
            print("ENVIRONMENT SETUP TEST RESULTS")
            print("=" * 50)
            print(f"Python compatible: {results.get('python_compatible', False)}")
            print(f"Python version: {results.get('python_version', 'unknown')}")
            for var, test in results.get("env_var_tests", {}).items():
                status = "✓" if test.get("set") else "✗"
                print(f"{status} {var}: {test.get('set', False)}")
            print("=" * 50)

        else:
            # Complete test
            results = await test_suite.run_complete_test()
            test_suite.save_test_report(results, args.output)

            # Print summary
            if "summary" in results:
                summary = results["summary"]
                print("\n" + "=" * 50)
                print("COMPLETE AI INTEGRATION TEST SUMMARY")
                print("=" * 50)
                print(f"Total Providers: {summary.get('total_providers', 0)}")
                print(f"Successful Providers: {summary.get('successful_providers', 0)}")
                print(f"Total Capabilities: {summary.get('total_capabilities', 0)}")
                print(
                    f"Successful Capabilities: {summary.get('successful_capabilities', 0)}"
                )
                print(f"Total Scripts: {summary.get('total_scripts', 0)}")
                print(f"Working Scripts: {summary.get('working_scripts', 0)}")
                print(
                    f"Total Workflow Components: {summary.get('total_workflow_components', 0)}"
                )
                print(
                    f"Working Workflow Components: {summary.get('working_workflow_components', 0)}"
                )
                print(
                    f"Total Environment Variables: {summary.get('total_env_vars', 0)}"
                )
                print(f"Set Environment Variables: {summary.get('set_env_vars', 0)}")
                print(f"Python Compatible: {summary.get('python_compatible', False)}")
                print(f"Overall Status: {summary.get('overall_status', 'unknown')}")
                print("\nRecommendations:")
                for rec in summary.get("recommendations", []):
                    print(f"- {rec}")
                print("=" * 50)

            logger.info("Complete AI integration test finished.")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

    finally:
        await test_suite.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
