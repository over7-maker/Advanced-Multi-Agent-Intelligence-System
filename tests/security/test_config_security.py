"""
Configuration security tests.
"""
import re
from pathlib import Path

import pytest

from tests.fixtures.production_fixtures import (
    docker_compose_path,
    env_template_path,
    k8s_manifest_path,
    project_root,
)


@pytest.mark.security
class TestConfigSecurity:
    """Test suite for configuration security."""
    
    def test_no_hardcoded_secrets_in_compose(self, docker_compose_path: Path):
        """Test docker-compose.prod.yml has no hardcoded secrets."""
        with open(docker_compose_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for common secret patterns
        secret_patterns = [
            r'password\s*[:=]\s*["\']?[^${"\'\s}]+["\']?',
            r'secret\s*[:=]\s*["\']?[^${"\'\s}]+["\']?',
            r'key\s*[:=]\s*["\']?sk-[^${"\'\s}]+["\']?',
        ]
        
        for pattern in secret_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            # Filter out environment variable references
            hardcoded = [m for m in matches if '${' not in m and '$' not in m]
            assert len(hardcoded) == 0, \
                f"Found potential hardcoded secrets: {hardcoded}"
    
    def test_no_hardcoded_secrets_in_k8s(self, k8s_manifest_path: Path):
        """Test Kubernetes manifests have no hardcoded secrets."""
        with open(k8s_manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Secrets should be in Secret resources, not hardcoded
        # Check that sensitive values use references
        secret_patterns = [
            r'password\s*[:=]\s*["\']?[^${"\'\s}]+["\']?',
        ]
        
        for pattern in secret_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            # In Secret resources, values might be base64 encoded, which is OK
            # But in ConfigMap or other resources, they should use references
            hardcoded = [m for m in matches if '${' not in m and 'secretKeyRef' not in content]
            # Allow some hardcoded values if they're clearly placeholders
            real_secrets = [m for m in hardcoded if 'CHANGE_THIS' not in m and 'PLACEHOLDER' not in m]
            assert len(real_secrets) == 0, \
                f"Found potential hardcoded secrets: {real_secrets}"
    
    def test_ssl_tls_configuration(self, project_root: Path):
        """Test SSL/TLS configuration is strong."""
        nginx_config = project_root / "nginx" / "nginx.conf"
        if nginx_config.exists():
            with open(nginx_config, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for TLS 1.2 or higher
            assert 'TLSv1.2' in content or 'TLSv1.3' in content, \
                "Should use TLS 1.2 or higher"
            
            # Check for strong ciphers
            assert 'GCM' in content or 'ECDHE' in content, \
                "Should use strong cipher suites"
    
    def test_security_headers_present(self, project_root: Path):
        """Test that security headers are configured."""
        nginx_config = project_root / "nginx" / "nginx.conf"
        if nginx_config.exists():
            with open(nginx_config, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_headers = [
                'Strict-Transport-Security',
                'X-Frame-Options',
                'X-Content-Type-Options',
            ]
            
            for header in required_headers:
                assert header in content, \
                    f"Missing security header: {header}"

