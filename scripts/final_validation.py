#!/usr/bin/env python3
"""
Final Validation - Comprehensive validation of all AI integrations and workflows
"""

import asyncio
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime
import subprocess

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from services.ai_service_manager import AIServiceManager, AIProvider
from config.ai_config import get_ai_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FinalValidation:
    """Final Validation Suite"""

    def __init__(self):
        self.ai_service = None
        self.config_manager = get_ai_config()
        self.validation_results = {}

    async def initialize(self):
        """Initialize the validation suite"""
        try:
            config = {
                'deepseek_api_key': os.getenv('DEEPSEEK_API_KEY'),
                'glm_api_key': os.getenv('GLM_API_KEY'),
                'grok_api_key': os.getenv('GROK_API_KEY'),
                'kimi_api_key': os.getenv('KIMI_API_KEY'),
                'qwen_api_key': os.getenv('QWEN_API_KEY'),
                'gptoss_api_key': os.getenv('GPTOSS_API_KEY')
            }

            self.ai_service = AIServiceManager(config)
            await self.ai_service.initialize()
            logger.info("Final Validation initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing Final Validation: {e}")
            raise

    async def validate_ai_providers(self) -> Dict[str, Any]:
        """Validate all AI providers"""
        try:
            logger.info("Validating AI providers...")

            provider_tests = {}
            for provider in AIProvider:
                logger.info(f"Testing {provider.value}...")

                try:
                    # Test with simple request
                    test_response = await self.ai_service.generate_response(
                        "Hello, this is a connectivity test. Respond with 'OK'.",
                        preferred_provider=provider
                    )

                    provider_tests[provider.value] = {
                        'status': 'success' if test_response.success else 'failed',
                        'response_time': test_response.response_time,
                        'error': test_response.error if not test_response.success else None,
                        'provider_used': test_response.provider,
                        'content_length': len(test_response.content) if test_response.success else 0
                    }

                    if test_response.success:
                        logger.info(f"✓ {provider.value} test successful")
                    else:
                        logger.warning(f"✗ {provider.value} test failed: {test_response.error}")

                except Exception as e:
                    provider_tests[provider.value] = {
                        'status': 'error',
                        'error': str(e)
                    }
                    logger.error(f"✗ {provider.value} test error: {e}")

            return {
                'provider_tests': provider_tests,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error validating AI providers: {e}")
            return {'error': str(e)}

    async def validate_ai_capabilities(self) -> Dict[str, Any]:
        """Validate all AI capabilities"""
        try:
            logger.info("Validating AI capabilities...")

            capabilities = {
                'code_generation': await self._test_code_generation(),
                'code_analysis': await self._test_code_analysis(),
                'code_improvement': await self._test_code_improvement(),
                'test_generation': await self._test_test_generation(),
                'documentation_generation': await self._test_documentation_generation(),
                'security_analysis': await self._test_security_analysis(),
                'performance_analysis': await self._test_performance_analysis()
            }

            return {
                'capabilities': capabilities,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error validating AI capabilities: {e}")
            return {'error': str(e)}

    async def _test_code_generation(self) -> Dict[str, Any]:
        """Test code generation capability"""
        try:
            prompt = """Generate a simple Python function that calculates the factorial of a number.
Include proper error handling and documentation."""

            response = await self.ai_service.generate_code(prompt, "python")

            return {
                'success': response.success,
                'provider': response.provider,
                'response_time': response.response_time,
                'content_length': len(response.content) if response.success else 0,
                'error': response.error if not response.success else None
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

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
                'success': response.success,
                'provider': response.provider,
                'response_time': response.response_time,
                'content_length': len(response.content) if response.success else 0,
                'error': response.error if not response.success else None
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

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
                'success': response.success,
                'provider': response.provider,
                'response_time': response.response_time,
                'content_length': len(response.content) if response.success else 0,
                'error': response.error if not response.success else None
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

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
                'success': response.success,
                'provider': response.provider,
                'response_time': response.response_time,
                'content_length': len(response.content) if response.success else 0,
                'error': response.error if not response.success else None
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _test_documentation_generation(self) -> Dict[str, Any]:
        """Test documentation generation capability"""
        try:
            prompt = """Generate comprehensive documentation for a Python function that calculates factorial.
Include function signature, parameters, return value, examples, and usage notes."""

            response = await self.ai_service.generate_response(prompt)

            return {
                'success': response.success,
                'provider': response.provider,
                'response_time': response.response_time,
                'content_length': len(response.content) if response.success else 0,
                'error': response.error if not response.success else None
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

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
                'success': response.success,
                'provider': response.provider,
                'response_time': response.response_time,
                'content_length': len(response.content) if response.success else 0,
                'error': response.error if not response.success else None
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

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
                'success': response.success,
                'provider': response.provider,
                'response_time': response.response_time,
                'content_length': len(response.content) if response.success else 0,
                'error': response.error if not response.success else None
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def validate_all_scripts(self) -> Dict[str, Any]:
        """Validate all AI scripts"""
        try:
            logger.info("Validating all AI scripts...")

            scripts = [
                'ai_code_analyzer.py',
                'ai_code_improver.py',
                'ai_test_generator.py',
                'ai_documentation_generator.py',
                'ai_security_auditor.py',
                'ai_performance_analyzer.py',
                'ai_continuous_developer.py',
                'setup_ai_integration.py',
                'complete_ai_integration.py',
                'test_ai_integration_complete.py',
                'validate_complete_workflows.py',
                'complete_workflow_setup.py'
            ]

            script_validations = {}
            for script in scripts:
                script_path = Path(f"scripts/{script}")
                script_validation = {
                    'exists': script_path.exists(),
                    'readable': False,
                    'has_main': False,
                    'has_argparse': False,
                    'has_ai_service': False,
                    'size': 0,
                    'line_count': 0
                }

                if script_path.exists():
                    try:
                        with open(script_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        script_validation.update({
                            'readable': True,
                            'has_main': 'if __name__ == "__main__"' in content,
                            'has_argparse': 'argparse' in content,
                            'has_ai_service': 'AIServiceManager' in content,
                            'size': len(content),
                            'line_count': len(content.splitlines())
                        })

                    except Exception as e:
                        script_validation['error'] = str(e)

                script_validations[script] = script_validation

            return {
                'script_validations': script_validations,
                'total_scripts': len(scripts),
                'existing_scripts': len([s for s in script_validations.values() if s['exists']]),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error validating AI scripts: {e}")
            return {'error': str(e)}

    def validate_github_actions_workflow(self) -> Dict[str, Any]:
        """Validate GitHub Actions workflow"""
        try:
            logger.info("Validating GitHub Actions workflow...")

            workflow_file = Path(".github/workflows/ai_development.yml")
            if not workflow_file.exists():
                return {
                    'workflow_exists': False,
                    'error': 'Workflow file not found'
                }

            # Read workflow content
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow_content = f.read()

            # Check for required components
            required_components = [
                'ai_code_analysis',
                'ai_code_improvement',
                'ai_test_generation',
                'ai_documentation',
                'ai_security_audit',
                'ai_performance_optimization',
                'continuous_ai_development'
            ]

            component_tests = {}
            for component in required_components:
                component_tests[component] = component in workflow_content

            # Check for environment variables
            env_vars = [
                'DEEPSEEK_API_KEY',
                'GLM_API_KEY',
                'GROK_API_KEY',
                'KIMI_API_KEY',
                'QWEN_API_KEY',
                'GPTOSS_API_KEY'
            ]

            env_tests = {}
            for env_var in env_vars:
                env_tests[env_var] = f'${{{{ secrets.{env_var} }}}}' in workflow_content

            return {
                'workflow_exists': True,
                'component_tests': component_tests,
                'env_tests': env_tests,
                'workflow_size': len(workflow_content),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error validating GitHub Actions workflow: {e}")
            return {'error': str(e)}

    def validate_environment_setup(self) -> Dict[str, Any]:
        """Validate environment setup"""
        try:
            logger.info("Validating environment setup...")

            # Check environment variables
            required_env_vars = [
                'DEEPSEEK_API_KEY',
                'GLM_API_KEY',
                'GROK_API_KEY',
                'KIMI_API_KEY',
                'QWEN_API_KEY',
                'GPTOSS_API_KEY'
            ]

            env_validations = {}
            for env_var in required_env_vars:
                value = os.getenv(env_var)
                env_validations[env_var] = {
                    'set': value is not None,
                    'length': len(value) if value else 0,
                    'starts_with_sk': value.startswith('sk-') if value else False,
                    'valid_format': value and len(value) > 50 if value else False
                }

            # Check Python version
            python_version = sys.version_info
            python_compatible = python_version.major == 3 and python_version.minor >= 8

            # Check required files
            required_files = [
                'services/ai_service_manager.py',
                'config/ai_config.py',
                'AI_INTEGRATION_README.md',
                'setup_ai_complete.sh'
            ]

            file_validations = {}
            for file_path in required_files:
                file_exists = Path(file_path).exists()
                file_validations[file_path] = file_exists

            return {
                'env_validations': env_validations,
                'python_compatible': python_compatible,
                'python_version': f"{python_version.major}.{python_version.minor}.{python_version.micro}",
                'file_validations': file_validations,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error validating environment setup: {e}")
            return {'error': str(e)}

    async def run_final_validation(self) -> Dict[str, Any]:
        """Run final validation"""
        try:
            logger.info("Running final validation...")

            # Validate AI providers
            provider_validation = await self.validate_ai_providers()

            # Validate AI capabilities
            capability_validation = await self.validate_ai_capabilities()

            # Validate all scripts
            script_validation = self.validate_all_scripts()

            # Validate GitHub Actions workflow
            workflow_validation = self.validate_github_actions_workflow()

            # Validate environment setup
            environment_validation = self.validate_environment_setup()

            # Generate final validation report
            validation_report = {
                'timestamp': datetime.now().isoformat(),
                'provider_validation': provider_validation,
                'capability_validation': capability_validation,
                'script_validation': script_validation,
                'workflow_validation': workflow_validation,
                'environment_validation': environment_validation,
                'summary': self._generate_final_summary(
                    provider_validation, capability_validation, script_validation,
                    workflow_validation, environment_validation
                )
            }

            return validation_report

        except Exception as e:
            logger.error(f"Error in final validation: {e}")
            return {'error': str(e)}

    def _generate_final_summary(self, provider_validation: Dict[str, Any],
                              capability_validation: Dict[str, Any],
                              script_validation: Dict[str, Any],
                              workflow_validation: Dict[str, Any],
                              environment_validation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final validation summary"""
        try:
            # Count successful providers
            provider_results = provider_validation.get('provider_tests', {})
            successful_providers = len([
                p for p in provider_results.values()
                if p.get('status') == 'success'
            ])

            # Count successful capabilities
            capability_results = capability_validation.get('capabilities', {})
            successful_capabilities = len([
                c for c in capability_results.values()
                if c.get('success', False)
            ])

            # Count working scripts
            script_results = script_validation.get('script_validations', {})
            working_scripts = len([
                s for s in script_results.values()
                if s.get('exists', False) and s.get('has_main', False)
            ])

            # Check workflow components
            workflow_components = workflow_validation.get('component_tests', {})
            working_components = len([
                c for c in workflow_components.values()
                if c
            ])

            # Check environment variables
            env_results = environment_validation.get('env_validations', {})
            set_env_vars = len([
                e for e in env_results.values()
                if e.get('set', False)
            ])

            return {
                'total_providers': len(provider_results),
                'successful_providers': successful_providers,
                'total_capabilities': len(capability_results),
                'successful_capabilities': successful_capabilities,
                'total_scripts': len(script_results),
                'working_scripts': working_scripts,
                'total_workflow_components': len(workflow_components),
                'working_workflow_components': working_components,
                'total_env_vars': len(env_results),
                'set_env_vars': set_env_vars,
                'python_compatible': environment_validation.get('python_compatible', False),
                'overall_status': 'complete' if successful_providers > 0 and successful_capabilities > 0 else 'incomplete',
                'recommendations': self._generate_final_recommendations(
                    successful_providers, successful_capabilities, working_scripts,
                    working_components, set_env_vars
                )
            }

        except Exception as e:
            logger.error(f"Error generating final summary: {e}")
            return {'error': str(e)}

    def _generate_final_recommendations(self, successful_providers: int,
                                       successful_capabilities: int,
                                       working_scripts: int,
                                       working_components: int,
                                       set_env_vars: int) -> List[str]:
        """Generate final recommendations"""
        recommendations = []

        if successful_providers == 0:
            recommendations.append("No AI providers are working. Check API keys and network connectivity.")
        elif successful_providers < 6:
            recommendations.append(f"Only {successful_providers} AI providers are working. Consider adding more API keys.")

        if successful_capabilities < 7:
            recommendations.append(f"Only {successful_capabilities} AI capabilities are working. Check provider configurations.")

        if working_scripts < 12:
            recommendations.append(f"Only {working_scripts} AI scripts are working. Check script implementations.")

        if working_components < 7:
            recommendations.append(f"Only {working_components} workflow components are working. Check GitHub Actions workflow.")

        if set_env_vars < 6:
            recommendations.append(f"Only {set_env_vars} environment variables are set. Set all required API keys.")

        if successful_providers > 0 and successful_capabilities > 0 and working_scripts > 0:
            recommendations.append("AI integration is working well! All components are functional.")
            recommendations.append("Monitor AI provider health and performance regularly.")

        return recommendations

    def save_validation_report(self, report: Dict[str, Any], output_file: str):
        """Save validation report to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Validation report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving validation report: {e}")

    async def shutdown(self):
        """Shutdown the validation suite"""
        if self.ai_service:
            await self.ai_service.shutdown()

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Final Validation')
    parser.add_argument('--output', default='final_validation_report.json', help='Output file for validation report')
    parser.add_argument('--providers-only', action='store_true', help='Only validate AI providers')
    parser.add_argument('--capabilities-only', action='store_true', help='Only validate AI capabilities')
    parser.add_argument('--scripts-only', action='store_true', help='Only validate AI scripts')
    parser.add_argument('--workflow-only', action='store_true', help='Only validate GitHub Actions workflow')
    parser.add_argument('--environment-only', action='store_true', help='Only validate environment setup')

    args = parser.parse_args()

    validator = FinalValidation()

    try:
        await validator.initialize()

        if args.providers_only:
            # Only validate AI providers
            results = await validator.validate_ai_providers()
            print("\n" + "="*50)
            print("AI PROVIDER VALIDATION RESULTS")
            print("="*50)
            for provider, test in results.get('provider_tests', {}).items():
                status = "✓" if test.get('status') == 'success' else "✗"
                print(f"{status} {provider}: {test.get('status', 'unknown')}")
            print("="*50)

        elif args.capabilities_only:
            # Only validate AI capabilities
            results = await validator.validate_ai_capabilities()
            print("\n" + "="*50)
            print("AI CAPABILITY VALIDATION RESULTS")
            print("="*50)
            for capability, test in results.get('capabilities', {}).items():
                status = "✓" if test.get('success') else "✗"
                print(f"{status} {capability}: {test.get('success', False)}")
            print("="*50)

        elif args.scripts_only:
            # Only validate AI scripts
            results = validator.validate_all_scripts()
            print("\n" + "="*50)
            print("AI SCRIPT VALIDATION RESULTS")
            print("="*50)
            for script, validation in results.get('script_validations', {}).items():
                status = "✓" if validation.get('exists') and validation.get('has_main') else "✗"
                print(f"{status} {script}: {validation.get('exists', False)}")
            print("="*50)

        elif args.workflow_only:
            # Only validate GitHub Actions workflow
            results = validator.validate_github_actions_workflow()
            print("\n" + "="*50)
            print("GITHUB ACTIONS WORKFLOW VALIDATION RESULTS")
            print("="*50)
            print(f"Workflow exists: {results.get('workflow_exists', False)}")
            for component, working in results.get('component_tests', {}).items():
                status = "✓" if working else "✗"
                print(f"{status} {component}: {working}")
            print("="*50)

        elif args.environment_only:
            # Only validate environment setup
            results = validator.validate_environment_setup()
            print("\n" + "="*50)
            print("ENVIRONMENT SETUP VALIDATION RESULTS")
            print("="*50)
            print(f"Python compatible: {results.get('python_compatible', False)}")
            for var, validation in results.get('env_validations', {}).items():
                status = "✓" if validation.get('set') else "✗"
                print(f"{status} {var}: {validation.get('set', False)}")
            print("="*50)

        else:
            # Complete validation
            results = await validator.run_final_validation()
            validator.save_validation_report(results, args.output)

            # Print summary
            if 'summary' in results:
                summary = results['summary']
                print("\n" + "="*50)
                print("FINAL VALIDATION SUMMARY")
                print("="*50)
                print(f"Total Providers: {summary.get('total_providers', 0)}")
                print(f"Successful Providers: {summary.get('successful_providers', 0)}")
                print(f"Total Capabilities: {summary.get('total_capabilities', 0)}")
                print(f"Successful Capabilities: {summary.get('successful_capabilities', 0)}")
                print(f"Total Scripts: {summary.get('total_scripts', 0)}")
                print(f"Working Scripts: {summary.get('working_scripts', 0)}")
                print(f"Total Workflow Components: {summary.get('total_workflow_components', 0)}")
                print(f"Working Workflow Components: {summary.get('working_workflow_components', 0)}")
                print(f"Total Environment Variables: {summary.get('total_env_vars', 0)}")
                print(f"Set Environment Variables: {summary.get('set_env_vars', 0)}")
                print(f"Python Compatible: {summary.get('python_compatible', False)}")
                print(f"Overall Status: {summary.get('overall_status', 'unknown')}")
                print("\nRecommendations:")
                for rec in summary.get('recommendations', []):
                    print(f"- {rec}")
                print("="*50)

            logger.info("Final validation complete.")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

    finally:
        await validator.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
