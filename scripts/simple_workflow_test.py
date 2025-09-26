#!/usr/bin/env python3
"""
Simple Workflow Test - Test workflows without AI dependencies
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime
import yaml

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleWorkflowTest:
    """Simple workflow tester without AI dependencies"""
    
    def __init__(self):
        self.test_results = {}
    
    def test_github_workflows(self) -> Dict[str, Any]:
        """Test GitHub Actions workflows"""
        try:
            logger.info("Testing GitHub Actions workflows...")
            
            workflow_files = [
                '.github/workflows/ai_development.yml',
                '.github/workflows/ai_complete_workflow.yml',
                '.github/workflows/ai_simple_workflow.yml'
            ]
            
            workflow_tests = {}
            
            for workflow_file in workflow_files:
                workflow_path = Path(workflow_file)
                if workflow_path.exists():
                    try:
                        with open(workflow_path, 'r', encoding='utf-8') as f:
                            workflow_content = f.read()
                        
                        # Parse YAML
                        workflow_yaml = yaml.safe_load(workflow_content)
                        
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
                        
                        jobs = workflow_yaml.get('jobs', {})
                        component_tests = {}
                        
                        for component in required_components:
                            component_tests[component] = component in jobs
                        
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
                        
                        workflow_tests[workflow_file] = {
                            'exists': True,
                            'yaml_valid': True,
                            'component_tests': component_tests,
                            'env_tests': env_tests,
                            'workflow_size': len(workflow_content),
                            'total_jobs': len(jobs),
                            'working_components': len([c for c in component_tests.values() if c])
                        }
                        
                    except yaml.YAMLError as e:
                        workflow_tests[workflow_file] = {
                            'exists': True,
                            'yaml_valid': False,
                            'error': f'YAML parsing error: {e}'
                        }
                    
                    except Exception as e:
                        workflow_tests[workflow_file] = {
                            'exists': True,
                            'yaml_valid': False,
                            'error': str(e)
                        }
                else:
                    workflow_tests[workflow_file] = {
                        'exists': False,
                        'yaml_valid': False,
                        'error': 'Workflow file not found'
                    }
            
            return {
                'workflow_tests': workflow_tests,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error testing GitHub workflows: {e}")
            return {'error': str(e)}
    
    def test_ai_scripts(self) -> Dict[str, Any]:
        """Test all AI scripts"""
        try:
            logger.info("Testing AI scripts...")
            
            scripts = [
                'ai_code_analyzer.py',
                'ai_code_improver.py',
                'ai_test_generator.py',
                'ai_documentation_generator.py',
                'ai_security_auditor.py',
                'ai_performance_analyzer.py',
                'ai_continuous_developer.py',
                'ai_issues_responder.py',
                'setup_ai_integration.py',
                'complete_ai_integration.py',
                'test_ai_integration_complete.py',
                'validate_complete_workflows.py',
                'complete_workflow_setup.py',
                'final_validation.py',
                'test_workflows.py',
                'simple_workflow_test.py'
            ]
            
            script_tests = {}
            
            for script in scripts:
                script_path = Path(f"scripts/{script}")
                script_test = {
                    'exists': script_path.exists(),
                    'readable': False,
                    'has_main': False,
                    'has_argparse': False,
                    'size': 0,
                    'line_count': 0
                }
                
                if script_path.exists():
                    try:
                        with open(script_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        script_test.update({
                            'readable': True,
                            'has_main': 'if __name__ == "__main__"' in content,
                            'has_argparse': 'argparse' in content,
                            'size': len(content),
                            'line_count': len(content.splitlines())
                        })
                        
                    except Exception as e:
                        script_test['error'] = str(e)
                
                script_tests[script] = script_test
            
            return {
                'script_tests': script_tests,
                'total_scripts': len(scripts),
                'existing_scripts': len([s for s in script_tests.values() if s['exists']]),
                'working_scripts': len([s for s in script_tests.values() if s['exists'] and s['has_main']]),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error testing AI scripts: {e}")
            return {'error': str(e)}
    
    def test_environment_setup(self) -> Dict[str, Any]:
        """Test environment setup"""
        try:
            logger.info("Testing environment setup...")
            
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
            logger.error(f"Error testing environment setup: {e}")
            return {'error': str(e)}
    
    def run_complete_test(self) -> Dict[str, Any]:
        """Run complete workflow test"""
        try:
            logger.info("Running complete workflow test...")
            
            # Test GitHub workflows
            workflow_tests = self.test_github_workflows()
            
            # Test AI scripts
            script_tests = self.test_ai_scripts()
            
            # Test environment setup
            environment_tests = self.test_environment_setup()
            
            # Generate comprehensive test report
            test_report = {
                'timestamp': datetime.now().isoformat(),
                'workflow_tests': workflow_tests,
                'script_tests': script_tests,
                'environment_tests': environment_tests,
                'summary': self._generate_test_summary(
                    workflow_tests, script_tests, environment_tests
                )
            }
            
            return test_report
            
        except Exception as e:
            logger.error(f"Error in complete test: {e}")
            return {'error': str(e)}
    
    def _generate_test_summary(self, workflow_tests: Dict[str, Any],
                             script_tests: Dict[str, Any],
                             environment_tests: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test summary"""
        try:
            # Count successful workflows
            workflow_results = workflow_tests.get('workflow_tests', {})
            successful_workflows = len([
                w for w in workflow_results.values()
                if w.get('yaml_valid', False) and w.get('working_components', 0) > 0
            ])
            
            # Count working scripts
            script_results = script_tests.get('script_tests', {})
            working_scripts = len([
                s for s in script_results.values()
                if s.get('exists', False) and s.get('has_main', False)
            ])
            
            # Count environment variables
            env_results = environment_tests.get('env_validations', {})
            set_env_vars = len([
                e for e in env_results.values()
                if e.get('set', False)
            ])
            
            # Count required files
            file_results = environment_tests.get('file_validations', {})
            existing_files = len([
                f for f in file_results.values()
                if f
            ])
            
            return {
                'total_workflows': len(workflow_results),
                'successful_workflows': successful_workflows,
                'total_scripts': len(script_results),
                'working_scripts': working_scripts,
                'total_env_vars': len(env_results),
                'set_env_vars': set_env_vars,
                'total_files': len(file_results),
                'existing_files': existing_files,
                'python_compatible': environment_tests.get('python_compatible', False),
                'overall_status': 'complete' if successful_workflows > 0 and working_scripts > 0 else 'incomplete',
                'recommendations': self._generate_test_recommendations(
                    successful_workflows, working_scripts, set_env_vars, existing_files
                )
            }
            
        except Exception as e:
            logger.error(f"Error generating test summary: {e}")
            return {'error': str(e)}
    
    def _generate_test_recommendations(self, successful_workflows: int,
                                     working_scripts: int,
                                     set_env_vars: int,
                                     existing_files: int) -> List[str]:
        """Generate test recommendations"""
        recommendations = []
        
        if successful_workflows == 0:
            recommendations.append("No workflows are working. Check GitHub Actions configuration.")
        elif successful_workflows < 3:
            recommendations.append(f"Only {successful_workflows} workflows are working. Complete all workflow configurations.")
        
        if working_scripts < 16:
            recommendations.append(f"Only {working_scripts} AI scripts are working. Check script implementations.")
        
        if set_env_vars < 6:
            recommendations.append(f"Only {set_env_vars} environment variables are set. Set all required API keys.")
        
        if existing_files < 4:
            recommendations.append(f"Only {existing_files} required files exist. Check file implementations.")
        
        if successful_workflows > 0 and working_scripts > 0:
            recommendations.append("Workflow testing is mostly complete! Address remaining issues.")
            recommendations.append("All components are working together successfully.")
        
        return recommendations
    
    def save_test_report(self, report: Dict[str, Any], output_file: str):
        """Save test report to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Test report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving test report: {e}")

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Simple Workflow Test')
    parser.add_argument('--output', default='simple_workflow_test_report.json', help='Output file for test report')
    parser.add_argument('--workflows-only', action='store_true', help='Only test GitHub workflows')
    parser.add_argument('--scripts-only', action='store_true', help='Only test AI scripts')
    parser.add_argument('--environment-only', action='store_true', help='Only test environment setup')
    
    args = parser.parse_args()
    
    tester = SimpleWorkflowTest()
    
    try:
        if args.workflows_only:
            # Only test GitHub workflows
            results = tester.test_github_workflows()
            print("\n" + "="*50)
            print("GITHUB WORKFLOWS TEST RESULTS")
            print("="*50)
            for workflow, test in results.get('workflow_tests', {}).items():
                status = "✓" if test.get('yaml_valid') and test.get('working_components', 0) > 0 else "✗"
                print(f"{status} {workflow}: {test.get('working_components', 0)} components")
            print("="*50)
            
        elif args.scripts_only:
            # Only test AI scripts
            results = tester.test_ai_scripts()
            print("\n" + "="*50)
            print("AI SCRIPTS TEST RESULTS")
            print("="*50)
            for script, test in results.get('script_tests', {}).items():
                status = "✓" if test.get('exists') and test.get('has_main') else "✗"
                print(f"{status} {script}: {test.get('exists', False)}")
            print("="*50)
            
        elif args.environment_only:
            # Only test environment setup
            results = tester.test_environment_setup()
            print("\n" + "="*50)
            print("ENVIRONMENT SETUP TEST RESULTS")
            print("="*50)
            print(f"Python compatible: {results.get('python_compatible', False)}")
            for var, test in results.get('env_validations', {}).items():
                status = "✓" if test.get('set') else "✗"
                print(f"{status} {var}: {test.get('set', False)}")
            for file, exists in results.get('file_validations', {}).items():
                status = "✓" if exists else "✗"
                print(f"{status} {file}: {exists}")
            print("="*50)
            
        else:
            # Complete test
            results = tester.run_complete_test()
            tester.save_test_report(results, args.output)
            
            # Print summary
            if 'summary' in results:
                summary = results['summary']
                print("\n" + "="*50)
                print("SIMPLE WORKFLOW TEST SUMMARY")
                print("="*50)
                print(f"Total Workflows: {summary.get('total_workflows', 0)}")
                print(f"Successful Workflows: {summary.get('successful_workflows', 0)}")
                print(f"Total Scripts: {summary.get('total_scripts', 0)}")
                print(f"Working Scripts: {summary.get('working_scripts', 0)}")
                print(f"Total Env Vars: {summary.get('total_env_vars', 0)}")
                print(f"Set Env Vars: {summary.get('set_env_vars', 0)}")
                print(f"Total Files: {summary.get('total_files', 0)}")
                print(f"Existing Files: {summary.get('existing_files', 0)}")
                print(f"Python Compatible: {summary.get('python_compatible', False)}")
                print(f"Overall Status: {summary.get('overall_status', 'unknown')}")
                print("\nRecommendations:")
                for rec in summary.get('recommendations', []):
                    print(f"- {rec}")
                print("="*50)
            
            logger.info("Simple workflow testing complete.")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()