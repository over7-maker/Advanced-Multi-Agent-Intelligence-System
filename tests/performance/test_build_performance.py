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
        try:
            subprocess.run(['docker', '--version'], 
                         capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Docker not available")
        
        start_time = time.time()
        result = subprocess.run(
            ['docker', 'build', '-t', 'amas-test:perf', 
             '-f', str(dockerfile_path), str(project_root)],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes
        )
        build_time = time.time() - start_time
        
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

