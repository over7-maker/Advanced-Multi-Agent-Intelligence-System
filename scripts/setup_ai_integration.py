#!/usr/bin/env python3
"""
AI Integration Setup Script - Sets up all AI services and configurations
"""

import asyncio
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime

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

class AIIntegrationSetup:
    """AI Integration Setup Manager"""
    
    def __init__(self):
        self.ai_service = None
        self.config_manager = get_ai_config()
        self.setup_results = {}
    
    async def initialize(self):
        """Initialize the setup manager"""
        try:
            # Load configuration
            config = {
                'deepseek_api_key': os.getenv('DEEPSEEK_API_KEY', ''),
                'glm_api_key': os.getenv('GLM_API_KEY', ''),
                'grok_api_key': os.getenv('GROK_API_KEY', ''),
                'kimi_api_key': os.getenv('KIMI_API_KEY', ''),
                'qwen_api_key': os.getenv('QWEN_API_KEY', ''),
                'gptoss_api_key': os.getenv('GPTOSS_API_KEY', '')
            }
            
            self.ai_service = AIServiceManager(config)
            await self.ai_service.initialize()
            logger.info("AI Integration Setup initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AI Integration Setup: {e}")
            raise
    
    async def validate_ai_providers(self) -> Dict[str, Any]:
        """Validate all AI providers"""
        try:
            logger.info("Validating AI providers...")
            
            # Get configuration validation
            config_validation = self.config_manager.validate_configurations()
            
            # Test each provider
            provider_tests = {}
            for provider in AIProvider:
                config = self.config_manager.get_provider_config(provider)
                if config and config.enabled:
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
                            'provider_used': test_response.provider
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
                'config_validation': config_validation,
                'provider_tests': provider_tests,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error validating AI providers: {e}")
            return {'error': str(e)}
    
    async def test_ai_capabilities(self) -> Dict[str, Any]:
        """Test AI capabilities across all providers"""
        try:
            logger.info("Testing AI capabilities...")
            
            capabilities = {
                'code_generation': await self._test_code_generation(),
                'code_analysis': await self._test_code_analysis(),
                'code_improvement': await self._test_code_improvement(),
                'test_generation': await self._test_test_generation(),
                'documentation': await self._test_documentation(),
                'security_analysis': await self._test_security_analysis()
            }
            
            return {
                'capabilities': capabilities,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error testing AI capabilities: {e}")
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
    
    async def _test_documentation(self) -> Dict[str, Any]:
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
    
    async def setup_github_actions(self) -> Dict[str, Any]:
        """Setup GitHub Actions integration"""
        try:
            logger.info("Setting up GitHub Actions integration...")
            
            # Check if .github/workflows directory exists
            workflows_dir = Path(".github/workflows")
            workflows_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if AI development workflow exists
            ai_workflow = workflows_dir / "ai_development.yml"
            if ai_workflow.exists():
                logger.info("✓ AI development workflow already exists")
                return {'status': 'exists', 'workflow_file': str(ai_workflow)}
            else:
                logger.warning("✗ AI development workflow not found")
                return {'status': 'missing', 'workflow_file': str(ai_workflow)}
            
        except Exception as e:
            logger.error(f"Error setting up GitHub Actions: {e}")
            return {'error': str(e)}
    
    async def generate_setup_report(self) -> Dict[str, Any]:
        """Generate comprehensive setup report"""
        try:
            logger.info("Generating setup report...")
            
            # Validate providers
            provider_validation = await self.validate_ai_providers()
            
            # Test capabilities
            capability_tests = await self.test_ai_capabilities()
            
            # Check GitHub Actions
            github_setup = await self.setup_github_actions()
            
            # Get provider statistics
            provider_stats = self.ai_service.get_provider_stats()
            
            # Generate health check
            health_check = await self.ai_service.health_check()
            
            report = {
                'setup_timestamp': datetime.now().isoformat(),
                'provider_validation': provider_validation,
                'capability_tests': capability_tests,
                'github_setup': github_setup,
                'provider_stats': provider_stats,
                'health_check': health_check,
                'summary': self._generate_summary(provider_validation, capability_tests, health_check)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating setup report: {e}")
            return {'error': str(e)}
    
    def _generate_summary(self, provider_validation: Dict[str, Any], 
                         capability_tests: Dict[str, Any], 
                         health_check: Dict[str, Any]) -> Dict[str, Any]:
        """Generate setup summary"""
        try:
            # Count successful providers
            successful_providers = len([
                p for p in provider_validation.get('provider_tests', {}).values()
                if p.get('status') == 'success'
            ])
            
            # Count successful capabilities
            successful_capabilities = len([
                c for c in capability_tests.get('capabilities', {}).values()
                if c.get('success', False)
            ])
            
            # Overall health
            overall_health = health_check.get('overall_health', 'unknown')
            
            return {
                'total_providers': len(provider_validation.get('provider_tests', {})),
                'successful_providers': successful_providers,
                'total_capabilities': len(capability_tests.get('capabilities', {})),
                'successful_capabilities': successful_capabilities,
                'overall_health': overall_health,
                'setup_status': 'complete' if successful_providers > 0 else 'incomplete',
                'recommendations': self._generate_recommendations(
                    successful_providers, successful_capabilities, overall_health
                )
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {'error': str(e)}
    
    def _generate_recommendations(self, successful_providers: int, 
                                 successful_capabilities: int, 
                                 overall_health: str) -> list:
        """Generate setup recommendations"""
        recommendations = []
        
        if successful_providers == 0:
            recommendations.append("No AI providers are working. Check API keys and network connectivity.")
        elif successful_providers < 3:
            recommendations.append("Only a few AI providers are working. Consider adding more API keys for better reliability.")
        
        if successful_capabilities < 3:
            recommendations.append("Some AI capabilities are not working. Check provider configurations.")
        
        if overall_health == 'critical':
            recommendations.append("System health is critical. Immediate attention required.")
        elif overall_health == 'degraded':
            recommendations.append("System health is degraded. Consider optimizing configurations.")
        
        if not recommendations:
            recommendations.append("AI integration setup is complete and healthy!")
        
        return recommendations
    
    def save_setup_report(self, report: Dict[str, Any], output_file: str):
        """Save setup report to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
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
    parser = argparse.ArgumentParser(description='AI Integration Setup')
    parser.add_argument('--output', default='ai_setup_report.json', help='Output file for setup report')
    parser.add_argument('--validate-only', action='store_true', help='Only validate providers')
    parser.add_argument('--test-only', action='store_true', help='Only test capabilities')
    
    args = parser.parse_args()
    
    setup = AIIntegrationSetup()
    
    try:
        await setup.initialize()
        
        if args.validate_only:
            # Only validate providers
            results = await setup.validate_ai_providers()
            print("\n" + "="*50)
            print("AI PROVIDER VALIDATION RESULTS")
            print("="*50)
            for provider, test in results.get('provider_tests', {}).items():
                status = "✓" if test.get('status') == 'success' else "✗"
                print(f"{status} {provider}: {test.get('status', 'unknown')}")
            print("="*50)
            
        elif args.test_only:
            # Only test capabilities
            results = await setup.test_ai_capabilities()
            print("\n" + "="*50)
            print("AI CAPABILITY TEST RESULTS")
            print("="*50)
            for capability, test in results.get('capabilities', {}).items():
                status = "✓" if test.get('success') else "✗"
                print(f"{status} {capability}: {test.get('success', False)}")
            print("="*50)
            
        else:
            # Full setup report
            results = await setup.generate_setup_report()
            setup.save_setup_report(results, args.output)
            
            # Print summary
            if 'summary' in results:
                summary = results['summary']
                print("\n" + "="*50)
                print("AI INTEGRATION SETUP SUMMARY")
                print("="*50)
                print(f"Total Providers: {summary.get('total_providers', 0)}")
                print(f"Successful Providers: {summary.get('successful_providers', 0)}")
                print(f"Total Capabilities: {summary.get('total_capabilities', 0)}")
                print(f"Successful Capabilities: {summary.get('successful_capabilities', 0)}")
                print(f"Overall Health: {summary.get('overall_health', 'unknown')}")
                print(f"Setup Status: {summary.get('setup_status', 'unknown')}")
                print("\nRecommendations:")
                for rec in summary.get('recommendations', []):
                    print(f"- {rec}")
                print("="*50)
            
            logger.info("AI integration setup complete.")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)
    
    finally:
        await setup.shutdown()

if __name__ == "__main__":
    asyncio.run(main())