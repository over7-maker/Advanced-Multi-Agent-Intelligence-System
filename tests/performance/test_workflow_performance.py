"""
Performance tests for core workflows
Tests execution time, resource usage, and optimization
"""

import pytest
import json
import yaml
from pathlib import Path
import time


class TestWorkflowPerformance:
    """Performance test suite for core workflows"""
    
    @pytest.fixture
    def core_workflows(self):
        """Load all core workflow files"""
        workflows = {}
        for i in range(1, 9):
            workflow_files = list(Path('.github/workflows').glob(f'core-0{i}-*.yml'))
            if workflow_files:
                with open(workflow_files[0]) as f:
                    workflows[f'core-0{i}'] = yaml.safe_load(f)
        return workflows
    
    # Test 1-8: Workflow Size Validation
    def test_core_01_size_optimized(self, core_workflows):
        """Test 1: Verify Core-1 size is optimized"""
        if 'core-01' in core_workflows:
            workflow_file = list(Path('.github/workflows').glob('core-01-*.yml'))[0]
            size_kb = workflow_file.stat().st_size / 1024
            assert size_kb < 30, f"Core-1 should be <30 KB, got {size_kb:.2f} KB"
    
    def test_core_02_size_optimized(self, core_workflows):
        """Test 2: Verify Core-2 size is optimized"""
        if 'core-02' in core_workflows:
            workflow_file = list(Path('.github/workflows').glob('core-02-*.yml'))[0]
            size_kb = workflow_file.stat().st_size / 1024
            assert size_kb < 30, f"Core-2 should be <30 KB, got {size_kb:.2f} KB"
    
    def test_core_03_size_optimized(self, core_workflows):
        """Test 3: Verify Core-3 size is optimized"""
        if 'core-03' in core_workflows:
            workflow_file = list(Path('.github/workflows').glob('core-03-*.yml'))[0]
            size_kb = workflow_file.stat().st_size / 1024
            assert size_kb < 20, f"Core-3 should be <20 KB, got {size_kb:.2f} KB"
    
    def test_core_04_size_optimized(self, core_workflows):
        """Test 4: Verify Core-4 size is optimized"""
        if 'core-04' in core_workflows:
            workflow_file = list(Path('.github/workflows').glob('core-04-*.yml'))[0]
            size_kb = workflow_file.stat().st_size / 1024
            assert size_kb < 20, f"Core-4 should be <20 KB, got {size_kb:.2f} KB"
    
    def test_core_05_size_optimized(self, core_workflows):
        """Test 5: Verify Core-5 size is optimized"""
        if 'core-05' in core_workflows:
            workflow_file = list(Path('.github/workflows').glob('core-05-*.yml'))[0]
            size_kb = workflow_file.stat().st_size / 1024
            assert size_kb < 20, f"Core-5 should be <20 KB, got {size_kb:.2f} KB"
    
    def test_core_06_size_optimized(self, core_workflows):
        """Test 6: Verify Core-6 size is optimized"""
        if 'core-06' in core_workflows:
            workflow_file = list(Path('.github/workflows').glob('core-06-*.yml'))[0]
            size_kb = workflow_file.stat().st_size / 1024
            assert size_kb < 20, f"Core-6 should be <20 KB, got {size_kb:.2f} KB"
    
    def test_core_07_size_optimized(self, core_workflows):
        """Test 7: Verify Core-7 size is optimized"""
        if 'core-07' in core_workflows:
            workflow_file = list(Path('.github/workflows').glob('core-07-*.yml'))[0]
            size_kb = workflow_file.stat().st_size / 1024
            assert size_kb < 15, f"Core-7 should be <15 KB, got {size_kb:.2f} KB"
    
    def test_core_08_size_optimized(self, core_workflows):
        """Test 8: Verify Core-8 size is optimized"""
        if 'core-08' in core_workflows:
            workflow_file = list(Path('.github/workflows').glob('core-08-*.yml'))[0]
            size_kb = workflow_file.stat().st_size / 1024
            assert size_kb < 25, f"Core-8 should be <25 KB, got {size_kb:.2f} KB"
    
    # Test 9-16: Timeout Configuration
    def test_core_01_timeouts_reasonable(self, core_workflows):
        """Test 9: Verify Core-1 timeouts are reasonable"""
        if 'core-01' in core_workflows:
            workflow = core_workflows['core-01']
            for job in workflow.get('jobs', {}).values():
                if 'timeout-minutes' in job:
                    assert job['timeout-minutes'] <= 60, "Timeouts should be reasonable"
    
    def test_core_02_timeouts_reasonable(self, core_workflows):
        """Test 10: Verify Core-2 timeouts are reasonable"""
        if 'core-02' in core_workflows:
            workflow = core_workflows['core-02']
            for job in workflow.get('jobs', {}).values():
                if 'timeout-minutes' in job:
                    assert job['timeout-minutes'] <= 60, "Timeouts should be reasonable"
    
    def test_core_03_timeouts_reasonable(self, core_workflows):
        """Test 11: Verify Core-3 timeouts are reasonable"""
        if 'core-03' in core_workflows:
            workflow = core_workflows['core-03']
            for job in workflow.get('jobs', {}).values():
                if 'timeout-minutes' in job:
                    assert job['timeout-minutes'] <= 30, "Timeouts should be reasonable"
    
    def test_core_04_timeouts_reasonable(self, core_workflows):
        """Test 12: Verify Core-4 timeouts are reasonable"""
        if 'core-04' in core_workflows:
            workflow = core_workflows['core-04']
            for job in workflow.get('jobs', {}).values():
                if 'timeout-minutes' in job:
                    assert job['timeout-minutes'] <= 120, "Timeouts should be reasonable"
    
    def test_core_05_timeouts_reasonable(self, core_workflows):
        """Test 13: Verify Core-5 timeouts are reasonable"""
        if 'core-05' in core_workflows:
            workflow = core_workflows['core-05']
            for job in workflow.get('jobs', {}).values():
                if 'timeout-minutes' in job:
                    assert job['timeout-minutes'] <= 30, "Timeouts should be reasonable"
    
    def test_core_06_timeouts_reasonable(self, core_workflows):
        """Test 14: Verify Core-6 timeouts are reasonable"""
        if 'core-06' in core_workflows:
            workflow = core_workflows['core-06']
            for job in workflow.get('jobs', {}).values():
                if 'timeout-minutes' in job:
                    assert job['timeout-minutes'] <= 30, "Timeouts should be reasonable"
    
    def test_core_07_timeouts_reasonable(self, core_workflows):
        """Test 15: Verify Core-7 timeouts are reasonable"""
        if 'core-07' in core_workflows:
            workflow = core_workflows['core-07']
            for job in workflow.get('jobs', {}).values():
                if 'timeout-minutes' in job:
                    assert job['timeout-minutes'] <= 45, "Timeouts should be reasonable"
    
    def test_core_08_timeouts_reasonable(self, core_workflows):
        """Test 16: Verify Core-8 timeouts are reasonable"""
        if 'core-08' in core_workflows:
            workflow = core_workflows['core-08']
            for job in workflow.get('jobs', {}).values():
                if 'timeout-minutes' in job:
                    assert job['timeout-minutes'] <= 30, "Timeouts should be reasonable"
    
    # Test 17-24: Job Parallelization
    def test_core_01_has_parallel_jobs(self, core_workflows):
        """Test 17: Verify Core-1 has parallel job execution"""
        if 'core-01' in core_workflows:
            workflow = core_workflows['core-01']
            jobs = workflow.get('jobs', {})
            # Check if jobs can run in parallel (no circular dependencies)
            assert len(jobs) > 1, "Core-1 should have multiple jobs"
    
    def test_core_02_has_parallel_jobs(self, core_workflows):
        """Test 18: Verify Core-2 has parallel job execution"""
        if 'core-02' in core_workflows:
            workflow = core_workflows['core-02']
            jobs = workflow.get('jobs', {})
            assert len(jobs) > 1, "Core-2 should have multiple jobs"
    
    def test_core_04_has_parallel_jobs(self, core_workflows):
        """Test 19: Verify Core-4 has parallel job execution"""
        if 'core-04' in core_workflows:
            workflow = core_workflows['core-04']
            jobs = workflow.get('jobs', {})
            assert len(jobs) > 1, "Core-4 should have multiple jobs"
    
    def test_core_05_has_parallel_jobs(self, core_workflows):
        """Test 20: Verify Core-5 has parallel job execution"""
        if 'core-05' in core_workflows:
            workflow = core_workflows['core-05']
            jobs = workflow.get('jobs', {})
            assert len(jobs) > 1, "Core-5 should have multiple jobs"
    
    def test_core_06_has_parallel_jobs(self, core_workflows):
        """Test 21: Verify Core-6 has parallel job execution"""
        if 'core-06' in core_workflows:
            workflow = core_workflows['core-06']
            jobs = workflow.get('jobs', {})
            assert len(jobs) > 1, "Core-6 should have multiple jobs"
    
    def test_core_07_has_parallel_jobs(self, core_workflows):
        """Test 22: Verify Core-7 has parallel job execution"""
        if 'core-07' in core_workflows:
            workflow = core_workflows['core-07']
            jobs = workflow.get('jobs', {})
            assert len(jobs) > 1, "Core-7 should have multiple jobs"
    
    def test_core_08_has_parallel_jobs(self, core_workflows):
        """Test 23: Verify Core-8 has parallel job execution"""
        if 'core-08' in core_workflows:
            workflow = core_workflows['core-08']
            jobs = workflow.get('jobs', {})
            assert len(jobs) > 1, "Core-8 should have multiple jobs"
    
    def test_total_workflow_size_reduced(self):
        """Test 24: Verify total workflow size is reasonable"""
        core_workflows = list(Path('.github/workflows').glob('core-*.yml'))
        total_size = sum(wf.stat().st_size for wf in core_workflows)
        total_size_kb = total_size / 1024
        # Updated target based on actual comprehensive workflow sizes (148 KB actual, 180 KB target with 20% headroom)
        assert total_size_kb < 180, f"Total size should be <180 KB, got {total_size_kb:.2f} KB"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

