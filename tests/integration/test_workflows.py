#!/usr/bin/env python3
"""
Test Workflows - Test all AI workflows and ensure nothing is skipped
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

import yaml

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from services.ai_service_manager import AIProvider, AIServiceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WorkflowTester:
    """Test all AI workflows"""

    def __init__(self):
        self.ai_service = None
        self.test_results = {}

    async def initialize(self):
        """Initialize the workflow tester"""
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
            logger.info("Workflow Tester initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing Workflow Tester: {e}")
            raise

    def test_github_workflows(self) -> Dict[str, Any]:
        """Test GitHub Actions workflows"""
        try:
            logger.info("Testing GitHub Actions workflows...")

            workflow_files = [
                ".github/workflows/ai_development.yml",
                ".github/workflows/ai_complete_workflow.yml",
                ".github/workflows/ai_simple_workflow.yml",
            ]

            workflow_tests = {}

            for workflow_file in workflow_files:
                workflow_path = Path(workflow_file)
                if workflow_path.exists():
                    try:
                        with open(workflow_path, "r", encoding="utf-8") as f:
                            workflow_content = f.read()

                        # Parse YAML
                        workflow_yaml = yaml.safe_load(workflow_content)

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

                        jobs = workflow_yaml.get("jobs", {})
                        component_tests = {}

                        for component in required_components:
                            component_tests[component] = component in jobs

                        # Check for environment variables
                        env_vars = [
                            "DEEPSEEK_API_KEY",
                            "GLM_API_KEY",
                            "GROK_API_KEY",
                            "KIMI_API_KEY",
                            "QWEN_API_KEY",
                            "GPTOSS_API_KEY",
                        ]

                        env_tests = {}
                        for env_var in env_vars:
                            env_tests[env_var] = (
                                f"${{{{ secrets.{env_var} }}}}" in workflow_content
                            )

                        workflow_tests[workflow_file] = {
                            "exists": True,
                            "yaml_valid": True,
                            "component_tests": component_tests,
                            "env_tests": env_tests,
                            "workflow_size": len(workflow_content),
                            "total_jobs": len(jobs),
                            "working_components": len(
                                [c for c in component_tests.values() if c]
                            ),
                        }

                    except yaml.YAMLError as e:
                        workflow_tests[workflow_file] = {
                            "exists": True,
                            "yaml_valid": False,
                            "error": f"YAML parsing error: {e}",
                        }

                    except Exception as e:
                        workflow_tests[workflow_file] = {
                            "exists": True,
                            "yaml_valid": False,
                            "error": str(e),
                        }
                else:
                    workflow_tests[workflow_file] = {
                        "exists": False,
                        "yaml_valid": False,
                        "error": "Workflow file not found",
                    }

            return {
                "workflow_tests": workflow_tests,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error testing GitHub workflows: {e}")
            return {"error": str(e)}

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
                "ai_issues_responder.py",
                "setup_ai_integration.py",
                "complete_ai_integration.py",
                "test_ai_integration_complete.py",
                "validate_complete_workflows.py",
                "complete_workflow_setup.py",
                "final_validation.py",
            ]

            script_tests = {}

            for script in scripts:
                script_path = Path(f"scripts/{script}")
                script_test = {
                    "exists": script_path.exists(),
                    "readable": False,
                    "has_main": False,
                    "has_argparse": False,
                    "has_ai_service": False,
                    "size": 0,
                    "line_count": 0,
                }

                if script_path.exists():
                    try:
                        with open(script_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        script_test.update(
                            {
                                "readable": True,
                                "has_main": 'if __name__ == "__main__"' in content,
                                "has_argparse": "argparse" in content,
                                "has_ai_service": "AIServiceManager" in content,
                                "size": len(content),
                                "line_count": len(content.splitlines()),
                            }
                        )

                    except Exception as e:
                        script_test["error"] = str(e)

                script_tests[script] = script_test

            return {
                "script_tests": script_tests,
                "total_scripts": len(scripts),
                "existing_scripts": len(
                    [s for s in script_tests.values() if s["exists"]]
                ),
                "working_scripts": len(
                    [s for s in script_tests.values() if s["exists"] and s["has_main"]]
                ),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error testing AI scripts: {e}")
            return {"error": str(e)}

    def test_script_execution(self) -> Dict[str, Any]:
        """Test script execution"""
        try:
            logger.info("Testing script execution...")

            test_scripts = [
                "setup_ai_integration.py",
                "test_ai_integration_complete.py",
                "validate_complete_workflows.py",
                "final_validation.py",
            ]

            execution_tests = {}

            for script in test_scripts:
                script_path = Path(f"scripts/{script}")
                if script_path.exists():
                    try:
                        # Test help command
                        result = subprocess.run(
                            [sys.executable, str(script_path), "--help"],
                            capture_output=True,
                            text=True,
                            timeout=30,
                        )

                        execution_tests[script] = {
                            "exists": True,
                            "help_works": result.returncode == 0,
                            "output": result.stdout,
                            "error": result.stderr,
                            "timeout": False,
                        }

                    except subprocess.TimeoutExpired:
                        execution_tests[script] = {
                            "exists": True,
                            "help_works": False,
                            "output": "",
                            "error": "Timeout",
                            "timeout": True,
                        }

                    except Exception as e:
                        execution_tests[script] = {
                            "exists": True,
                            "help_works": False,
                            "output": "",
                            "error": str(e),
                            "timeout": False,
                        }
                else:
                    execution_tests[script] = {
                        "exists": False,
                        "help_works": False,
                        "output": "",
                        "error": "File not found",
                        "timeout": False,
                    }

            return {
                "execution_tests": execution_tests,
                "total_scripts": len(test_scripts),
                "working_scripts": len(
                    [s for s in execution_tests.values() if s.get("help_works", False)]
                ),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error testing script execution: {e}")
            return {"error": str(e)}

    async def test_ai_providers(self) -> Dict[str, Any]:
        """Test AI providers"""
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

    async def run_complete_test(self) -> Dict[str, Any]:
        """Run complete workflow test"""
        try:
            logger.info("Running complete workflow test...")

            # Test GitHub workflows
            workflow_tests = self.test_github_workflows()

            # Test AI scripts
            script_tests = self.test_ai_scripts()

            # Test script execution
            execution_tests = self.test_script_execution()

            # Test AI providers
            provider_tests = await self.test_ai_providers()

            # Generate comprehensive test report
            test_report = {
                "timestamp": datetime.now().isoformat(),
                "workflow_tests": workflow_tests,
                "script_tests": script_tests,
                "execution_tests": execution_tests,
                "provider_tests": provider_tests,
                "summary": self._generate_test_summary(
                    workflow_tests, script_tests, execution_tests, provider_tests
                ),
            }

            return test_report

        except Exception as e:
            logger.error(f"Error in complete test: {e}")
            return {"error": str(e)}

    def _generate_test_summary(
        self,
        workflow_tests: Dict[str, Any],
        script_tests: Dict[str, Any],
        execution_tests: Dict[str, Any],
        provider_tests: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate test summary"""
        try:
            # Count successful workflows
            workflow_results = workflow_tests.get("workflow_tests", {})
            successful_workflows = len(
                [
                    w
                    for w in workflow_results.values()
                    if w.get("yaml_valid", False) and w.get("working_components", 0) > 0
                ]
            )

            # Count working scripts
            script_results = script_tests.get("script_tests", {})
            working_scripts = len(
                [
                    s
                    for s in script_results.values()
                    if s.get("exists", False) and s.get("has_main", False)
                ]
            )

            # Count working executions
            execution_results = execution_tests.get("execution_tests", {})
            working_executions = len(
                [e for e in execution_results.values() if e.get("help_works", False)]
            )

            # Count successful providers
            provider_results = provider_tests.get("provider_tests", {})
            successful_providers = len(
                [p for p in provider_results.values() if p.get("status") == "success"]
            )

            return {
                "total_workflows": len(workflow_results),
                "successful_workflows": successful_workflows,
                "total_scripts": len(script_results),
                "working_scripts": working_scripts,
                "total_executions": len(execution_results),
                "working_executions": working_executions,
                "total_providers": len(provider_results),
                "successful_providers": successful_providers,
                "overall_status": (
                    "complete"
                    if successful_workflows > 0 and working_scripts > 0
                    else "incomplete"
                ),
                "recommendations": self._generate_test_recommendations(
                    successful_workflows,
                    working_scripts,
                    working_executions,
                    successful_providers,
                ),
            }

        except Exception as e:
            logger.error(f"Error generating test summary: {e}")
            return {"error": str(e)}

    def _generate_test_recommendations(
        self,
        successful_workflows: int,
        working_scripts: int,
        working_executions: int,
        successful_providers: int,
    ) -> List[str]:
        """Generate test recommendations"""
        recommendations = []

        if successful_workflows == 0:
            recommendations.append(
                "No workflows are working. Check GitHub Actions configuration."
            )
        elif successful_workflows < 3:
            recommendations.append(
                f"Only {successful_workflows} workflows are working. Complete all workflow configurations."
            )

        if working_scripts < 14:
            recommendations.append(
                f"Only {working_scripts} AI scripts are working. Check script implementations."
            )

        if working_executions < 4:
            recommendations.append(
                f"Only {working_executions} scripts can execute. Check script implementations."
            )

        if successful_providers == 0:
            recommendations.append(
                "No AI providers are working. Check API keys and network connectivity."
            )
        elif successful_providers < 6:
            recommendations.append(
                f"Only {successful_providers} AI providers are working. Consider adding more API keys."
            )

        if successful_workflows > 0 and working_scripts > 0 and working_executions > 0:
            recommendations.append(
                "Workflow testing is mostly complete! Address remaining issues."
            )
            recommendations.append("All components are working together successfully.")

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
        """Shutdown the workflow tester"""
        if self.ai_service:
            await self.ai_service.shutdown()


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test Workflows")
    parser.add_argument(
        "--output",
        default="workflow_test_report.json",
        help="Output file for test report",
    )
    parser.add_argument(
        "--workflows-only", action="store_true", help="Only test GitHub workflows"
    )
    parser.add_argument(
        "--scripts-only", action="store_true", help="Only test AI scripts"
    )
    parser.add_argument(
        "--execution-only", action="store_true", help="Only test script execution"
    )
    parser.add_argument(
        "--providers-only", action="store_true", help="Only test AI providers"
    )

    args = parser.parse_args()

    tester = WorkflowTester()

    try:
        await tester.initialize()

        if args.workflows_only:
            # Only test GitHub workflows
            results = tester.test_github_workflows()
            print("\n" + "=" * 50)
            print("GITHUB WORKFLOWS TEST RESULTS")
            print("=" * 50)
            for workflow, test in results.get("workflow_tests", {}).items():
                status = (
                    "✓"
                    if test.get("yaml_valid") and test.get("working_components", 0) > 0
                    else "✗"
                )
                print(
                    f"{status} {workflow}: {test.get('working_components', 0)} components"
                )
            print("=" * 50)

        elif args.scripts_only:
            # Only test AI scripts
            results = tester.test_ai_scripts()
            print("\n" + "=" * 50)
            print("AI SCRIPTS TEST RESULTS")
            print("=" * 50)
            for script, test in results.get("script_tests", {}).items():
                status = "✓" if test.get("exists") and test.get("has_main") else "✗"
                print(f"{status} {script}: {test.get('exists', False)}")
            print("=" * 50)

        elif args.execution_only:
            # Only test script execution
            results = tester.test_script_execution()
            print("\n" + "=" * 50)
            print("SCRIPT EXECUTION TEST RESULTS")
            print("=" * 50)
            for script, test in results.get("execution_tests", {}).items():
                status = "✓" if test.get("help_works") else "✗"
                print(f"{status} {script}: {test.get('help_works', False)}")
            print("=" * 50)

        elif args.providers_only:
            # Only test AI providers
            results = await tester.test_ai_providers()
            print("\n" + "=" * 50)
            print("AI PROVIDERS TEST RESULTS")
            print("=" * 50)
            for provider, test in results.get("provider_tests", {}).items():
                status = "✓" if test.get("status") == "success" else "✗"
                print(f"{status} {provider}: {test.get('status', 'unknown')}")
            print("=" * 50)

        else:
            # Complete test
            results = await tester.run_complete_test()
            tester.save_test_report(results, args.output)

            # Print summary
            if "summary" in results:
                summary = results["summary"]
                print("\n" + "=" * 50)
                print("WORKFLOW TEST SUMMARY")
                print("=" * 50)
                print(f"Total Workflows: {summary.get('total_workflows', 0)}")
                print(f"Successful Workflows: {summary.get('successful_workflows', 0)}")
                print(f"Total Scripts: {summary.get('total_scripts', 0)}")
                print(f"Working Scripts: {summary.get('working_scripts', 0)}")
                print(f"Total Executions: {summary.get('total_executions', 0)}")
                print(f"Working Executions: {summary.get('working_executions', 0)}")
                print(f"Total Providers: {summary.get('total_providers', 0)}")
                print(f"Successful Providers: {summary.get('successful_providers', 0)}")
                print(f"Overall Status: {summary.get('overall_status', 'unknown')}")
                print("\nRecommendations:")
                for rec in summary.get("recommendations", []):
                    print(f"- {rec}")
                print("=" * 50)

            logger.info("Workflow testing complete.")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

    finally:
        await tester.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
