"""
Integration tests for Core-2: Processing Engine workflow
50 tests covering all functionality and integrations
"""

import pytest
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import tempfile
import shutil
import asyncio


class TestProcessingEngineWorkflow:
    """Integration test suite for Core-2: Processing Engine workflow"""
    
    @pytest.fixture
    def workflow_file(self):
        """Load the workflow YAML file"""
        workflow_path = Path('.github/workflows/core-02-processing-engine.yml')
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
    
    # Test 1-10: Workflow Structure & Configuration
    def test_workflow_exists(self, workflow_file):
        """Test 1: Verify workflow file exists"""
        assert workflow_file is not None, "Workflow file should exist"
    
    def test_workflow_has_correct_name(self, workflow_file):
        """Test 2: Verify workflow name"""
        assert 'name' in workflow_file
        assert 'Core-2: Processing Engine' in workflow_file['name']
    
    def test_workflow_has_all_trigger_types(self, workflow_file):
        """Test 3: Verify workflow has all trigger types"""
        triggers = workflow_file['on']
        assert 'push' in triggers
        assert 'pull_request' in triggers
        assert 'issues' in triggers
        assert 'issue_comment' in triggers
        assert 'schedule' in triggers
        assert 'workflow_dispatch' in triggers
    
    def test_workflow_has_processing_mode_input(self, workflow_file):
        """Test 4: Verify processing_mode input"""
        inputs = workflow_file['on']['workflow_dispatch']['inputs']
        assert 'processing_mode' in inputs
        assert inputs['processing_mode']['default'] == 'intelligent'
    
    def test_workflow_has_improvement_mode_input(self, workflow_file):
        """Test 5: Verify improvement_mode input"""
        inputs = workflow_file['on']['workflow_dispatch']['inputs']
        assert 'improvement_mode' in inputs
    
    def test_workflow_has_response_mode_input(self, workflow_file):
        """Test 6: Verify response_mode input"""
        inputs = workflow_file['on']['workflow_dispatch']['inputs']
        assert 'response_mode' in inputs
    
    def test_workflow_has_audit_mode_input(self, workflow_file):
        """Test 7: Verify audit_mode input"""
        inputs = workflow_file['on']['workflow_dispatch']['inputs']
        assert 'audit_mode' in inputs
    
    def test_workflow_has_python_version_env(self, workflow_file):
        """Test 8: Verify PYTHON_VERSION env var"""
        assert 'PYTHON_VERSION' in workflow_file['env']
        assert workflow_file['env']['PYTHON_VERSION'] == '3.11'
    
    def test_workflow_has_node_version_env(self, workflow_file):
        """Test 9: Verify NODE_VERSION env var"""
        assert 'NODE_VERSION' in workflow_file['env']
        assert workflow_file['env']['NODE_VERSION'] == '20'
    
    def test_workflow_has_processing_mode_env(self, workflow_file):
        """Test 10: Verify PROCESSING_MODE env var"""
        assert 'PROCESSING_MODE' in workflow_file['env']
    
    # Test 11-20: Job Structure
    def test_workflow_has_ai_project_analysis_job(self, workflow_file):
        """Test 11: Verify ai-project-analysis job exists"""
        assert 'ai-project-analysis' in workflow_file['jobs']
    
    def test_workflow_has_project_analysis_learning_job(self, workflow_file):
        """Test 12: Verify project_analysis_learning job exists"""
        assert 'project_analysis_learning' in workflow_file['jobs']
    
    def test_workflow_has_ai_issue_analysis_job(self, workflow_file):
        """Test 13: Verify ai-issue-analysis job exists"""
        assert 'ai-issue-analysis' in workflow_file['jobs']
    
    def test_workflow_has_issue_analysis_categorization_job(self, workflow_file):
        """Test 14: Verify issue_analysis_categorization job exists"""
        assert 'issue_analysis_categorization' in workflow_file['jobs']
    
    def test_workflow_has_pr_analysis_processing_job(self, workflow_file):
        """Test 15: Verify pr_analysis_processing job exists"""
        assert 'pr_analysis_processing' in workflow_file['jobs']
    
    def test_workflow_has_audit_processing_job(self, workflow_file):
        """Test 16: Verify audit_processing job exists"""
        assert 'audit_processing' in workflow_file['jobs']
    
    def test_workflow_has_hardened_analysis_job(self, workflow_file):
        """Test 17: Verify hardened_analysis job exists"""
        assert 'hardened_analysis' in workflow_file['jobs']
    
    def test_workflow_has_processing_summary_job(self, workflow_file):
        """Test 18: Verify processing_summary job exists"""
        assert 'processing_summary' in workflow_file['jobs']
    
    def test_ai_project_analysis_uses_orchestrator(self, workflow_file):
        """Test 19: Verify ai-project-analysis uses orchestrator"""
        job = workflow_file['jobs']['ai-project-analysis']
        assert 'uses' in job
        assert '00-zero-failure-ai-orchestrator.yml' in job['uses']
    
    def test_ai_issue_analysis_uses_orchestrator(self, workflow_file):
        """Test 20: Verify ai-issue-analysis uses orchestrator"""
        job = workflow_file['jobs']['ai-issue-analysis']
        assert 'uses' in job
        assert '00-zero-failure-ai-orchestrator.yml' in job['uses']
    
    # Test 21-30: Job Dependencies
    def test_project_analysis_depends_on_ai_analysis(self, workflow_file):
        """Test 21: Verify project_analysis_learning depends on ai-project-analysis"""
        job = workflow_file['jobs']['project_analysis_learning']
        assert 'needs' in job
        assert 'ai-project-analysis' in job['needs']
    
    def test_issue_analysis_depends_on_ai_issue_analysis(self, workflow_file):
        """Test 22: Verify issue_analysis_categorization depends on ai-issue-analysis"""
        job = workflow_file['jobs']['issue_analysis_categorization']
        assert 'needs' in job
        assert 'ai-issue-analysis' in job['needs']
    
    def test_processing_summary_depends_on_all_jobs(self, workflow_file):
        """Test 23: Verify processing_summary depends on all processing jobs"""
        job = workflow_file['jobs']['processing_summary']
        assert 'needs' in job
        assert len(job['needs']) >= 5
    
    def test_project_analysis_has_timeout(self, workflow_file):
        """Test 24: Verify project_analysis_learning has timeout"""
        job = workflow_file['jobs']['project_analysis_learning']
        assert 'timeout-minutes' in job
        assert job['timeout-minutes'] == 45
    
    def test_issue_analysis_has_timeout(self, workflow_file):
        """Test 25: Verify issue_analysis_categorization has timeout"""
        job = workflow_file['jobs']['issue_analysis_categorization']
        assert 'timeout-minutes' in job
        assert job['timeout-minutes'] == 20
    
    def test_pr_analysis_has_timeout(self, workflow_file):
        """Test 26: Verify pr_analysis_processing has timeout"""
        job = workflow_file['jobs']['pr_analysis_processing']
        assert 'timeout-minutes' in job
        assert job['timeout-minutes'] == 30
    
    def test_audit_processing_has_timeout(self, workflow_file):
        """Test 27: Verify audit_processing has timeout"""
        job = workflow_file['jobs']['audit_processing']
        assert 'timeout-minutes' in job
        assert job['timeout-minutes'] == 30
    
    def test_hardened_analysis_has_timeout(self, workflow_file):
        """Test 28: Verify hardened_analysis has timeout"""
        job = workflow_file['jobs']['hardened_analysis']
        assert 'timeout-minutes' in job
        assert job['timeout-minutes'] == 20
    
    def test_pr_analysis_has_permissions(self, workflow_file):
        """Test 29: Verify pr_analysis_processing has permissions"""
        job = workflow_file['jobs']['pr_analysis_processing']
        assert 'permissions' in job
        assert 'pull-requests' in job['permissions']
        assert job['permissions']['pull-requests'] == 'write'
    
    def test_hardened_analysis_has_permissions(self, workflow_file):
        """Test 30: Verify hardened_analysis has permissions"""
        job = workflow_file['jobs']['hardened_analysis']
        assert 'permissions' in job
        assert 'pull-requests' in job['permissions']
    
    # Test 31-40: Step Configuration
    def test_project_analysis_has_checkout_step(self, workflow_file):
        """Test 31: Verify project_analysis_learning has checkout step"""
        job = workflow_file['jobs']['project_analysis_learning']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('Checkout' in s for s in steps)
    
    def test_project_analysis_has_python_setup(self, workflow_file):
        """Test 32: Verify project_analysis_learning has Python setup"""
        job = workflow_file['jobs']['project_analysis_learning']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('Python' in s for s in steps)
    
    def test_issue_analysis_has_checkout_step(self, workflow_file):
        """Test 33: Verify issue_analysis_categorization has checkout step"""
        job = workflow_file['jobs']['issue_analysis_categorization']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('Checkout' in s for s in steps)
    
    def test_pr_analysis_has_checkout_step(self, workflow_file):
        """Test 34: Verify pr_analysis_processing has checkout step"""
        job = workflow_file['jobs']['pr_analysis_processing']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('Checkout' in s for s in steps)
    
    def test_audit_processing_has_checkout_step(self, workflow_file):
        """Test 35: Verify audit_processing has checkout step"""
        job = workflow_file['jobs']['audit_processing']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('Checkout' in s for s in steps)
    
    def test_hardened_analysis_has_checkout_step(self, workflow_file):
        """Test 36: Verify hardened_analysis has checkout step"""
        job = workflow_file['jobs']['hardened_analysis']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('Checkout' in s for s in steps)
    
    def test_project_analysis_has_analysis_step(self, workflow_file):
        """Test 37: Verify project_analysis_learning has analysis step"""
        job = workflow_file['jobs']['project_analysis_learning']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('analysis' in s.lower() for s in steps)
    
    def test_issue_analysis_has_analysis_step(self, workflow_file):
        """Test 38: Verify issue_analysis_categorization has analysis step"""
        job = workflow_file['jobs']['issue_analysis_categorization']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('analysis' in s.lower() for s in steps)
    
    def test_pr_analysis_has_pr_analysis_step(self, workflow_file):
        """Test 39: Verify pr_analysis_processing has PR analysis step"""
        job = workflow_file['jobs']['pr_analysis_processing']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('pr' in s.lower() or 'analysis' in s.lower() for s in steps)
    
    def test_hardened_analysis_has_validation_step(self, workflow_file):
        """Test 40: Verify hardened_analysis has validation step"""
        job = workflow_file['jobs']['hardened_analysis']
        steps = [s.get('name', '') for s in job['steps']]
        assert any('validate' in s.lower() or 'syntax' in s.lower() for s in steps)
    
    # Test 41-50: Artifact & Integration
    def test_project_analysis_uploads_artifacts(self, workflow_file):
        """Test 41: Verify project_analysis_learning uploads artifacts"""
        job = workflow_file['jobs']['project_analysis_learning']
        steps = job['steps']
        upload_steps = [s for s in steps if s.get('uses', '').startswith('actions/upload-artifact')]
        assert len(upload_steps) > 0
    
    def test_issue_analysis_uploads_artifacts(self, workflow_file):
        """Test 42: Verify issue_analysis_categorization uploads artifacts"""
        job = workflow_file['jobs']['issue_analysis_categorization']
        steps = job['steps']
        upload_steps = [s for s in steps if s.get('uses', '').startswith('actions/upload-artifact')]
        assert len(upload_steps) > 0
    
    def test_pr_analysis_uploads_artifacts(self, workflow_file):
        """Test 43: Verify pr_analysis_processing uploads artifacts"""
        job = workflow_file['jobs']['pr_analysis_processing']
        steps = job['steps']
        upload_steps = [s for s in steps if s.get('uses', '').startswith('actions/upload-artifact')]
        assert len(upload_steps) > 0
    
    def test_audit_processing_uploads_artifacts(self, workflow_file):
        """Test 44: Verify audit_processing uploads artifacts"""
        job = workflow_file['jobs']['audit_processing']
        steps = job['steps']
        upload_steps = [s for s in steps if s.get('uses', '').startswith('actions/upload-artifact')]
        assert len(upload_steps) > 0
    
    def test_hardened_analysis_uploads_artifacts(self, workflow_file):
        """Test 45: Verify hardened_analysis uploads artifacts"""
        job = workflow_file['jobs']['hardened_analysis']
        steps = job['steps']
        upload_steps = [s for s in steps if s.get('uses', '').startswith('actions/upload-artifact')]
        assert len(upload_steps) > 0
    
    def test_processing_summary_downloads_artifacts(self, workflow_file):
        """Test 46: Verify processing_summary downloads artifacts"""
        job = workflow_file['jobs']['processing_summary']
        steps = job['steps']
        download_steps = [s for s in steps if s.get('uses', '').startswith('actions/download-artifact')]
        assert len(download_steps) > 0
    
    def test_processing_summary_creates_comment(self, workflow_file):
        """Test 47: Verify processing_summary creates PR comment"""
        job = workflow_file['jobs']['processing_summary']
        steps = job['steps']
        comment_steps = [s for s in steps if 'comment' in s.get('name', '').lower()]
        assert len(comment_steps) > 0
    
    def test_all_jobs_have_conditional_logic(self, workflow_file):
        """Test 48: Verify all jobs have conditional logic"""
        jobs = workflow_file['jobs']
        for job_name, job in jobs.items():
            if job_name not in ['processing_summary']:  # Summary always runs
                assert 'if' in job, f"Job {job_name} should have conditional logic"
    
    def test_orchestrator_jobs_have_secrets(self, workflow_file):
        """Test 49: Verify orchestrator jobs inherit secrets"""
        job = workflow_file['jobs']['ai-project-analysis']
        assert 'secrets' in job
        assert job['secrets'] == 'inherit'
    
    def test_orchestrator_jobs_continue_on_error(self, workflow_file):
        """Test 50: Verify orchestrator jobs continue on error"""
        job = workflow_file['jobs']['ai-project-analysis']
        assert 'continue-on-error' in job
        assert job['continue-on-error'] == True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

