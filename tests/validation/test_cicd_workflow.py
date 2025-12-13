"""
CI/CD workflow validation tests.
"""
import pytest
from pathlib import Path

from tests.fixtures.production_fixtures import cicd_workflow_path
from tests.utils.validation_helpers import YAMLValidator


class TestCICDWorkflowValidation:
    """Test suite for .github/workflows/deploy.yml validation."""
    
    def test_workflow_exists(self, cicd_workflow_path: Path):
        """Test that deploy.yml exists."""
        assert cicd_workflow_path.exists(), \
            f"deploy.yml not found at {cicd_workflow_path}"
    
    def test_yaml_syntax(self, cicd_workflow_path: Path):
        """Test workflow has valid YAML syntax."""
        valid, error = YAMLValidator.validate_file(cicd_workflow_path)
        assert valid, f"YAML syntax error: {error}"
    
    def test_required_jobs(self, cicd_workflow_path: Path):
        """Test that all required jobs are defined."""
        workflow_data = YAMLValidator.load_file(cicd_workflow_path)
        assert workflow_data is not None, "Failed to load workflow YAML"
        
        jobs = workflow_data.get('jobs', {})
        
        required_jobs = [
            'test',
            'build-frontend',
            'build-docker',
            'deploy-production',
        ]
        
        missing_jobs = [job for job in required_jobs if job not in jobs]
        assert len(missing_jobs) == 0, \
            f"Missing required jobs: {', '.join(missing_jobs)}"
    
    def test_job_dependencies(self, cicd_workflow_path: Path):
        """Test that job dependencies are correctly configured."""
        workflow_data = YAMLValidator.load_file(cicd_workflow_path)
        jobs = workflow_data.get('jobs', {})
        
        # Check build-docker depends on test and build-frontend
        build_docker = jobs.get('build-docker', {})
        needs = build_docker.get('needs', [])
        
        assert 'test' in needs, "build-docker should depend on test"
        assert 'build-frontend' in needs, "build-docker should depend on build-frontend"
        
        # Check deploy-production depends on build-docker
        deploy = jobs.get('deploy-production', {})
        deploy_needs = deploy.get('needs', [])
        
        assert 'build-docker' in deploy_needs, \
            "deploy-production should depend on build-docker"
    
    def test_test_job_configuration(self, cicd_workflow_path: Path):
        """Test test job is properly configured."""
        workflow_data = YAMLValidator.load_file(cicd_workflow_path)
        jobs = workflow_data.get('jobs', {})
        
        test_job = jobs.get('test', {})
        assert test_job is not None, "Test job should be defined"
        
        # Check for services
        assert 'services' in test_job, "Test job should define services"
        services = test_job['services']
        assert 'postgres' in services, "Test job should include postgres service"
        assert 'redis' in services, "Test job should include redis service"
        
        # Check for steps
        assert 'steps' in test_job, "Test job should have steps"
        steps = test_job['steps']
        assert len(steps) > 0, "Test job should have at least one step"
    
    def test_docker_build_job(self, cicd_workflow_path: Path):
        """Test Docker build job configuration."""
        workflow_data = YAMLValidator.load_file(cicd_workflow_path)
        jobs = workflow_data.get('jobs', {})
        
        build_job = jobs.get('build-docker', {})
        assert build_job is not None, "build-docker job should be defined"
        
        # Check for Docker setup steps
        steps = build_job.get('steps', [])
        step_names = [step.get('name', '') for step in steps]
        
        assert any('Docker' in name for name in step_names), \
            "build-docker should have Docker setup step"
        assert any('Build' in name or 'build' in name for name in step_names), \
            "build-docker should have build step"
    
    def test_deploy_job_configuration(self, cicd_workflow_path: Path):
        """Test deployment job configuration."""
        workflow_data = YAMLValidator.load_file(cicd_workflow_path)
        jobs = workflow_data.get('jobs', {})
        
        deploy_job = jobs.get('deploy-production', {})
        assert deploy_job is not None, "deploy-production job should be defined"
        
        # Check for environment
        assert 'environment' in deploy_job, \
            "deploy-production should specify environment"
        
        # Check for kubectl setup
        steps = deploy_job.get('steps', [])
        step_names = [step.get('name', '') for step in steps]
        
        assert any('kubectl' in name.lower() for name in step_names), \
            "deploy-production should have kubectl setup step"
        assert any('Deploy' in name or 'deploy' in name for name in step_names), \
            "deploy-production should have deployment step"
    
    def test_workflow_triggers(self, cicd_workflow_path: Path):
        """Test workflow trigger configuration."""
        # Read file content directly to check for triggers
        with open(cicd_workflow_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for trigger configuration
        assert 'on:' in content, "Workflow should have 'on:' trigger configuration"
        assert 'push:' in content, "Workflow should trigger on push"
        assert 'pull_request:' in content or 'pull-request:' in content, \
            "Workflow should trigger on pull_request"
        
        # Also try to parse YAML (optional check)
        workflow_data = YAMLValidator.load_file(cicd_workflow_path)
        if workflow_data:
            on = workflow_data.get('on', {})
            if isinstance(on, dict):
                # Check for push trigger
                if 'push' in on:
                    push = on['push']
                    if isinstance(push, dict):
                        assert 'branches' in push, "Push trigger should specify branches"
                
                # Check for pull_request trigger (if YAML parsed correctly)
                if 'pull_request' not in on:
                    # If YAML parsing didn't work, we already checked the file content above
                    pass
    
    def test_environment_variables(self, cicd_workflow_path: Path):
        """Test environment variables are defined."""
        workflow_data = YAMLValidator.load_file(cicd_workflow_path)
        
        env = workflow_data.get('env', {})
        assert 'REGISTRY' in env, "Workflow should define REGISTRY env var"
        assert 'IMAGE_NAME' in env, "Workflow should define IMAGE_NAME env var"

