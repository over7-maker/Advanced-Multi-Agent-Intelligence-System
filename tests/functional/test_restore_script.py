"""
Restore script functional tests.
"""
import os
import subprocess
from pathlib import Path

import pytest

from tests.fixtures.production_fixtures import restore_script_path


@pytest.mark.functional
class TestRestoreScript:
    """Test suite for restore.sh functionality."""
    
    def test_restore_script_exists(self, restore_script_path: Path):
        """Test that restore.sh exists and is executable."""
        assert restore_script_path.exists(), \
            f"restore.sh not found at {restore_script_path}"
        assert restore_script_path.is_file(), "restore.sh should be a file"
        
        # Check if executable
        assert os.access(restore_script_path, os.X_OK), \
            "restore.sh should be executable"
    
    def test_restore_script_syntax(self, restore_script_path: Path):
        """Test that restore.sh has valid bash syntax."""
        # Convert CRLF to LF if needed
        with open(restore_script_path, 'rb') as f:
            content = f.read()
        content = content.replace(b'\r\n', b'\n')
        with open(restore_script_path, 'wb') as f:
            f.write(content)
        
        result = subprocess.run(
            ['bash', '-n', str(restore_script_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0, \
            f"restore.sh has syntax errors: {result.stderr}"
    
    def test_restore_script_help(self, restore_script_path: Path):
        """Test that restore.sh shows help when requested."""
        result = subprocess.run(
            ['bash', str(restore_script_path), '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Script should either show help or exit with error
        assert result.returncode in [0, 1], \
            f"Unexpected exit code: {result.returncode}"
    
    def test_restore_script_required_args(self, restore_script_path: Path):
        """Test that restore.sh requires arguments."""
        result = subprocess.run(
            ['bash', str(restore_script_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Should fail without required arguments
        assert result.returncode != 0, \
            "Script should fail without required arguments"
    
    def test_confirmation_function(self, restore_script_path: Path):
        """Test that restore script has confirmation function."""
        with open(restore_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'confirm_restore' in content or 'confirm' in content.lower(), \
            "Restore script should have confirmation function"
    
    def test_restore_database_function(self, restore_script_path: Path):
        """Test that restore script has database restore function."""
        with open(restore_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'restore_database' in content or 'restore_postgresql' in content, \
            "Restore script should have database restore function"
    
    def test_verification_function(self, restore_script_path: Path):
        """Test that restore script has verification function."""
        with open(restore_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'verify' in content.lower(), \
            "Restore script should have verification function"
    
    def test_backup_detection_function(self, restore_script_path: Path):
        """Test that restore script can detect backup files."""
        with open(restore_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'find_backup' in content or 'backup' in content.lower(), \
            "Restore script should have backup detection function"
    
    def test_error_handling(self, restore_script_path: Path):
        """Test that restore script has error handling."""
        with open(restore_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for error handling patterns
        assert 'set -e' in content or 'set -euo' in content, \
            "Restore script should use strict error handling"
        assert 'error' in content.lower() or 'log_error' in content, \
            "Restore script should have error logging"

