#!/usr/bin/env python3
"""
Complete Workflow Validation - Validates all AI workflows and integrations
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

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CompleteWorkflowValidator:
    """Complete Workflow Validator"""

    def __init__(self):
        self.validation_results = {}

    def validate_github_actions_workflow(self) -> Dict[str, Any]:
        """Validate GitHub Actions workflow"""
        try:
            logger.info("Validating GitHub Actions workflow...")

            workflow_file = Path(".github/workflows/ai_development.yml")
            if not workflow_file.exists():
                return {"workflow_exists": False, "error": "Workflow file not found"}

            # Read and parse workflow
            with open(workflow_file, "r", encoding="utf-8") as f:
                workflow_content = f.read()

            try:
                workflow_yaml = yaml.safe_load(workflow_content)
            except yaml.YAMLError as e:
                return {
                    "workflow_exists": True,
                    "yaml_valid": False,
                    "error": f"YAML parsing error: {e}",
                }

            # Validate required jobs
            required_jobs = [
                "ai_code_analysis",
                "ai_code_improvement",
                "ai_test_generation",
                "ai_documentation",
                "ai_security_audit",
                "ai_performance_optimization",
                "continuous_ai_development",
            ]

            jobs = workflow_yaml.get("jobs", {})
            job_validations = {}

            for job in required_jobs:
                if job in jobs:
                    job_config = jobs[job]
                    job_validations[job] = {
                        "exists": True,
                        "has_steps": "steps" in job_config,
                        "has_env": "env" in job_config,
                        "has_run": any(
                            "run" in step for step in job_config.get("steps", [])
                        ),
                        "step_count": len(job_config.get("steps", [])),
                    }
                else:
                    job_validations[job] = {
                        "exists": False,
                        "has_steps": False,
                        "has_env": False,
                        "has_run": False,
                        "step_count": 0,
                    }

            # Validate environment variables
            env_vars = [
                "DEEPSEEK_API_KEY",
                "GLM_API_KEY",
                "GROK_API_KEY",
                "KIMI_API_KEY",
                "QWEN_API_KEY",
                "GPTOSS_API_KEY",
            ]

            env_validation = {}
            for env_var in env_vars:
                env_validation[env_var] = (
                    f"${{{{ secrets.{env_var} }}}}" in workflow_content
                )

            # Validate script references
            required_scripts = [
                "ai_code_analyzer.py",
                "ai_code_improver.py",
                "ai_test_generator.py",
                "ai_documentation_generator.py",
                "ai_security_auditor.py",
                "ai_performance_analyzer.py",
                "ai_continuous_developer.py",
            ]

            script_validation = {}
            for script in required_scripts:
                script_validation[script] = script in workflow_content

            return {
                "workflow_exists": True,
                "yaml_valid": True,
                "job_validations": job_validations,
                "env_validation": env_validation,
                "script_validation": script_validation,
                "workflow_size": len(workflow_content),
                "total_jobs": len(jobs),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error validating GitHub Actions workflow: {e}")
            return {"error": str(e)}

    def validate_ai_scripts(self) -> Dict[str, Any]:
        """Validate all AI scripts"""
        try:
            logger.info("Validating AI scripts...")

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
                "test_ai_integration_complete.py",
            ]

            script_validations = {}

            for script in scripts:
                script_path = Path(f"scripts/{script}")
                script_validation = {
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

                        script_validation.update(
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
                        script_validation["error"] = str(e)

                script_validations[script] = script_validation

            return {
                "script_validations": script_validations,
                "total_scripts": len(scripts),
                "existing_scripts": len(
                    [s for s in script_validations.values() if s["exists"]]
                ),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error validating AI scripts: {e}")
            return {"error": str(e)}

    def validate_ai_services(self) -> Dict[str, Any]:
        """Validate AI service components"""
        try:
            logger.info("Validating AI service components...")

            service_files = ["services/ai_service_manager.py", "config/ai_config.py"]

            service_validations = {}

            for service_file in service_files:
                file_path = Path(service_file)
                service_validation = {
                    "exists": file_path.exists(),
                    "readable": False,
                    "has_classes": False,
                    "has_async_methods": False,
                    "size": 0,
                    "line_count": 0,
                }

                if file_path.exists():
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        service_validation.update(
                            {
                                "readable": True,
                                "has_classes": "class " in content,
                                "has_async_methods": "async def " in content,
                                "size": len(content),
                                "line_count": len(content.splitlines()),
                            }
                        )

                    except Exception as e:
                        service_validation["error"] = str(e)

                service_validations[service_file] = service_validation

            return {
                "service_validations": service_validations,
                "total_services": len(service_files),
                "existing_services": len(
                    [s for s in service_validations.values() if s["exists"]]
                ),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error validating AI services: {e}")
            return {"error": str(e)}

    def validate_documentation(self) -> Dict[str, Any]:
        """Validate documentation"""
        try:
            logger.info("Validating documentation...")

            doc_files = [
                "AI_INTEGRATION_README.md",
                "README.md",
                "setup_ai_complete.sh",
            ]

            doc_validations = {}

            for doc_file in doc_files:
                file_path = Path(doc_file)
                doc_validation = {
                    "exists": file_path.exists(),
                    "readable": False,
                    "size": 0,
                    "line_count": 0,
                    "has_ai_content": False,
                }

                if file_path.exists():
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        doc_validation.update(
                            {
                                "readable": True,
                                "size": len(content),
                                "line_count": len(content.splitlines()),
                                "has_ai_content": "AI" in content or "ai" in content,
                            }
                        )

                    except Exception as e:
                        doc_validation["error"] = str(e)

                doc_validations[doc_file] = doc_validation

            return {
                "doc_validations": doc_validations,
                "total_docs": len(doc_files),
                "existing_docs": len(
                    [d for d in doc_validations.values() if d["exists"]]
                ),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error validating documentation: {e}")
            return {"error": str(e)}

    def validate_environment_setup(self) -> Dict[str, Any]:
        """Validate environment setup"""
        try:
            logger.info("Validating environment setup...")

            # Check environment variables
            required_env_vars = [
                "DEEPSEEK_API_KEY",
                "GLM_API_KEY",
                "GROK_API_KEY",
                "KIMI_API_KEY",
                "QWEN_API_KEY",
                "GPTOSS_API_KEY",
            ]

            env_validations = {}
            for env_var in required_env_vars:
                value = os.getenv(env_var)
                env_validations[env_var] = {
                    "set": value is not None,
                    "length": len(value) if value else 0,
                    "starts_with_sk": value.startswith("sk-") if value else False,
                    "valid_format": value and len(value) > 50 if value else False,
                }

            # Check Python version
            python_version = sys.version_info
            python_compatible = python_version.major == 3 and python_version.minor >= 8

            # Check required directories
            required_dirs = ["scripts", "services", "config", ".github/workflows"]

            dir_validations = {}
            for dir_path in required_dirs:
                path = Path(dir_path)
                dir_validations[dir_path] = {
                    "exists": path.exists(),
                    "is_directory": path.is_dir() if path.exists() else False,
                }

            return {
                "env_validations": env_validations,
                "python_compatible": python_compatible,
                "python_version": f"{python_version.major}.{python_version.minor}.{python_version.micro}",
                "dir_validations": dir_validations,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error validating environment setup: {e}")
            return {"error": str(e)}

    def test_script_execution(self) -> Dict[str, Any]:
        """Test script execution"""
        try:
            logger.info("Testing script execution...")

            test_scripts = [
                "setup_ai_integration.py",
                "test_ai_integration_complete.py",
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

    def run_complete_validation(self) -> Dict[str, Any]:
        """Run complete workflow validation"""
        try:
            logger.info("Running complete workflow validation...")

            # Validate GitHub Actions workflow
            workflow_validation = self.validate_github_actions_workflow()

            # Validate AI scripts
            script_validation = self.validate_ai_scripts()

            # Validate AI services
            service_validation = self.validate_ai_services()

            # Validate documentation
            doc_validation = self.validate_documentation()

            # Validate environment setup
            env_validation = self.validate_environment_setup()

            # Test script execution
            execution_validation = self.test_script_execution()

            # Generate comprehensive validation report
            validation_report = {
                "timestamp": datetime.now().isoformat(),
                "workflow_validation": workflow_validation,
                "script_validation": script_validation,
                "service_validation": service_validation,
                "doc_validation": doc_validation,
                "env_validation": env_validation,
                "execution_validation": execution_validation,
                "summary": self._generate_validation_summary(
                    workflow_validation,
                    script_validation,
                    service_validation,
                    doc_validation,
                    env_validation,
                    execution_validation,
                ),
            }

            return validation_report

        except Exception as e:
            logger.error(f"Error in complete validation: {e}")
            return {"error": str(e)}

    def _generate_validation_summary(
        self,
        workflow_validation: Dict[str, Any],
        script_validation: Dict[str, Any],
        service_validation: Dict[str, Any],
        doc_validation: Dict[str, Any],
        env_validation: Dict[str, Any],
        execution_validation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate validation summary"""
        try:
            # Count successful validations
            workflow_jobs = workflow_validation.get("job_validations", {})
            successful_jobs = len(
                [
                    j
                    for j in workflow_jobs.values()
                    if j.get("exists", False) and j.get("has_steps", False)
                ]
            )

            script_results = script_validation.get("script_validations", {})
            working_scripts = len(
                [
                    s
                    for s in script_results.values()
                    if s.get("exists", False) and s.get("has_main", False)
                ]
            )

            service_results = service_validation.get("service_validations", {})
            working_services = len(
                [
                    s
                    for s in service_results.values()
                    if s.get("exists", False) and s.get("has_classes", False)
                ]
            )

            doc_results = doc_validation.get("doc_validations", {})
            existing_docs = len(
                [d for d in doc_results.values() if d.get("exists", False)]
            )

            env_results = env_validation.get("env_validations", {})
            set_env_vars = len([e for e in env_results.values() if e.get("set", False)])

            execution_results = execution_validation.get("execution_tests", {})
            working_executions = len(
                [e for e in execution_results.values() if e.get("help_works", False)]
            )

            return {
                "total_workflow_jobs": len(workflow_jobs),
                "successful_workflow_jobs": successful_jobs,
                "total_scripts": len(script_results),
                "working_scripts": working_scripts,
                "total_services": len(service_results),
                "working_services": working_services,
                "total_docs": len(doc_results),
                "existing_docs": existing_docs,
                "total_env_vars": len(env_results),
                "set_env_vars": set_env_vars,
                "total_executions": len(execution_results),
                "working_executions": working_executions,
                "python_compatible": env_validation.get("python_compatible", False),
                "overall_status": (
                    "complete"
                    if successful_jobs > 0 and working_scripts > 0
                    else "incomplete"
                ),
                "recommendations": self._generate_validation_recommendations(
                    successful_jobs,
                    working_scripts,
                    working_services,
                    existing_docs,
                    set_env_vars,
                    working_executions,
                ),
            }

        except Exception as e:
            logger.error(f"Error generating validation summary: {e}")
            return {"error": str(e)}

    def _generate_validation_recommendations(
        self,
        successful_jobs: int,
        working_scripts: int,
        working_services: int,
        existing_docs: int,
        set_env_vars: int,
        working_executions: int,
    ) -> List[str]:
        """Generate validation recommendations"""
        recommendations = []

        if successful_jobs < 7:
            recommendations.append(
                f"Only {successful_jobs} workflow jobs are complete. Complete all GitHub Actions workflows."
            )

        if working_scripts < 10:
            recommendations.append(
                f"Only {working_scripts} AI scripts are working. Check script implementations."
            )

        if working_services < 2:
            recommendations.append(
                f"Only {working_services} AI services are working. Check service implementations."
            )

        if existing_docs < 3:
            recommendations.append(
                f"Only {existing_docs} documentation files exist. Complete all documentation."
            )

        if set_env_vars < 6:
            recommendations.append(
                f"Only {set_env_vars} environment variables are set. Set all required API keys."
            )

        if working_executions < 2:
            recommendations.append(
                f"Only {working_executions} scripts can execute. Check script implementations."
            )

        if successful_jobs > 0 and working_scripts > 0 and working_services > 0:
            recommendations.append(
                "Workflow validation is mostly complete! Address remaining issues."
            )
            recommendations.append("All components are working together successfully.")

        return recommendations

    def save_validation_report(self, report: Dict[str, Any], output_file: str):
        """Save validation report to file"""
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Validation report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving validation report: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Complete Workflow Validation")
    parser.add_argument(
        "--output",
        default="complete_workflow_validation_report.json",
        help="Output file for validation report",
    )
    parser.add_argument(
        "--workflow-only",
        action="store_true",
        help="Only validate GitHub Actions workflow",
    )
    parser.add_argument(
        "--scripts-only", action="store_true", help="Only validate AI scripts"
    )
    parser.add_argument(
        "--services-only", action="store_true", help="Only validate AI services"
    )
    parser.add_argument(
        "--docs-only", action="store_true", help="Only validate documentation"
    )
    parser.add_argument(
        "--env-only", action="store_true", help="Only validate environment setup"
    )
    parser.add_argument(
        "--execution-only", action="store_true", help="Only test script execution"
    )

    args = parser.parse_args()

    validator = CompleteWorkflowValidator()

    try:
        if args.workflow_only:
            # Only validate GitHub Actions workflow
            results = validator.validate_github_actions_workflow()
            print("\n" + "=" * 50)
            print("GITHUB ACTIONS WORKFLOW VALIDATION")
            print("=" * 50)
            print(f"Workflow exists: {results.get('workflow_exists', False)}")
            print(f"YAML valid: {results.get('yaml_valid', False)}")
            for job, validation in results.get("job_validations", {}).items():
                status = "✓" if validation.get("exists") else "✗"
                print(f"{status} {job}: {validation.get('exists', False)}")
            print("=" * 50)

        elif args.scripts_only:
            # Only validate AI scripts
            results = validator.validate_ai_scripts()
            print("\n" + "=" * 50)
            print("AI SCRIPTS VALIDATION")
            print("=" * 50)
            for script, validation in results.get("script_validations", {}).items():
                status = (
                    "✓"
                    if validation.get("exists") and validation.get("has_main")
                    else "✗"
                )
                print(f"{status} {script}: {validation.get('exists', False)}")
            print("=" * 50)

        elif args.services_only:
            # Only validate AI services
            results = validator.validate_ai_services()
            print("\n" + "=" * 50)
            print("AI SERVICES VALIDATION")
            print("=" * 50)
            for service, validation in results.get("service_validations", {}).items():
                status = (
                    "✓"
                    if validation.get("exists") and validation.get("has_classes")
                    else "✗"
                )
                print(f"{status} {service}: {validation.get('exists', False)}")
            print("=" * 50)

        elif args.docs_only:
            # Only validate documentation
            results = validator.validate_documentation()
            print("\n" + "=" * 50)
            print("DOCUMENTATION VALIDATION")
            print("=" * 50)
            for doc, validation in results.get("doc_validations", {}).items():
                status = "✓" if validation.get("exists") else "✗"
                print(f"{status} {doc}: {validation.get('exists', False)}")
            print("=" * 50)

        elif args.env_only:
            # Only validate environment setup
            results = validator.validate_environment_setup()
            print("\n" + "=" * 50)
            print("ENVIRONMENT SETUP VALIDATION")
            print("=" * 50)
            print(f"Python compatible: {results.get('python_compatible', False)}")
            for var, validation in results.get("env_validations", {}).items():
                status = "✓" if validation.get("set") else "✗"
                print(f"{status} {var}: {validation.get('set', False)}")
            print("=" * 50)

        elif args.execution_only:
            # Only test script execution
            results = validator.test_script_execution()
            print("\n" + "=" * 50)
            print("SCRIPT EXECUTION VALIDATION")
            print("=" * 50)
            for script, validation in results.get("execution_tests", {}).items():
                status = "✓" if validation.get("help_works") else "✗"
                print(f"{status} {script}: {validation.get('help_works', False)}")
            print("=" * 50)

        else:
            # Complete validation
            results = validator.run_complete_validation()
            validator.save_validation_report(results, args.output)

            # Print summary
            if "summary" in results:
                summary = results["summary"]
                print("\n" + "=" * 50)
                print("COMPLETE WORKFLOW VALIDATION SUMMARY")
                print("=" * 50)
                print(f"Total Workflow Jobs: {summary.get('total_workflow_jobs', 0)}")
                print(
                    f"Successful Workflow Jobs: {summary.get('successful_workflow_jobs', 0)}"
                )
                print(f"Total Scripts: {summary.get('total_scripts', 0)}")
                print(f"Working Scripts: {summary.get('working_scripts', 0)}")
                print(f"Total Services: {summary.get('total_services', 0)}")
                print(f"Working Services: {summary.get('working_services', 0)}")
                print(f"Total Docs: {summary.get('total_docs', 0)}")
                print(f"Existing Docs: {summary.get('existing_docs', 0)}")
                print(f"Total Env Vars: {summary.get('total_env_vars', 0)}")
                print(f"Set Env Vars: {summary.get('set_env_vars', 0)}")
                print(f"Total Executions: {summary.get('total_executions', 0)}")
                print(f"Working Executions: {summary.get('working_executions', 0)}")
                print(f"Python Compatible: {summary.get('python_compatible', False)}")
                print(f"Overall Status: {summary.get('overall_status', 'unknown')}")
                print("\nRecommendations:")
                for rec in summary.get("recommendations", []):
                    print(f"- {rec}")
                print("=" * 50)

            logger.info("Complete workflow validation finished.")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
