"""
Unit tests for Core-1: Data Pipeline workflow
42 tests covering all functionality
"""

import pytest
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil


class TestDataPipelineWorkflow:
    """Test suite for Core-1: Data Pipeline workflow"""
    
    @pytest.fixture
    def workflow_file(self):
        """Load the workflow YAML file"""
        workflow_path = Path('.github/workflows/core-01-data-pipeline.yml')
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
    
    # Test 1-5: Workflow Structure
    def test_workflow_exists(self, workflow_file):
        """Test 1: Verify workflow file exists"""
        assert workflow_file is not None, "Workflow file should exist"
    
    def test_workflow_has_name(self, workflow_file):
        """Test 2: Verify workflow has a name"""
        assert 'name' in workflow_file, "Workflow should have a name"
        assert 'Core-1: Data Pipeline' in workflow_file['name']
    
    def test_workflow_has_on_triggers(self, workflow_file):
        """Test 3: Verify workflow has trigger definitions"""
        assert 'on' in workflow_file, "Workflow should have trigger definitions"
    
    def test_workflow_has_schedule(self, workflow_file):
        """Test 4: Verify workflow has schedule triggers"""
        assert 'schedule' in workflow_file['on'], "Workflow should have schedule triggers"
        assert len(workflow_file['on']['schedule']) >= 1
    
    def test_workflow_has_workflow_dispatch(self, workflow_file):
        """Test 5: Verify workflow has manual dispatch"""
        assert 'workflow_dispatch' in workflow_file['on'], "Workflow should support manual dispatch"
    
    # Test 6-10: Input Parameters
    def test_workflow_has_pipeline_mode_input(self, workflow_file):
        """Test 6: Verify pipeline_mode input exists"""
        inputs = workflow_file['on']['workflow_dispatch']['inputs']
        assert 'pipeline_mode' in inputs, "Should have pipeline_mode input"
        assert inputs['pipeline_mode']['default'] == 'comprehensive'
    
    def test_workflow_has_audit_type_input(self, workflow_file):
        """Test 7: Verify audit_type input exists"""
        inputs = workflow_file['on']['workflow_dispatch']['inputs']
        assert 'audit_type' in inputs, "Should have audit_type input"
    
    def test_workflow_has_build_mode_input(self, workflow_file):
        """Test 8: Verify build_mode input exists"""
        inputs = workflow_file['on']['workflow_dispatch']['inputs']
        assert 'build_mode' in inputs, "Should have build_mode input"
    
    def test_workflow_has_version_strategy_input(self, workflow_file):
        """Test 9: Verify version_strategy input exists"""
        inputs = workflow_file['on']['workflow_dispatch']['inputs']
        assert 'version_strategy' in inputs, "Should have version_strategy input"
    
    def test_workflow_has_package_format_input(self, workflow_file):
        """Test 10: Verify package_format input exists"""
        inputs = workflow_file['on']['workflow_dispatch']['inputs']
        assert 'package_format' in inputs, "Should have package_format input"
    
    # Test 11-15: Environment Variables
    def test_workflow_has_env_section(self, workflow_file):
        """Test 11: Verify workflow has environment variables"""
        assert 'env' in workflow_file, "Workflow should have environment variables"
    
    def test_workflow_has_python_version(self, workflow_file):
        """Test 12: Verify Python version is set"""
        assert 'PYTHON_VERSION' in workflow_file['env'], "Should set PYTHON_VERSION"
        assert workflow_file['env']['PYTHON_VERSION'] == '3.11'
    
    def test_workflow_has_pipeline_mode_env(self, workflow_file):
        """Test 13: Verify PIPELINE_MODE env var"""
        assert 'PIPELINE_MODE' in workflow_file['env'], "Should set PIPELINE_MODE"
    
    def test_workflow_has_audit_type_env(self, workflow_file):
        """Test 14: Verify AUDIT_TYPE env var"""
        assert 'AUDIT_TYPE' in workflow_file['env'], "Should set AUDIT_TYPE"
    
    def test_workflow_has_build_mode_env(self, workflow_file):
        """Test 15: Verify BUILD_MODE env var"""
        assert 'BUILD_MODE' in workflow_file['env'], "Should set BUILD_MODE"
    
    # Test 16-20: Jobs Structure
    def test_workflow_has_jobs(self, workflow_file):
        """Test 16: Verify workflow has jobs section"""
        assert 'jobs' in workflow_file, "Workflow should have jobs"
    
    def test_workflow_has_data_backup_job(self, workflow_file):
        """Test 17: Verify data_backup_integrity job exists"""
        assert 'data_backup_integrity' in workflow_file['jobs'], "Should have data_backup_integrity job"
    
    def test_workflow_has_comprehensive_audit_job(self, workflow_file):
        """Test 18: Verify comprehensive_audit job exists"""
        assert 'comprehensive_audit' in workflow_file['jobs'], "Should have comprehensive_audit job"
    
    def test_workflow_has_project_audit_job(self, workflow_file):
        """Test 19: Verify project_audit job exists"""
        assert 'project_audit' in workflow_file['jobs'], "Should have project_audit job"
    
    def test_workflow_has_workflow_audit_job(self, workflow_file):
        """Test 20: Verify workflow_audit job exists"""
        assert 'workflow_audit' in workflow_file['jobs'], "Should have workflow_audit job"
    
    # Test 21-25: Job Configuration
    def test_data_backup_job_has_timeout(self, workflow_file):
        """Test 21: Verify data_backup_integrity has timeout"""
        job = workflow_file['jobs']['data_backup_integrity']
        assert 'timeout-minutes' in job, "Job should have timeout"
        assert job['timeout-minutes'] == 15
    
    def test_comprehensive_audit_job_has_timeout(self, workflow_file):
        """Test 22: Verify comprehensive_audit has timeout"""
        job = workflow_file['jobs']['comprehensive_audit']
        assert 'timeout-minutes' in job, "Job should have timeout"
        assert job['timeout-minutes'] == 30
    
    def test_project_audit_job_has_timeout(self, workflow_file):
        """Test 23: Verify project_audit has timeout"""
        job = workflow_file['jobs']['project_audit']
        assert 'timeout-minutes' in job, "Job should have timeout"
        assert job['timeout-minutes'] == 60
    
    def test_workflow_audit_job_has_timeout(self, workflow_file):
        """Test 24: Verify workflow_audit has timeout"""
        job = workflow_file['jobs']['workflow_audit']
        assert 'timeout-minutes' in job, "Job should have timeout"
        assert job['timeout-minutes'] == 30
    
    def test_version_package_build_job_has_timeout(self, workflow_file):
        """Test 25: Verify version_package_build has timeout"""
        job = workflow_file['jobs']['version_package_build']
        assert 'timeout-minutes' in job, "Job should have timeout"
        assert job['timeout-minutes'] == 45
    
    # Test 26-30: Job Steps
    def test_data_backup_has_checkout_step(self, workflow_file):
        """Test 26: Verify data_backup has checkout step"""
        job = workflow_file['jobs']['data_backup_integrity']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('Checkout' in s for s in steps), "Should have checkout step"
    
    def test_data_backup_has_python_setup(self, workflow_file):
        """Test 27: Verify data_backup has Python setup"""
        job = workflow_file['jobs']['data_backup_integrity']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('Python' in s for s in steps), "Should have Python setup step"
    
    def test_comprehensive_audit_has_audit_step(self, workflow_file):
        """Test 28: Verify comprehensive_audit has audit step"""
        job = workflow_file['jobs']['comprehensive_audit']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('audit' in s.lower() for s in steps), "Should have audit step"
    
    def test_project_audit_has_documentation_step(self, workflow_file):
        """Test 29: Verify project_audit has documentation step"""
        job = workflow_file['jobs']['project_audit']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('documentation' in s.lower() for s in steps), "Should have documentation step"
    
    def test_version_build_has_build_step(self, workflow_file):
        """Test 30: Verify version_package_build has build step"""
        job = workflow_file['jobs']['version_package_build']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('build' in s.lower() for s in steps), "Should have build step"
    
    # Test 31-35: Artifact Uploads
    def test_comprehensive_audit_uploads_artifacts(self, workflow_file):
        """Test 31: Verify comprehensive_audit uploads artifacts"""
        job = workflow_file['jobs']['comprehensive_audit']
        steps = job['steps']
        upload_steps = [s for s in steps if s.get('uses', '').startswith('actions/upload-artifact')]
        assert len(upload_steps) > 0, "Should upload artifacts"
    
    def test_project_audit_uploads_artifacts(self, workflow_file):
        """Test 32: Verify project_audit uploads artifacts"""
        job = workflow_file['jobs']['project_audit']
        steps = job['steps']
        upload_steps = [s for s in steps if s.get('uses', '').startswith('actions/upload-artifact')]
        assert len(upload_steps) > 0, "Should upload artifacts"
    
    def test_workflow_audit_uploads_artifacts(self, workflow_file):
        """Test 33: Verify workflow_audit uploads artifacts"""
        job = workflow_file['jobs']['workflow_audit']
        steps = job['steps']
        upload_steps = [s for s in steps if s.get('uses', '').startswith('actions/upload-artifact')]
        assert len(upload_steps) > 0, "Should upload artifacts"
    
    def test_version_build_uploads_artifacts(self, workflow_file):
        """Test 34: Verify version_package_build uploads artifacts"""
        job = workflow_file['jobs']['version_package_build']
        steps = job['steps']
        upload_steps = [s for s in steps if s.get('uses', '').startswith('actions/upload-artifact')]
        assert len(upload_steps) > 0, "Should upload artifacts"
    
    def test_data_validation_uploads_artifacts(self, workflow_file):
        """Test 35: Verify data_validation uploads artifacts"""
        job = workflow_file['jobs']['data_validation']
        steps = job['steps']
        upload_steps = [s for s in steps if s.get('uses', '').startswith('actions/upload-artifact')]
        assert len(upload_steps) > 0, "Should upload artifacts"
    
    # Test 36-40: Conditional Logic
    def test_data_backup_has_conditional(self, workflow_file):
        """Test 36: Verify data_backup has conditional logic"""
        job = workflow_file['jobs']['data_backup_integrity']
        assert 'if' in job, "Job should have conditional logic"
    
    def test_comprehensive_audit_has_conditional(self, workflow_file):
        """Test 37: Verify comprehensive_audit has conditional logic"""
        job = workflow_file['jobs']['comprehensive_audit']
        assert 'if' in job, "Job should have conditional logic"
    
    def test_project_audit_has_conditional(self, workflow_file):
        """Test 38: Verify project_audit has conditional logic"""
        job = workflow_file['jobs']['project_audit']
        assert 'if' in job, "Job should have conditional logic"
    
    def test_workflow_audit_has_conditional(self, workflow_file):
        """Test 39: Verify workflow_audit has conditional logic"""
        job = workflow_file['jobs']['workflow_audit']
        assert 'if' in job, "Job should have conditional logic"
    
    def test_version_build_has_conditional(self, workflow_file):
        """Test 40: Verify version_package_build has conditional logic"""
        job = workflow_file['jobs']['version_package_build']
        assert 'if' in job, "Job should have conditional logic"
    
    # Test 41-42: Summary Job
    def test_pipeline_summary_job_exists(self, workflow_file):
        """Test 41: Verify pipeline_summary job exists"""
        assert 'pipeline_summary' in workflow_file['jobs'], "Should have pipeline_summary job"
    
    def test_pipeline_summary_has_dependencies(self, workflow_file):
        """Test 42: Verify pipeline_summary depends on other jobs"""
        job = workflow_file['jobs']['pipeline_summary']
        assert 'needs' in job, "Summary job should depend on other jobs"
        assert len(job['needs']) >= 5, "Should depend on multiple jobs"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

