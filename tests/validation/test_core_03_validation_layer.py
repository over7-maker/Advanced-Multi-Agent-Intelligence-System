"""
Validation tests for Core-3: Validation Layer workflow
35 tests covering all validation functionality
"""

import pytest
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil


class TestValidationLayerWorkflow:
    """Validation test suite for Core-3: Validation Layer workflow"""
    
    @pytest.fixture
    def workflow_file(self):
        """Load the workflow YAML file"""
        workflow_path = Path('.github/workflows/core-03-validation-layer.yml')
        if workflow_path.exists():
            with open(workflow_path) as f:
                return yaml.safe_load(f)
        return None
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)
    
    # Test 1-7: Workflow Structure
    def test_workflow_exists(self, workflow_file):
        """Test 1: Verify workflow file exists"""
        assert workflow_file is not None, "Workflow file should exist"
    
    def test_workflow_has_correct_name(self, workflow_file):
        """Test 2: Verify workflow name"""
        assert 'name' in workflow_file
        assert 'Core-3: Validation Layer' in workflow_file['name']
    
    def test_workflow_has_pull_request_trigger(self, workflow_file):
        """Test 3: Verify pull_request trigger"""
        assert 'pull_request' in workflow_file['on']
        assert 'types' in workflow_file['on']['pull_request']
    
    def test_workflow_has_push_trigger(self, workflow_file):
        """Test 4: Verify push trigger"""
        assert 'push' in workflow_file['on']
        assert 'branches' in workflow_file['on']['push']
    
    def test_workflow_has_workflow_dispatch(self, workflow_file):
        """Test 5: Verify workflow_dispatch trigger"""
        assert 'workflow_dispatch' in workflow_file['on']
    
    def test_workflow_has_validation_mode_input(self, workflow_file):
        """Test 6: Verify validation_mode input"""
        inputs = workflow_file['on']['workflow_dispatch']['inputs']
        assert 'validation_mode' in inputs
        assert inputs['validation_mode']['default'] == 'comprehensive'
    
    def test_workflow_has_strict_mode_input(self, workflow_file):
        """Test 7: Verify strict_mode input"""
        inputs = workflow_file['on']['workflow_dispatch']['inputs']
        assert 'strict_mode' in inputs
        assert inputs['strict_mode']['type'] == 'boolean'
    
    # Test 8-14: Environment Variables
    def test_workflow_has_python_version_env(self, workflow_file):
        """Test 8: Verify PYTHON_VERSION env var"""
        assert 'PYTHON_VERSION' in workflow_file['env']
        assert workflow_file['env']['PYTHON_VERSION'] == '3.11'
    
    def test_workflow_has_node_version_env(self, workflow_file):
        """Test 9: Verify NODE_VERSION env var"""
        assert 'NODE_VERSION' in workflow_file['env']
        assert workflow_file['env']['NODE_VERSION'] == '20'
    
    def test_workflow_has_validation_mode_env(self, workflow_file):
        """Test 10: Verify VALIDATION_MODE env var"""
        assert 'VALIDATION_MODE' in workflow_file['env']
    
    def test_workflow_has_strict_mode_env(self, workflow_file):
        """Test 11: Verify STRICT_MODE env var"""
        assert 'STRICT_MODE' in workflow_file['env']
    
    # Test 12-18: Job Structure
    def test_workflow_has_workflow_validation_job(self, workflow_file):
        """Test 12: Verify workflow_validation job exists"""
        assert 'workflow_validation' in workflow_file['jobs']
    
    def test_workflow_has_code_quality_validation_job(self, workflow_file):
        """Test 13: Verify code_quality_validation job exists"""
        assert 'code_quality_validation' in workflow_file['jobs']
    
    def test_workflow_has_security_validation_job(self, workflow_file):
        """Test 14: Verify security_validation job exists"""
        assert 'security_validation' in workflow_file['jobs']
    
    def test_workflow_has_web_validation_job(self, workflow_file):
        """Test 15: Verify web_validation job exists"""
        assert 'web_validation' in workflow_file['jobs']
    
    def test_workflow_has_architecture_validation_job(self, workflow_file):
        """Test 16: Verify architecture_validation job exists"""
        assert 'architecture_validation' in workflow_file['jobs']
    
    def test_workflow_has_validation_summary_job(self, workflow_file):
        """Test 17: Verify validation_summary job exists"""
        assert 'validation_summary' in workflow_file['jobs']
    
    def test_validation_summary_depends_on_all_jobs(self, workflow_file):
        """Test 18: Verify validation_summary depends on all validation jobs"""
        job = workflow_file['jobs']['validation_summary']
        assert 'needs' in job
        assert len(job['needs']) >= 5
    
    # Test 19-25: Job Configuration
    def test_workflow_validation_has_timeout(self, workflow_file):
        """Test 19: Verify workflow_validation has timeout"""
        job = workflow_file['jobs']['workflow_validation']
        assert 'timeout-minutes' in job
        assert job['timeout-minutes'] == 15
    
    def test_code_quality_has_timeout(self, workflow_file):
        """Test 20: Verify code_quality_validation has timeout"""
        job = workflow_file['jobs']['code_quality_validation']
        assert 'timeout-minutes' in job
        assert job['timeout-minutes'] == 20
    
    def test_security_validation_has_timeout(self, workflow_file):
        """Test 21: Verify security_validation has timeout"""
        job = workflow_file['jobs']['security_validation']
        assert 'timeout-minutes' in job
        assert job['timeout-minutes'] == 15
    
    def test_web_validation_has_timeout(self, workflow_file):
        """Test 22: Verify web_validation has timeout"""
        job = workflow_file['jobs']['web_validation']
        assert 'timeout-minutes' in job
        assert job['timeout-minutes'] == 20
    
    def test_architecture_validation_has_timeout(self, workflow_file):
        """Test 23: Verify architecture_validation has timeout"""
        job = workflow_file['jobs']['architecture_validation']
        assert 'timeout-minutes' in job
        assert job['timeout-minutes'] == 10
    
    def test_code_quality_has_permissions(self, workflow_file):
        """Test 24: Verify code_quality_validation has permissions"""
        job = workflow_file['jobs']['code_quality_validation']
        assert 'permissions' in job
        assert 'pull-requests' in job['permissions']
    
    def test_web_validation_has_concurrency(self, workflow_file):
        """Test 25: Verify web_validation has concurrency"""
        job = workflow_file['jobs']['web_validation']
        assert 'concurrency' in job
    
    # Test 26-30: Step Validation
    def test_workflow_validation_has_actionlint_step(self, workflow_file):
        """Test 26: Verify workflow_validation has actionlint step"""
        job = workflow_file['jobs']['workflow_validation']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('actionlint' in s.lower() for s in steps)
    
    def test_workflow_validation_has_yaml_validation_step(self, workflow_file):
        """Test 27: Verify workflow_validation has YAML validation step"""
        job = workflow_file['jobs']['workflow_validation']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('yaml' in s.lower() for s in steps)
    
    def test_code_quality_has_formatting_step(self, workflow_file):
        """Test 28: Verify code_quality_validation has formatting step"""
        job = workflow_file['jobs']['code_quality_validation']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('formatting' in s.lower() for s in steps)
    
    def test_code_quality_has_linting_step(self, workflow_file):
        """Test 29: Verify code_quality_validation has linting step"""
        job = workflow_file['jobs']['code_quality_validation']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('lint' in s.lower() for s in steps)
    
    def test_security_validation_has_safety_step(self, workflow_file):
        """Test 30: Verify security_validation has safety step"""
        job = workflow_file['jobs']['security_validation']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('safety' in s.lower() for s in steps)
    
    # Test 31-35: Artifact & Integration
    def test_workflow_validation_uploads_artifacts(self, workflow_file):
        """Test 31: Verify workflow_validation uploads artifacts"""
        job = workflow_file['jobs']['workflow_validation']
        steps = job['steps']
        upload_steps = [s for s in steps if s.get('uses', '').startswith('actions/upload-artifact')]
        assert len(upload_steps) > 0
    
    def test_code_quality_uploads_artifacts(self, workflow_file):
        """Test 32: Verify code_quality_validation uploads artifacts"""
        job = workflow_file['jobs']['code_quality_validation']
        steps = job['steps']
        upload_steps = [s for s in steps if s.get('uses', '').startswith('actions/upload-artifact')]
        assert len(upload_steps) > 0
    
    def test_security_validation_uploads_artifacts(self, workflow_file):
        """Test 33: Verify security_validation uploads artifacts"""
        job = workflow_file['jobs']['security_validation']
        steps = job['steps']
        upload_steps = [s for s in steps if s.get('uses', '').startswith('actions/upload-artifact')]
        assert len(upload_steps) > 0
    
    def test_validation_summary_downloads_artifacts(self, workflow_file):
        """Test 34: Verify validation_summary downloads artifacts"""
        job = workflow_file['jobs']['validation_summary']
        steps = job['steps']
        download_steps = [s for s in steps if s.get('uses', '').startswith('actions/download-artifact')]
        assert len(download_steps) > 0
    
    def test_validation_summary_creates_comment(self, workflow_file):
        """Test 35: Verify validation_summary creates PR comment"""
        job = workflow_file['jobs']['validation_summary']
        steps = job['steps']
        comment_steps = [s for s in steps if 'comment' in s.get('name', '').lower()]
        assert len(comment_steps) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

