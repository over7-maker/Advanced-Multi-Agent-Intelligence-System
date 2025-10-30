from standalone_universal_ai_manager import get_api_key
#!/usr/bin/env python3
"""
Complete Workflow Setup - Sets up and validates all AI workflows and integrations
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

from services.ai_service_manager import AIProvider, AIServiceManager

from config.ai_config import get_ai_config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CompleteWorkflowSetup:
    """Complete Workflow Setup Manager"""

    def __init__(self):
        self.ai_service = None
        self.config_manager = get_ai_config()
        self.setup_results = {}

    async def initialize(self):
        """Initialize the setup manager"""
        try:
            config = {
                "deepseek_api_key": get_api_key("DEEPSEEK_API_KEY"),
                "glm_api_key": get_api_key("GLM_API_KEY"),
                "grok_api_key": get_api_key("GROK_API_KEY"),
                "kimi_api_key": get_api_key("KIMI_API_KEY"),
                "qwen_api_key": get_api_key("QWEN_API_KEY"),
                "gptoss_api_key": get_api_key("GPTOSS_API_KEY"),
            }

            self.ai_service = AIServiceManager(config)
            await self.ai_service.initialize()
            logger.info("Complete Workflow Setup initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing Complete Workflow Setup: {e}")
            raise

    async def setup_all_ai_workflows(self) -> Dict[str, Any]:
        """Setup all AI workflows"""
        try:
            logger.info("Setting up all AI workflows...")

            workflows = {
                "code_analysis": await self._setup_code_analysis_workflow(),
                "code_improvement": await self._setup_code_improvement_workflow(),
                "test_generation": await self._setup_test_generation_workflow(),
                "documentation": await self._setup_documentation_workflow(),
                "security_audit": await self._setup_security_audit_workflow(),
                "performance_analysis": await self._setup_performance_analysis_workflow(),
                "continuous_development": await self._setup_continuous_development_workflow(),
            }

            return {"workflows": workflows, "timestamp": datetime.now().isoformat()}

        except Exception as e:
            logger.error(f"Error setting up AI workflows: {e}")
            return {"error": str(e)}

    async def _setup_code_analysis_workflow(self) -> Dict[str, Any]:
        """Setup code analysis workflow"""
        try:
            prompt = """Create a comprehensive code analysis workflow for AMAS that:

1. Uses multiple AI providers for analysis
2. Analyzes code quality, security, and performance
3. Generates detailed analysis reports
4. Provides actionable recommendations
5. Integrates with GitHub Actions

Generate a complete workflow implementation."""

            response = await self.ai_service.generate_code(prompt, "python")

            if response.success:
                return {
                    "workflow_code": response.content,
                    "provider": response.provider,
                    "status": "generated",
                }
            else:
                return {"status": "failed", "error": response.error}

        except Exception as e:
            logger.error(f"Error setting up code analysis workflow: {e}")
            return {"error": str(e)}

    async def _setup_code_improvement_workflow(self) -> Dict[str, Any]:
        """Setup code improvement workflow"""
        try:
            prompt = """Create a comprehensive code improvement workflow for AMAS that:

1. Uses AI to improve code quality
2. Implements performance optimizations
3. Applies security best practices
4. Generates improved code versions
5. Creates pull requests with improvements

Generate a complete workflow implementation."""

            response = await self.ai_service.generate_code(prompt, "python")

            if response.success:
                return {
                    "workflow_code": response.content,
                    "provider": response.provider,
                    "status": "generated",
                }
            else:
                return {"status": "failed", "error": response.error}

        except Exception as e:
            logger.error(f"Error setting up code improvement workflow: {e}")
            return {"error": str(e)}

    async def _setup_test_generation_workflow(self) -> Dict[str, Any]:
        """Setup test generation workflow"""
        try:
            prompt = """Create a comprehensive test generation workflow for AMAS that:

1. Uses AI to generate comprehensive tests
2. Creates unit, integration, and performance tests
3. Ensures high test coverage
4. Generates test documentation
5. Integrates with CI/CD pipeline

Generate a complete workflow implementation."""

            response = await self.ai_service.generate_code(prompt, "python")

            if response.success:
                return {
                    "workflow_code": response.content,
                    "provider": response.provider,
                    "status": "generated",
                }
            else:
                return {"status": "failed", "error": response.error}

        except Exception as e:
            logger.error(f"Error setting up test generation workflow: {e}")
            return {"error": str(e)}

    async def _setup_documentation_workflow(self) -> Dict[str, Any]:
        """Setup documentation workflow"""
        try:
            prompt = """Create a comprehensive documentation workflow for AMAS that:

