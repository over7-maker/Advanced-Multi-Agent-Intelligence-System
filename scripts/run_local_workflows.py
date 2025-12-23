#!/usr/bin/env python3
"""
Local GitHub Actions Workflow Runner
Executes GitHub Actions workflows locally by parsing YAML and running equivalent Python scripts.
"""

import os
import sys
import json
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class LocalWorkflowRunner:
    """Run GitHub Actions workflows locally."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.workflows_dir = project_root / ".github" / "workflows"
        self.scripts_dir = project_root / ".github" / "scripts"
        
    def load_workflow(self, workflow_file: Path) -> Dict[str, Any]:
        """Load and parse a workflow YAML file."""
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading workflow {workflow_file}: {e}")
            return {}
    
    def get_workflow_jobs(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Extract jobs from workflow."""
        return workflow.get('jobs', {})
    
    def find_script_for_step(self, step: Dict[str, Any]) -> Optional[Path]:
        """Find the Python script that corresponds to a workflow step."""
        run_content = step.get('run', '')
        
        # Look for Python script execution
        if 'python' in run_content.lower():
            # Extract script path
            lines = run_content.split('\n')
            for line in lines:
                if 'python' in line.lower() and '.py' in line:
                    # Extract path
                    parts = line.split()
                    for part in parts:
                        if '.py' in part and not part.startswith('-'):
                            script_path = part.strip()
                            # Handle relative paths
                            if script_path.startswith('.'):
                                full_path = self.project_root / script_path.lstrip('./')
                            else:
                                full_path = self.scripts_dir / script_path
                            
                            if full_path.exists():
                                return full_path
        
        return None
    
    def execute_step(self, step: Dict[str, Any], job_name: str, step_name: str) -> bool:
        """Execute a single workflow step."""
        step_name_display = step.get('name', step_name)
        print(f"\n  🔹 Step: {step_name_display}")
        
        # Check if it's a script execution
        if 'run' in step:
            script_path = self.find_script_for_step(step)
            if script_path:
                print(f"    📜 Running script: {script_path.relative_to(self.project_root)}")
                return self.run_script(script_path, step.get('run', ''))
            else:
                # Execute shell command directly
                print(f"    💻 Executing command...")
                return self.run_shell_command(step.get('run', ''))
        
        # Handle action steps (skip for now, would need action simulation)
        if 'uses' in step:
            action = step.get('uses', '')
            print(f"    ⏭️  Skipping GitHub Action: {action}")
            print(f"    💡 This would run on GitHub Actions")
            return True
        
        return True
    
    def run_script(self, script_path: Path, original_command: str) -> bool:
        """Run a Python script."""
        try:
            # Extract arguments from original command if possible
            cmd = [sys.executable, str(script_path)]
            
            # Try to parse arguments from the original run command
            if '--' in original_command:
                parts = original_command.split('--', 1)[1].strip().split()
                cmd.extend(parts)
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                if result.stdout:
                    print(f"    ✅ Output: {result.stdout[:200]}...")
                return True
            else:
                print(f"    ❌ Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"    ❌ Exception: {e}")
            return False
    
    def run_shell_command(self, command: str) -> bool:
        """Run a shell command."""
        try:
            # Use shell=True for Windows compatibility
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                if result.stdout:
                    print(f"    ✅ Output: {result.stdout[:200]}...")
                return True
            else:
                print(f"    ⚠️  Warning: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"    ❌ Exception: {e}")
            return False
    
    def execute_job(self, job_name: str, job_config: Dict[str, Any]) -> bool:
        """Execute a workflow job."""
        print(f"\n{'='*60}")
        print(f"🔧 Job: {job_name}")
        print(f"{'='*60}")
        
        steps = job_config.get('steps', [])
        print(f"📋 Found {len(steps)} steps")
        
        success = True
        for i, step in enumerate(steps, 1):
            step_result = self.execute_step(step, job_name, f"step_{i}")
            if not step_result:
                print(f"    ⚠️  Step {i} had issues, but continuing...")
                # Don't fail completely, just note it
        
        return success
    
    def execute_workflow(self, workflow_file: Path, job_filter: Optional[str] = None) -> bool:
        """Execute a complete workflow."""
        print("=" * 60)
        print(f"🚀 Executing Workflow: {workflow_file.name}")
        print("=" * 60)
        
        workflow = self.load_workflow(workflow_file)
        if not workflow:
            return False
        
        workflow_name = workflow.get('name', workflow_file.stem)
        print(f"📝 Workflow Name: {workflow_name}")
        
        jobs = self.get_workflow_jobs(workflow)
        print(f"📦 Found {len(jobs)} jobs")
        
        if job_filter:
            if job_filter in jobs:
                jobs = {job_filter: jobs[job_filter]}
            else:
                print(f"❌ Job '{job_filter}' not found in workflow")
                return False
        
        # Execute jobs (handle dependencies later)
        for job_name, job_config in jobs.items():
            # Skip if job has conditions that aren't met
            if 'if' in job_config:
                print(f"⏭️  Skipping {job_name} (condition not evaluated locally)")
                continue
            
            self.execute_job(job_name, job_config)
        
        print("\n" + "=" * 60)
        print("✅ Workflow execution complete!")
        print("=" * 60)
        return True
    
    def list_workflows(self) -> List[Path]:
        """List all available workflow files."""
        workflows = []
        if self.workflows_dir.exists():
            for workflow_file in self.workflows_dir.glob("*.yml"):
                if not workflow_file.name.startswith('.'):
                    workflows.append(workflow_file)
            for workflow_file in self.workflows_dir.glob("*.yaml"):
                if not workflow_file.name.startswith('.'):
                    workflows.append(workflow_file)
        return sorted(workflows)
    
    def list_jobs(self, workflow_file: Path) -> List[str]:
        """List all jobs in a workflow."""
        workflow = self.load_workflow(workflow_file)
        return list(workflow.get('jobs', {}).keys())


def main():
    parser = argparse.ArgumentParser(
        description="Run GitHub Actions workflows locally"
    )
    parser.add_argument(
        'workflow',
        nargs='?',
        help='Workflow file to run (e.g., 00-master-ai-orchestrator.yml)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available workflows'
    )
    parser.add_argument(
        '--job',
        help='Run only a specific job from the workflow'
    )
    parser.add_argument(
        '--list-jobs',
        metavar='WORKFLOW',
        help='List all jobs in a workflow'
    )
    
    args = parser.parse_args()
    
    runner = LocalWorkflowRunner(PROJECT_ROOT)
    
    if args.list:
        print("📋 Available Workflows:")
        workflows = runner.list_workflows()
        for i, workflow in enumerate(workflows, 1):
            print(f"  {i}. {workflow.name}")
        return
    
    if args.list_jobs:
        workflow_file = PROJECT_ROOT / ".github" / "workflows" / args.list_jobs
        if not workflow_file.exists():
            print(f"❌ Workflow file not found: {workflow_file}")
            return
        
        jobs = runner.list_jobs(workflow_file)
        print(f"📋 Jobs in {args.list_jobs}:")
        for job in jobs:
            print(f"  - {job}")
        return
    
    if not args.workflow:
        print("❌ Please specify a workflow file or use --list to see available workflows")
        print("\nUsage examples:")
        print("  python scripts/run_local_workflows.py --list")
        print("  python scripts/run_local_workflows.py 00-master-ai-orchestrator.yml")
        print("  python scripts/run_local_workflows.py 00-master-ai-orchestrator.yml --job layer1_detection_analysis")
        return
    
    workflow_file = PROJECT_ROOT / ".github" / "workflows" / args.workflow
    if not workflow_file.exists():
        print(f"❌ Workflow file not found: {workflow_file}")
        print(f"💡 Use --list to see available workflows")
        return
    
    runner.execute_workflow(workflow_file, args.job)


if __name__ == "__main__":
    main()


