#!/usr/bin/env python3
"""
Test Workflow Execution - Test that all workflows can execute without errors
"""

import os
import sys
import yaml
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorkflowExecutionTester:
    """Test workflow execution"""

    def __init__(self):
        self.test_results = {}

    def test_script_execution(self, script_path: str) -> Dict[str, Any]:
        """Test if a script can execute"""
        try:
            if not Path(script_path).exists():
                return {
                    'exists': False,
                    'executable': False,
                    'error': 'Script not found'
                }

            # Test help command
            result = subprocess.run([
                sys.executable, script_path, '--help'
            ], capture_output=True, text=True, timeout=30)

            return {
                'exists': True,
                'executable': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                'exists': True,
                'executable': False,
                'output': '',
                'error': 'Timeout',
                'return_code': -1
            }
        except Exception as e:
            return {
                'exists': True,
                'executable': False,
                'output': '',
                'error': str(e),
                'return_code': -1
            }

    def test_workflow_scripts(self) -> Dict[str, Any]:
        """Test all scripts referenced in workflows"""
        try:
            logger.info("Testing workflow scripts...")

            # Get all scripts referenced in workflows
            workflow_files = [
                '.github/workflows/ai_development.yml',
                '.github/workflows/ai_complete_workflow.yml',
                '.github/workflows/ai_simple_workflow.yml'
            ]

            script_references = set()

            for workflow_file in workflow_files:
                if Path(workflow_file).exists():
                    with open(workflow_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Extract script references
                    lines = content.split('\n')
                    for line in lines:
                        if 'python scripts/' in line:
                            parts = line.split('python scripts/')
                            if len(parts) > 1:
                                script_part = parts[1].split()[0]
                                script_references.add(f'scripts/{script_part}')

            # Test each script
            script_tests = {}
            for script_ref in script_references:
                logger.info(f"Testing {script_ref}...")
                script_tests[script_ref] = self.test_script_execution(script_ref)

            return {
                'script_tests': script_tests,
                'total_scripts': len(script_references),
                'executable_scripts': len([s for s in script_tests.values() if s.get('executable', False)]),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error testing workflow scripts: {e}")
            return {'error': str(e)}

    def test_workflow_syntax(self) -> Dict[str, Any]:
        """Test workflow YAML syntax"""
        try:
            logger.info("Testing workflow syntax...")

            workflow_files = [
                '.github/workflows/ai_development.yml',
                '.github/workflows/ai_complete_workflow.yml',
                '.github/workflows/ai_simple_workflow.yml'
            ]

            syntax_tests = {}

            for workflow_file in workflow_files:
                if Path(workflow_file).exists():
                    try:
                        with open(workflow_file, 'r', encoding='utf-8') as f:
                            yaml.safe_load(f)
                        syntax_tests[workflow_file] = {
                            'valid': True,
                            'error': None
                        }
                    except yaml.YAMLError as e:
                        syntax_tests[workflow_file] = {
                            'valid': False,
                            'error': str(e)
                        }
                else:
                    syntax_tests[workflow_file] = {
                        'valid': False,
                        'error': 'File not found'
                    }

            return {
                'syntax_tests': syntax_tests,
                'total_workflows': len(workflow_files),
                'valid_workflows': len([s for s in syntax_tests.values() if s.get('valid', False)]),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error testing workflow syntax: {e}")
            return {'error': str(e)}

    def test_dependencies(self) -> Dict[str, Any]:
        """Test if all dependencies are available"""
        try:
            logger.info("Testing dependencies...")

            required_deps = [
                'openai',
                'aiohttp',
                'python-dotenv',
                'requests',
                'pyyaml'
            ]

            dep_tests = {}

            for dep in required_deps:
                try:
                    __import__(dep)
                    dep_tests[dep] = {
                        'available': True,
                        'error': None
                    }
                except ImportError:
                    dep_tests[dep] = {
                        'available': False,
                        'error': f'Module {dep} not found'
                    }

            return {
                'dep_tests': dep_tests,
                'total_deps': len(required_deps),
                'available_deps': len([d for d in dep_tests.values() if d.get('available', False)]),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error testing dependencies: {e}")
            return {'error': str(e)}

    def run_complete_test(self) -> Dict[str, Any]:
        """Run complete workflow execution test"""
        try:
            logger.info("Running complete workflow execution test...")

            # Test workflow syntax
            syntax_tests = self.test_workflow_syntax()

            # Test dependencies
            dependency_tests = self.test_dependencies()

            # Test workflow scripts
            script_tests = self.test_workflow_scripts()

            # Generate comprehensive test report
            test_report = {
                'timestamp': datetime.now().isoformat(),
                'syntax_tests': syntax_tests,
                'dependency_tests': dependency_tests,
                'script_tests': script_tests,
                'summary': self._generate_test_summary(
                    syntax_tests, dependency_tests, script_tests
                )
            }

            return test_report

        except Exception as e:
            logger.error(f"Error in complete test: {e}")
            return {'error': str(e)}

    def _generate_test_summary(self, syntax_tests: Dict[str, Any],
                              dependency_tests: Dict[str, Any],
                              script_tests: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test summary"""
        try:
            # Count valid workflows
            valid_workflows = syntax_tests.get('valid_workflows', 0)
            total_workflows = syntax_tests.get('total_workflows', 0)

            # Count available dependencies
            available_deps = dependency_tests.get('available_deps', 0)
            total_deps = dependency_tests.get('total_deps', 0)

            # Count executable scripts
            executable_scripts = script_tests.get('executable_scripts', 0)
            total_scripts = script_tests.get('total_scripts', 0)

            return {
                'total_workflows': total_workflows,
                'valid_workflows': valid_workflows,
                'total_dependencies': total_deps,
                'available_dependencies': available_deps,
                'total_scripts': total_scripts,
                'executable_scripts': executable_scripts,
                'overall_status': 'ready' if valid_workflows > 0 and available_deps > 0 else 'not_ready',
                'recommendations': self._generate_recommendations(
                    valid_workflows, total_workflows,
                    available_deps, total_deps,
                    executable_scripts, total_scripts
                )
            }

        except Exception as e:
            logger.error(f"Error generating test summary: {e}")
            return {'error': str(e)}

    def _generate_recommendations(self, valid_workflows: int, total_workflows: int,
                                 available_deps: int, total_deps: int,
                                 executable_scripts: int, total_scripts: int) -> List[str]:
        """Generate recommendations"""
        recommendations = []

        if valid_workflows < total_workflows:
            recommendations.append(f"Fix {total_workflows - valid_workflows} invalid workflows")

        if available_deps < total_deps:
            recommendations.append(f"Install {total_deps - available_deps} missing dependencies")

        if executable_scripts < total_scripts:
            recommendations.append(f"Fix {total_scripts - executable_scripts} non-executable scripts")

        if valid_workflows > 0 and available_deps > 0:
            recommendations.append("Workflows are ready for execution")

        return recommendations

    def save_test_report(self, report: Dict[str, Any], output_file: str):
        """Save test report"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Test report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving test report: {e}")

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Test Workflow Execution')
    parser.add_argument('--output', default='workflow_execution_test_report.json', help='Output file for test report')
    parser.add_argument('--syntax-only', action='store_true', help='Only test workflow syntax')
    parser.add_argument('--deps-only', action='store_true', help='Only test dependencies')
    parser.add_argument('--scripts-only', action='store_true', help='Only test scripts')

    args = parser.parse_args()

    tester = WorkflowExecutionTester()

    try:
        if args.syntax_only:
            # Only test syntax
            results = tester.test_workflow_syntax()
            print("\n" + "="*50)
            print("WORKFLOW SYNTAX TEST RESULTS")
            print("="*50)
            for workflow, test in results.get('syntax_tests', {}).items():
                status = "✓" if test.get('valid') else "✗"
                print(f"{status} {workflow}: {test.get('valid', False)}")
            print("="*50)

        elif args.deps_only:
            # Only test dependencies
            results = tester.test_dependencies()
            print("\n" + "="*50)
            print("DEPENDENCY TEST RESULTS")
            print("="*50)
            for dep, test in results.get('dep_tests', {}).items():
                status = "✓" if test.get('available') else "✗"
                print(f"{status} {dep}: {test.get('available', False)}")
            print("="*50)

        elif args.scripts_only:
            # Only test scripts
            results = tester.test_workflow_scripts()
            print("\n" + "="*50)
            print("SCRIPT TEST RESULTS")
            print("="*50)
            for script, test in results.get('script_tests', {}).items():
                status = "✓" if test.get('executable') else "✗"
                print(f"{status} {script}: {test.get('executable', False)}")
            print("="*50)

        else:
            # Complete test
            results = tester.run_complete_test()
            tester.save_test_report(results, args.output)

            # Print summary
            if 'summary' in results:
                summary = results['summary']
                print("\n" + "="*50)
                print("WORKFLOW EXECUTION TEST SUMMARY")
                print("="*50)
                print(f"Total Workflows: {summary.get('total_workflows', 0)}")
                print(f"Valid Workflows: {summary.get('valid_workflows', 0)}")
                print(f"Total Dependencies: {summary.get('total_dependencies', 0)}")
                print(f"Available Dependencies: {summary.get('available_dependencies', 0)}")
                print(f"Total Scripts: {summary.get('total_scripts', 0)}")
                print(f"Executable Scripts: {summary.get('executable_scripts', 0)}")
                print(f"Overall Status: {summary.get('overall_status', 'unknown')}")
                print("\nRecommendations:")
                for rec in summary.get('recommendations', []):
                    print(f"- {rec}")
                print("="*50)

            logger.info("Workflow execution testing complete.")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