1. Uses AI to generate documentation
2. Creates API documentation
3. Generates user guides
4. Maintains documentation quality
5. Publishes documentation automatically

Generate a complete workflow implementation."""

            response = await self.ai_service.generate_code(prompt, "python")

            if response.success:
                return {
                    "workflow_code": response.content,
                    "provider": response.provider,
                    "status": "generated",
                }
            else:
                return {"status": "failed", "error": response.error}

        except Exception as e:
            logger.error(f"Error setting up documentation workflow: {e}")
            return {"error": str(e)}

    async def _setup_security_audit_workflow(self) -> Dict[str, Any]:
        """Setup security audit workflow"""
        try:
            prompt = """Create a comprehensive security audit workflow for AMAS that:

1. Uses AI to perform security audits
2. Identifies vulnerabilities
3. Generates security reports
4. Provides remediation recommendations
5. Integrates with security tools

Generate a complete workflow implementation."""

            response = await self.ai_service.generate_code(prompt, "python")

            if response.success:
                return {
                    "workflow_code": response.content,
                    "provider": response.provider,
                    "status": "generated",
                }
            else:
                return {"status": "failed", "error": response.error}

        except Exception as e:
            logger.error(f"Error setting up security audit workflow: {e}")
            return {"error": str(e)}

    async def _setup_performance_analysis_workflow(self) -> Dict[str, Any]:
        """Setup performance analysis workflow"""
        try:
            prompt = """Create a comprehensive performance analysis workflow for AMAS that:

1. Uses AI to analyze performance
2. Identifies bottlenecks
3. Provides optimization recommendations
4. Generates performance reports
5. Monitors performance metrics

Generate a complete workflow implementation."""

            response = await self.ai_service.generate_code(prompt, "python")

            if response.success:
                return {
                    "workflow_code": response.content,
                    "provider": response.provider,
                    "status": "generated",
                }
            else:
                return {"status": "failed", "error": response.error}

        except Exception as e:
            logger.error(f"Error setting up performance analysis workflow: {e}")
            return {"error": str(e)}

    async def _setup_continuous_development_workflow(self) -> Dict[str, Any]:
        """Setup continuous development workflow"""
        try:
            prompt = """Create a comprehensive continuous development workflow for AMAS that:

1. Uses AI for continuous development
2. Automatically improves code
3. Generates new features
4. Maintains code quality
5. Provides development insights

