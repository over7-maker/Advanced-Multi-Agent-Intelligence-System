"""
Container security tests.
"""
import re
from pathlib import Path

import pytest

from tests.fixtures.production_fixtures import dockerfile_path


@pytest.mark.security
class TestContainerSecurity:
    """Test suite for container security."""
    
    def test_non_root_user(self, dockerfile_path: Path):
        """Test Dockerfile uses non-root user."""
        with open(dockerfile_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'USER' in content, "Dockerfile should use USER directive"
        
        # Check that user is not root
        user_lines = [line for line in content.split('\n') if 'USER' in line.upper()]
        for line in user_lines:
            assert 'root' not in line.lower() or 'USER root' not in line, \
                "Dockerfile should not run as root user"
    
    def test_minimal_base_image(self, dockerfile_path: Path):
        """Test Dockerfile uses minimal base image."""
        with open(dockerfile_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for minimal base images
        assert any(base in content.lower() for base in ['-slim', '-alpine', 'scratch']), \
            "Dockerfile should use minimal base image"
    
    def test_no_secrets_in_dockerfile(self, dockerfile_path: Path):
        """Test Dockerfile doesn't contain secrets."""
        with open(dockerfile_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for potential secrets
        secret_patterns = [
            r'password\s*=\s*["\']',
            r'api[_-]?key\s*=\s*["\']',
            r'secret\s*=\s*["\']',
        ]
        
        for pattern in secret_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            assert len(matches) == 0, \
                f"Found potential secrets in Dockerfile: {matches}"

