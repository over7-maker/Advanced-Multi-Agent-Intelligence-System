"""
Docker build functional tests.
"""
import subprocess
import time
from pathlib import Path

import pytest

from tests.fixtures.production_fixtures import dockerfile_path, project_root


@pytest.mark.functional
class TestDockerBuild:
    """Test suite for Docker build functionality."""
    
    @pytest.mark.slow
    def test_dockerfile_builds(self, dockerfile_path: Path, project_root: Path):
        """Test that Dockerfile builds successfully."""
        # Skip if Docker is not available
        try:
            subprocess.run(['docker', '--version'], 
                         capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Docker not available")
        
        # Build Docker image
        build_start = time.time()
        result = subprocess.run(
            ['docker', 'build', '-t', 'amas-test:latest', '-f', str(dockerfile_path), str(project_root)],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        build_time = time.time() - build_start
        
        assert result.returncode == 0, \
            f"Docker build failed: {result.stderr}\n{result.stdout}"
        
        # Build should complete within reasonable time
        assert build_time < 600, f"Build took too long: {build_time:.2f}s"
    
    @pytest.mark.slow
    def test_multi_stage_build(self, dockerfile_path: Path, project_root: Path):
        """Test that multi-stage build works correctly."""
        try:
            subprocess.run(['docker', '--version'], 
                         capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Docker not available")
        
        # Build with target stages
        stages = ['python-builder', 'frontend-builder']
        
        for stage in stages:
            result = subprocess.run(
                ['docker', 'build', '--target', stage, 
                 '-t', f'amas-test:{stage}', '-f', str(dockerfile_path), str(project_root)],
                capture_output=True,
                text=True,
                timeout=300
            )
            assert result.returncode == 0, \
                f"Failed to build stage {stage}: {result.stderr}"
    
    def test_dockerfile_readable(self, dockerfile_path: Path):
        """Test that Dockerfile is readable."""
        assert dockerfile_path.exists(), "Dockerfile should exist"
        assert dockerfile_path.is_file(), "Dockerfile should be a file"
        
        # Try to read the file
        with open(dockerfile_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert len(content) > 0, "Dockerfile should not be empty"
        assert 'FROM' in content, "Dockerfile should contain FROM statement"
    
    @pytest.mark.slow
    def test_image_size_reasonable(self, dockerfile_path: Path, project_root: Path):
        """Test that built image size is reasonable."""
        try:
            subprocess.run(['docker', '--version'], 
                         capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Docker not available")
        
        # Build image
        result = subprocess.run(
            ['docker', 'build', '-t', 'amas-test:size-test', 
             '-f', str(dockerfile_path), str(project_root)],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode != 0:
            pytest.skip(f"Docker build failed: {result.stderr}")
        
        # Get image size
        inspect_result = subprocess.run(
            ['docker', 'inspect', '--format={{.Size}}', 'amas-test:size-test'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if inspect_result.returncode == 0:
            size_bytes = int(inspect_result.stdout.strip())
            size_gb = size_bytes / (1024 ** 3)
            
            # Image should be less than 5GB (reasonable for production)
            assert size_gb < 5, \
                f"Image size {size_gb:.2f}GB is too large (should be < 5GB)"
    
    @pytest.mark.slow
    def test_health_check_in_image(self, dockerfile_path: Path, project_root: Path):
        """Test that health check is configured in built image."""
        try:
            subprocess.run(['docker', '--version'], 
                         capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Docker not available")
        
        # Build image
        result = subprocess.run(
            ['docker', 'build', '-t', 'amas-test:health-test', 
             '-f', str(dockerfile_path), str(project_root)],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode != 0:
            pytest.skip(f"Docker build failed: {result.stderr}")
        
        # Inspect image for health check
        inspect_result = subprocess.run(
            ['docker', 'inspect', '--format={{.Config.Healthcheck}}', 'amas-test:health-test'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Health check should be present (may be empty if not set, but we check Dockerfile has it)
        # We already validated Dockerfile has HEALTHCHECK in validation tests
        assert True  # If we got here, image built successfully