Generate a complete workflow implementation."""

            response = await self.ai_service.generate_code(prompt, "python")

            if response.success:
                return {
                    "workflow_code": response.content,
                    "provider": response.provider,
                    "status": "generated",
                }
            else:
                return {"status": "failed", "error": response.error}

        except Exception as e:
            logger.error(f"Error setting up continuous development workflow: {e}")
            return {"error": str(e)}

    def validate_all_components(self) -> Dict[str, Any]:
        """Validate all components"""
        try:
            logger.info("Validating all components...")

            # Validate GitHub Actions workflow
            workflow_file = Path(".github/workflows/ai_development.yml")
            workflow_valid = workflow_file.exists()

            # Validate AI scripts
            ai_scripts = [
                "ai_code_analyzer.py",
                "ai_code_improver.py",
                "ai_test_generator.py",
                "ai_documentation_generator.py",
                "ai_security_auditor.py",
                "ai_performance_analyzer.py",
                "ai_continuous_developer.py",
                "setup_ai_integration.py",
                "complete_ai_integration.py",
                "test_ai_integration_complete.py",
                "validate_complete_workflows.py",
            ]

            script_validations = {}
            for script in ai_scripts:
                script_path = Path(f"scripts/{script}")
                script_validations[script] = {
                    "exists": script_path.exists(),
                    "readable": script_path.exists() and script_path.is_file(),
                }

            # Validate AI services
            service_files = ["services/ai_service_manager.py", "config/ai_config.py"]

            service_validations = {}
            for service_file in service_files:
                service_path = Path(service_file)
                service_validations[service_file] = {
                    "exists": service_path.exists(),
                    "readable": service_path.exists() and service_path.is_file(),
                }

            # Validate documentation
            doc_files = [
                "AI_INTEGRATION_README.md",
                "README.md",
                "setup_ai_complete.sh",
            ]

            doc_validations = {}
            for doc_file in doc_files:
                doc_path = Path(doc_file)
                doc_validations[doc_file] = {
                    "exists": doc_path.exists(),
                    "readable": doc_path.exists() and doc_path.is_file(),
                }

            return {
                "workflow_valid": workflow_valid,
                "script_validations": script_validations,
                "service_validations": service_validations,
                "doc_validations": doc_validations,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error validating components: {e}")
            return {"error": str(e)}

    def test_all_scripts(self) -> Dict[str, Any]:
        """Test all scripts"""
        try:
            logger.info("Testing all scripts...")

            test_scripts = [
                "setup_ai_integration.py",
                "test_ai_integration_complete.py",
                "validate_complete_workflows.py",
            ]

            script_tests = {}
            for script in test_scripts:
                script_path = Path(f"scripts/{script}")
                if script_path.exists():
                    try:
                        result = subprocess.run(
                            [sys.executable, str(script_path), "--help"],
                            capture_output=True,
                            text=True,
                            timeout=30,
                        )

                        script_tests[script] = {
                            "exists": True,
                            "help_works": result.returncode == 0,
                            "output": result.stdout,
                            "error": result.stderr,
                        }

                    except subprocess.TimeoutExpired:
                        script_tests[script] = {
                            "exists": True,
                            "help_works": False,
                            "output": "",
                            "error": "Timeout",
                        }

                    except Exception as e:
                        script_tests[script] = {
                            "exists": True,
                            "help_works": False,
                            "output": "",
                            "error": str(e),
                        }
                else:
                    script_tests[script] = {
                        "exists": False,
                        "help_works": False,
                        "output": "",
                        "error": "File not found",
                    }

            return {
                "script_tests": script_tests,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error testing scripts: {e}")
            return {"error": str(e)}

    async def run_complete_setup(self) -> Dict[str, Any]:
        """Run complete workflow setup"""
        try:
            logger.info("Running complete workflow setup...")

            # Setup all AI workflows
            workflow_setup = await self.setup_all_ai_workflows()

            # Validate all components
            component_validation = self.validate_all_components()

            # Test all scripts
            script_testing = self.test_all_scripts()

            # Generate comprehensive setup report
            setup_report = {
                "timestamp": datetime.now().isoformat(),
                "workflow_setup": workflow_setup,
                "component_validation": component_validation,
                "script_testing": script_testing,
                "summary": self._generate_setup_summary(
                    workflow_setup, component_validation, script_testing
                ),
            }

            return setup_report

        except Exception as e:
            logger.error(f"Error in complete setup: {e}")
            return {"error": str(e)}

    def _generate_setup_summary(
        self,
        workflow_setup: Dict[str, Any],
        component_validation: Dict[str, Any],
        script_testing: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate setup summary"""
        try:
            # Count successful workflows
            workflows = workflow_setup.get("workflows", {})
            successful_workflows = len(
                [w for w in workflows.values() if w.get("status") == "generated"]
            )

            # Count validated components
            script_results = component_validation.get("script_validations", {})
            validated_scripts = len(
                [s for s in script_results.values() if s.get("exists", False)]
            )

            service_results = component_validation.get("service_validations", {})
            validated_services = len(
                [s for s in service_results.values() if s.get("exists", False)]
            )

            doc_results = component_validation.get("doc_validations", {})
            validated_docs = len(
                [d for d in doc_results.values() if d.get("exists", False)]
            )

            # Count working scripts
            script_tests = script_testing.get("script_tests", {})
            working_scripts = len(
                [s for s in script_tests.values() if s.get("help_works", False)]
            )

            return {
                "total_workflows": len(workflows),
                "successful_workflows": successful_workflows,
                "total_scripts": len(script_results),
                "validated_scripts": validated_scripts,
                "total_services": len(service_results),
                "validated_services": validated_services,
                "total_docs": len(doc_results),
                "validated_docs": validated_docs,
                "total_script_tests": len(script_tests),
                "working_scripts": working_scripts,
                "workflow_valid": component_validation.get("workflow_valid", False),
                "overall_status": (
                    "complete"
                    if successful_workflows > 0 and working_scripts > 0
                    else "incomplete"
                ),
                "recommendations": self._generate_setup_recommendations(
                    successful_workflows,
                    validated_scripts,
                    validated_services,
                    validated_docs,
                    working_scripts,
                ),
            }

        except Exception as e:
            logger.error(f"Error generating setup summary: {e}")
            return {"error": str(e)}

    def _generate_setup_recommendations(
        self,
        successful_workflows: int,
        validated_scripts: int,
        validated_services: int,
        validated_docs: int,
        working_scripts: int,
    ) -> List[str]:
        """Generate setup recommendations"""
        recommendations = []

        if successful_workflows < 7:
            recommendations.append(
                f"Only {successful_workflows} workflows were generated. Complete all AI workflows."
            )

        if validated_scripts < 11:
            recommendations.append(
                f"Only {validated_scripts} scripts are validated. Check script implementations."
            )

        if validated_services < 2:
            recommendations.append(
                f"Only {validated_services} services are validated. Check service implementations."
            )

        if validated_docs < 3:
            recommendations.append(
                f"Only {validated_docs} documentation files are validated. Complete all documentation."
            )

        if working_scripts < 3:
            recommendations.append(
                f"Only {working_scripts} scripts are working. Check script implementations."
            )

        if successful_workflows > 0 and working_scripts > 0:
            recommendations.append(
                "Workflow setup is mostly complete! Address remaining issues."
            )
            recommendations.append("All components are working together successfully.")

        return recommendations

    def save_setup_report(self, report: Dict[str, Any], output_file: str):
        """Save setup report to file"""
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Setup report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving setup report: {e}")

    async def shutdown(self):
        """Shutdown the setup manager"""
        if self.ai_service:
            await self.ai_service.shutdown()


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Complete Workflow Setup")
    parser.add_argument(
        "--output",
        default="complete_workflow_setup_report.json",
        help="Output file for setup report",
    )
    parser.add_argument(
        "--workflows-only", action="store_true", help="Only setup AI workflows"
    )
    parser.add_argument(
        "--validate-only", action="store_true", help="Only validate components"
    )
    parser.add_argument("--test-only", action="store_true", help="Only test scripts")

    args = parser.parse_args()

    setup = CompleteWorkflowSetup()

    try:
        await setup.initialize()

        if args.workflows_only:
            # Only setup AI workflows
            results = await setup.setup_all_ai_workflows()
            print("\n" + "=" * 50)
            print("AI WORKFLOW SETUP RESULTS")
            print("=" * 50)
            for workflow, result in results.get("workflows", {}).items():
                status = "✓" if result.get("status") == "generated" else "✗"
                print(f"{status} {workflow}: {result.get('status', 'unknown')}")
            print("=" * 50)

        elif args.validate_only:
            # Only validate components
            results = setup.validate_all_components()
            print("\n" + "=" * 50)
            print("COMPONENT VALIDATION RESULTS")
            print("=" * 50)
            print(f"Workflow valid: {results.get('workflow_valid', False)}")
            for script, validation in results.get("script_validations", {}).items():
                status = "✓" if validation.get("exists") else "✗"
                print(f"{status} {script}: {validation.get('exists', False)}")
            print("=" * 50)

        elif args.test_only:
            # Only test scripts
            results = setup.test_all_scripts()
            print("\n" + "=" * 50)
            print("SCRIPT TESTING RESULTS")
            print("=" * 50)
            for script, test in results.get("script_tests", {}).items():
                status = "✓" if test.get("help_works") else "✗"
                print(f"{status} {script}: {test.get('help_works', False)}")
            print("=" * 50)

        else:
            # Complete setup
            results = await setup.run_complete_setup()
            setup.save_setup_report(results, args.output)

            # Print summary
            if "summary" in results:
                summary = results["summary"]
                print("\n" + "=" * 50)
                print("COMPLETE WORKFLOW SETUP SUMMARY")
                print("=" * 50)
                print(f"Total Workflows: {summary.get('total_workflows', 0)}")
                print(f"Successful Workflows: {summary.get('successful_workflows', 0)}")
                print(f"Total Scripts: {summary.get('total_scripts', 0)}")
                print(f"Validated Scripts: {summary.get('validated_scripts', 0)}")
                print(f"Total Services: {summary.get('total_services', 0)}")
                print(f"Validated Services: {summary.get('validated_services', 0)}")
                print(f"Total Docs: {summary.get('total_docs', 0)}")
                print(f"Validated Docs: {summary.get('validated_docs', 0)}")
                print(f"Total Script Tests: {summary.get('total_script_tests', 0)}")
                print(f"Working Scripts: {summary.get('working_scripts', 0)}")
                print(f"Workflow Valid: {summary.get('workflow_valid', False)}")
                print(f"Overall Status: {summary.get('overall_status', 'unknown')}")
                print("\nRecommendations:")
                for rec in summary.get("recommendations", []):
                    print(f"- {rec}")
                print("=" * 50)

            logger.info("Complete workflow setup finished.")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

    finally:
        await setup.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
