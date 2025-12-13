"""
Nginx configuration validation tests.
"""
import pytest
from pathlib import Path

from tests.fixtures.production_fixtures import nginx_config_path
from tests.utils.validation_helpers import NginxConfigValidator


class TestNginxConfigValidation:
    """Test suite for nginx.conf validation."""
    
    def test_nginx_config_exists(self, nginx_config_path: Path):
        """Test that nginx.conf exists."""
        assert nginx_config_path.exists(), \
            f"nginx.conf not found at {nginx_config_path}"
    
    def test_nginx_syntax(self, nginx_config_path: Path):
        """Test nginx configuration syntax."""
        valid, error = NginxConfigValidator.validate_syntax(nginx_config_path)
        # If nginx binary not available, basic validation should still pass
        assert valid, f"Nginx config syntax error: {error}"
    
    def test_required_sections(self, nginx_config_path: Path):
        """Test that nginx.conf has all required sections."""
        with open(nginx_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'http' in content, "Missing 'http' block"
        assert 'server' in content, "Missing 'server' block"
        assert 'upstream' in content, "Missing 'upstream' block"
    
    def test_ssl_configuration(self, nginx_config_path: Path):
        """Test SSL/TLS configuration."""
        with open(nginx_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for SSL configuration
        assert 'ssl_certificate' in content, "Missing SSL certificate configuration"
        assert 'ssl_certificate_key' in content, "Missing SSL certificate key"
        assert 'ssl_protocols' in content, "Missing SSL protocols"
        assert 'TLSv1.2' in content or 'TLSv1.3' in content, \
            "Should use TLS 1.2 or higher"
    
    def test_security_headers(self, nginx_config_path: Path):
        """Test that security headers are configured."""
        headers = NginxConfigValidator.check_security_headers(nginx_config_path)
        
        required_headers = [
            'Strict-Transport-Security',
            'X-Frame-Options',
            'X-Content-Type-Options',
        ]
        
        for header in required_headers:
            assert header in headers, \
                f"Missing security header: {header}"
    
    def test_rate_limiting(self, nginx_config_path: Path):
        """Test that rate limiting is configured."""
        with open(nginx_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'limit_req_zone' in content, "Missing rate limiting zones"
        assert 'limit_req' in content, "Missing rate limiting rules"
    
    def test_websocket_support(self, nginx_config_path: Path):
        """Test that WebSocket proxying is configured."""
        with open(nginx_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'Upgrade' in content, "Missing WebSocket Upgrade header"
        assert 'Connection' in content, "Missing WebSocket Connection header"
        assert '/ws' in content or 'location /ws' in content, \
            "Missing WebSocket location block"
    
    def test_upstream_configuration(self, nginx_config_path: Path):
        """Test that upstream backend is configured."""
        with open(nginx_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'upstream' in content, "Missing upstream block"
        assert 'amas_backend' in content or 'backend' in content, \
            "Missing backend upstream configuration"
    
    def test_http_to_https_redirect(self, nginx_config_path: Path):
        """Test that HTTP to HTTPS redirect is configured."""
        with open(nginx_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for HTTP server block with redirect
        assert 'return 301' in content or 'return 302' in content, \
            "Missing HTTP to HTTPS redirect"
    
    def test_gzip_compression(self, nginx_config_path: Path):
        """Test that gzip compression is enabled."""
        with open(nginx_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'gzip on' in content or 'gzip' in content, \
            "Gzip compression should be enabled"

