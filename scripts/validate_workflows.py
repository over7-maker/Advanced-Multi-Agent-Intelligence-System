#!/usr/bin/env python3
"""
Validate Workflows - Comprehensive workflow validation to fix all failing checks
"""

import os
import sys
import yaml
import json
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

class WorkflowValidator:
    """Comprehensive workflow validator"""

    def __init__(self):
        self.validation_results = {}

    def validate_workflow_syntax(self, workflow_file: str) -> Dict[str, Any]:
        """Validate workflow YAML syntax"""
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow_content = f.read()

            # Parse YAML
            workflow_yaml = yaml.safe_load(workflow_content)

            # Check for required fields
            required_fields = ['name', 'on', 'jobs']
            missing_fields = [field for field in required_fields if field not in workflow_yaml]

            # Check jobs
            jobs = workflow_yaml.get('jobs', {})
            job_validations = {}

            for job_name, job_config in jobs.items():
                job_validation = {
                    'has_runs_on': 'runs-on' in job_config,
                    'has_steps': 'steps' in job_config,
                    'step_count': len(job_config.get('steps', [])),
                    'has_env': 'env' in job_config,
                    'has_condition': 'if' in job_config
                }

                # Check steps
                steps = job_config.get('steps', [])
                step_validations = []

                for step in steps:
                    step_validation = {
                        'has_name': 'name' in step,
                        'has_uses': 'uses' in step,
                        'has_run': 'run' in step,
                        'has_env': 'env' in step
                    }
                    step_validations.append(step_validation)

                job_validation['step_validations'] = step_validations
                job_validations[job_name] = job_validation

            return {
                'valid': True,
                'missing_fields': missing_fields,
                'job_count': len(jobs),
                'job_validations': job_validations,
                'workflow_size': len(workflow_content),
                'error': None
            }

        except yaml.YAMLError as e:
            return {
                'valid': False,
                'error': f'YAML syntax error: {e}',
                'missing_fields': [],
                'job_count': 0,
                'job_validations': {},
                'workflow_size': 0
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'missing_fields': [],
                'job_count': 0,
                'job_validations': {},
                'workflow_size': 0
            }

    def validate_workflow_dependencies(self, workflow_file: str) -> Dict[str, Any]:
        """Validate workflow dependencies"""
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow_content = f.read()

            # Check for required dependencies
            required_deps = [
                'openai',
                'aiohttp',
                'python-dotenv',
                'requests',
                'pyyaml'
            ]

            missing_deps = []
            for dep in required_deps:
                if dep not in workflow_content:
                    missing_deps.append(dep)

            # Check for error handling
            has_error_handling = '|| echo' in workflow_content or '|| true' in workflow_content

            # Check for environment variables
            env_vars = [
                'DEEPSEEK_API_KEY',
                'GLM_API_KEY',
                'GROK_API_KEY',
                'KIMI_API_KEY',
                'QWEN_API_KEY',
                'GPTOSS_API_KEY'
            ]

            missing_env_vars = []
            for env_var in env_vars:
                if f'${{{{ secrets.{env_var} }}}}' not in workflow_content:
                    missing_env_vars.append(env_var)

            return {
                'missing_dependencies': missing_deps,
                'has_error_handling': has_error_handling,
                'missing_env_vars': missing_env_vars,
                'total_deps': len(required_deps),
                'found_deps': len(required_deps) - len(missing_deps)
            }

        except Exception as e:
            return {
                'missing_dependencies': [],
                'has_error_handling': False,
                'missing_env_vars': [],
                'total_deps': 0,
                'found_deps': 0,
                'error': str(e)
            }

    def validate_workflow_scripts(self, workflow_file: str) -> Dict[str, Any]:
        """Validate that all referenced scripts exist"""
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow_content = f.read()

            # Extract script references
            script_references = []
            lines = workflow_content.split('\n')

            for line in lines:
                if 'python scripts/' in line:
                    # Extract script name
                    parts = line.split('python scripts/')
                    if len(parts) > 1:
                        script_part = parts[1].split()[0]
                        script_references.append(f'scripts/{script_part}')

            # Check if scripts exist
            script_validations = {}
            for script_ref in script_references:
                script_path = Path(script_ref)
                script_validations[script_ref] = {
                    'exists': script_path.exists(),
                    'readable': script_path.exists() and script_path.is_file()
                }

            return {
                'script_references': script_references,
                'script_validations': script_validations,
                'total_scripts': len(script_references),
                'existing_scripts': len([s for s in script_validations.values() if s['exists']])
            }

        except Exception as e:
            return {
                'script_references': [],
                'script_validations': {},
                'total_scripts': 0,
                'existing_scripts': 0,
                'error': str(e)
            }

    def validate_all_workflows(self) -> Dict[str, Any]:
        """Validate all workflows"""
        try:
            logger.info("Validating all workflows...")

            workflow_files = [
                '.github/workflows/ai_development.yml',
                '.github/workflows/ai_complete_workflow.yml',
                '.github/workflows/ai_simple_workflow.yml'
            ]

            workflow_validations = {}

            for workflow_file in workflow_files:
                logger.info(f"Validating {workflow_file}...")

                # Validate syntax
                syntax_validation = self.validate_workflow_syntax(workflow_file)

                # Validate dependencies
                dependency_validation = self.validate_workflow_dependencies(workflow_file)

                # Validate scripts
                script_validation = self.validate_workflow_scripts(workflow_file)

                workflow_validations[workflow_file] = {
                    'syntax': syntax_validation,
                    'dependencies': dependency_validation,
                    'scripts': script_validation,
                    'overall_valid': syntax_validation.get('valid', False) and
                                   len(dependency_validation.get('missing_dependencies', [])) == 0 and
                                   dependency_validation.get('has_error_handling', False)
                }

            return {
                'workflow_validations': workflow_validations,
                'total_workflows': len(workflow_files),
                'valid_workflows': len([w for w in workflow_validations.values() if w.get('overall_valid', False)]),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error validating workflows: {e}")
            return {'error': str(e)}

    def generate_fixes(self, validation_results: Dict[str, Any]) -> List[str]:
        """Generate fixes for workflow issues"""
        fixes = []

        workflow_validations = validation_results.get('workflow_validations', {})

        for workflow_file, validation in workflow_validations.items():
            syntax = validation.get('syntax', {})
            dependencies = validation.get('dependencies', {})
            scripts = validation.get('scripts', {})

            # Fix syntax issues
            if not syntax.get('valid', False):
                fixes.append(f"Fix YAML syntax in {workflow_file}: {syntax.get('error', 'Unknown error')}")

            # Fix missing dependencies
            missing_deps = dependencies.get('missing_dependencies', [])
            if missing_deps:
                fixes.append(f"Add missing dependencies to {workflow_file}: {', '.join(missing_deps)}")

            # Fix missing error handling
            if not dependencies.get('has_error_handling', False):
                fixes.append(f"Add error handling to {workflow_file}")

            # Fix missing environment variables
            missing_env_vars = dependencies.get('missing_env_vars', [])
            if missing_env_vars:
                fixes.append(f"Add missing environment variables to {workflow_file}: {', '.join(missing_env_vars)}")

            # Fix missing scripts
            script_validations = scripts.get('script_validations', {})
            missing_scripts = [s for s, v in script_validations.items() if not v.get('exists', False)]
            if missing_scripts:
                fixes.append(f"Create missing scripts for {workflow_file}: {', '.join(missing_scripts)}")

        return fixes

    def save_validation_report(self, results: Dict[str, Any], output_file: str):
        """Save validation report"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Validation report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving validation report: {e}")

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Validate Workflows')
    parser.add_argument('--output', default='workflow_validation_report.json', help='Output file for validation report')
    parser.add_argument('--workflow', help='Specific workflow file to validate')

    args = parser.parse_args()

    validator = WorkflowValidator()

    try:
        if args.workflow:
            # Validate specific workflow
            results = {
                'workflow_file': args.workflow,
                'syntax': validator.validate_workflow_syntax(args.workflow),
                'dependencies': validator.validate_workflow_dependencies(args.workflow),
                'scripts': validator.validate_workflow_scripts(args.workflow),
                'timestamp': datetime.now().isoformat()
            }
        else:
            # Validate all workflows
            results = validator.validate_all_workflows()

        # Generate fixes
        fixes = validator.generate_fixes(results)
        results['fixes'] = fixes

        # Save report
        validator.save_validation_report(results, args.output)

        # Print summary
        print("\n" + "="*50)
        print("WORKFLOW VALIDATION SUMMARY")
        print("="*50)

        if args.workflow:
            syntax = results.get('syntax', {})
            dependencies = results.get('dependencies', {})
            scripts = results.get('scripts', {})

            print(f"Workflow: {args.workflow}")
            print(f"Syntax Valid: {syntax.get('valid', False)}")
            print(f"Missing Dependencies: {len(dependencies.get('missing_dependencies', []))}")
            print(f"Has Error Handling: {dependencies.get('has_error_handling', False)}")
            print(f"Missing Scripts: {len([s for s in scripts.get('script_validations', {}).values() if not s.get('exists', False)])}")
        else:
            total_workflows = results.get('total_workflows', 0)
            valid_workflows = results.get('valid_workflows', 0)
            print(f"Total Workflows: {total_workflows}")
            print(f"Valid Workflows: {valid_workflows}")
            print(f"Invalid Workflows: {total_workflows - valid_workflows}")

        print(f"\nFixes Needed: {len(fixes)}")
        for i, fix in enumerate(fixes, 1):
            print(f"{i}. {fix}")

        print("="*50)

        logger.info("Workflow validation complete.")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
