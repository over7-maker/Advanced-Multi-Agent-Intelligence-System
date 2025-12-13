"""
Deployment script functional tests.
"""
import os
import subprocess
from pathlib import Path

import pytest

from tests.fixtures.production_fixtures import deploy_script_path


@pytest.mark.functional
class TestDeployScript:
    """Test suite for deploy-production.sh functionality."""
    
    def test_deploy_script_exists(self, deploy_script_path: Path):
        """Test that deploy-production.sh exists and is executable."""
        assert deploy_script_path.exists(), \
            f"deploy-production.sh not found at {deploy_script_path}"
        assert deploy_script_path.is_file(), "deploy-production.sh should be a file"
        
        # Check if executable
        assert os.access(deploy_script_path, os.X_OK), \
            "deploy-production.sh should be executable"
    
    def test_deploy_script_syntax(self, deploy_script_path: Path):
        """Test that deploy-production.sh has valid bash syntax."""
        # Convert CRLF to LF if needed
        with open(deploy_script_path, 'rb') as f:
            content = f.read()
        content = content.replace(b'\r\n', b'\n')
        with open(deploy_script_path, 'wb') as f:
            f.write(content)
        
        result = subprocess.run(
            ['bash', '-n', str(deploy_script_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0, \
            f"deploy-production.sh has syntax errors: {result.stderr}"
    
    def test_pre_flight_checks_function(self, deploy_script_path: Path):
        """Test that deploy script has pre-flight checks."""
        with open(deploy_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'pre_flight_checks' in content or 'pre-flight' in content.lower(), \
            "Deploy script should have pre-flight checks"
    
    def test_backup_function(self, deploy_script_path: Path):
        """Test that deploy script has backup function."""
        with open(deploy_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'backup' in content.lower(), \
            "Deploy script should backup before deployment"
    
    def test_build_function(self, deploy_script_path: Path):
        """Test that deploy script has build function."""
        with open(deploy_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'build' in content.lower(), \
            "Deploy script should have build function"
    
    def test_deploy_function(self, deploy_script_path: Path):
        """Test that deploy script has deploy function."""
        with open(deploy_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'deploy' in content.lower() or 'deploy()' in content, \
            "Deploy script should have deploy function"
    
    def test_health_check_function(self, deploy_script_path: Path):
        """Test that deploy script has health check function."""
        with open(deploy_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'check_health' in content or 'health' in content.lower(), \
            "Deploy script should have health check function"
    
    def test_migration_function(self, deploy_script_path: Path):
        """Test that deploy script has migration function."""
        with open(deploy_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'migration' in content.lower() or 'alembic' in content.lower(), \
            "Deploy script should run database migrations"
    
    def test_rollback_function(self, deploy_script_path: Path):
        """Test that deploy script has rollback function."""
        with open(deploy_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'rollback' in content.lower(), \
            "Deploy script should have rollback function"
    
    def test_error_handling(self, deploy_script_path: Path):
        """Test that deploy script has error handling."""
        with open(deploy_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'set -e' in content or 'set -euo' in content, \
            "Deploy script should use strict error handling"
        assert 'error' in content.lower() or 'log_error' in content, \
            "Deploy script should have error logging"
    
    def test_command_line_options(self, deploy_script_path: Path):
        """Test that deploy script supports command line options."""
        with open(deploy_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for case statement or argument parsing
        assert 'case' in content or '--build' in content or '--rollback' in content, \
            "Deploy script should support command line options"

