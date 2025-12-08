"""
Dockerfile validation tests.
"""
import pytest
from pathlib import Path

from tests.fixtures.production_fixtures import dockerfile_path
from tests.utils.validation_helpers import DockerfileValidator


class TestDockerfileValidation:
    """Test suite for Dockerfile validation."""
    
    def test_dockerfile_exists(self, dockerfile_path: Path):
        """Test that Dockerfile exists."""
        assert dockerfile_path.exists(), f"Dockerfile not found at {dockerfile_path}"
    
    def test_dockerfile_syntax(self, dockerfile_path: Path):
        """Test Dockerfile syntax is valid."""
        valid, error = DockerfileValidator.validate_syntax(dockerfile_path)
        assert valid, f"Dockerfile syntax error: {error}"
    
    def test_multi_stage_build(self, dockerfile_path: Path):
        """Test that Dockerfile has multi-stage build."""
        stages = DockerfileValidator.check_stages(dockerfile_path)
        assert len(stages) >= 2, "Dockerfile should have at least 2 build stages"
        
        # Check for required stages
        stage_names = [s.lower() for s in stages]
        assert 'python-builder' in stage_names or any('python' in s for s in stage_names), \
            "Missing python-builder stage"
        assert 'frontend-builder' in stage_names or any('frontend' in s for s in stage_names), \
            "Missing frontend-builder stage"
    
    def test_security_practices(self, dockerfile_path: Path):
        """Test Dockerfile follows security best practices."""
        practices = DockerfileValidator.check_security_practices(dockerfile_path)
        
        assert practices['non_root_user'], "Dockerfile should use non-root user"
        assert practices['health_check'], "Dockerfile should have HEALTHCHECK"
        assert practices['minimal_base'], "Dockerfile should use minimal base image"
        assert practices['no_secrets'], "Dockerfile should not contain hardcoded secrets"
    
    def test_required_sections(self, dockerfile_path: Path):
        """Test that Dockerfile has all required sections."""
        with open(dockerfile_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required sections
        assert 'FROM' in content, "Missing FROM statement"
        assert 'WORKDIR' in content, "Missing WORKDIR"
        assert 'COPY' in content, "Missing COPY statements"
        assert 'EXPOSE' in content, "Missing EXPOSE statement"
        assert 'CMD' in content or 'ENTRYPOINT' in content, "Missing CMD or ENTRYPOINT"
    
    def test_health_check_configuration(self, dockerfile_path: Path):
        """Test health check is properly configured."""
        with open(dockerfile_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'HEALTHCHECK' in content, "Missing HEALTHCHECK"
        
        # Check for proper health check configuration
        assert 'interval' in content.lower() or '--interval' in content, \
            "Health check should specify interval"
        assert 'timeout' in content.lower() or '--timeout' in content, \
            "Health check should specify timeout"
        assert 'retries' in content.lower() or '--retries' in content, \
            "Health check should specify retries"
    
    def test_non_root_user(self, dockerfile_path: Path):
        """Test that Dockerfile creates and uses non-root user."""
        with open(dockerfile_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for user creation
        assert 'useradd' in content.lower() or 'USER' in content, \
            "Dockerfile should create non-root user"
        
        # Check for USER directive
        assert 'USER' in content, "Dockerfile should switch to non-root user"
        
        # Verify user is not root
        user_lines = [line for line in content.split('\n') if 'USER' in line.upper()]
        for line in user_lines:
            assert 'root' not in line.lower() or 'USER root' not in line, \
                "Dockerfile should not run as root user"

