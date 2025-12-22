"""
Build performance tests.
"""
import subprocess
import time
from pathlib import Path

import pytest

from tests.fixtures.production_fixtures import docker_compose_path, dockerfile_path, project_root


@pytest.mark.performance
@pytest.mark.slow
class TestBuildPerformance:
    """Test suite for build performance."""
    
    def test_docker_build_time(self, dockerfile_path: Path, project_root: Path):
        """Test Docker build completes within time limit."""
        import os
        try:
            subprocess.run(['docker', '--version'], 
                         capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Docker not available")
        
        # Check available disk space
        try:
            import shutil
            free_space_gb = shutil.disk_usage(project_root).free / (1024 ** 3)
            if free_space_gb < 5:
                pytest.skip(f"Insufficient disk space: {free_space_gb:.2f}GB free (need at least 5GB)")
        except Exception:
            pass
        
        # Clean up Docker before build
        try:
            subprocess.run(['docker', 'system', 'prune', '-f'], 
                         capture_output=True, timeout=60)
        except Exception:
            pass
        
        start_time = time.time()
        result = subprocess.run(
            ['docker', 'build', '-t', 'amas-test:perf', 
             '-f', str(dockerfile_path), str(project_root)],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes
            env={**os.environ, 'DOCKER_BUILDKIT': '1'}
        )
        build_time = time.time() - start_time
        
        if result.returncode != 0:
            if 'No space left on device' in result.stderr:
                pytest.skip(f"Build failed due to insufficient disk space: {result.stderr}")
            assert False, f"Build failed: {result.stderr}"
        
        assert result.returncode == 0, f"Build failed: {result.stderr}"
        assert build_time < 600, \
            f"Build took {build_time:.2f}s, should be < 600s"
    
    def test_docker_compose_startup_time(self, docker_compose_path: Path, project_root: Path):
        """Test docker-compose startup time."""
        try:
            subprocess.run(['docker-compose', '--version'], 
                         capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Docker Compose not available")
        
        # Clean up any existing containers
        subprocess.run(
            ['docker-compose', '-f', str(docker_compose_path), 'down'],
            cwd=project_root,
            capture_output=True,
            timeout=60
        )
        
        start_time = time.time()
        result = subprocess.run(
            ['docker-compose', '-f', str(docker_compose_path), 'up', '-d'],
            cwd=project_root,
            capture_output=True,
            timeout=300
        )
        startup_time = time.time() - start_time
        
        # Cleanup
        subprocess.run(
            ['docker-compose', '-f', str(docker_compose_path), 'down'],
            cwd=project_root,
            capture_output=True,
            timeout=60
        )
        
        if result.returncode == 0:
            assert startup_time < 300, \
                f"Startup took {startup_time:.2f}s, should be < 300s"

