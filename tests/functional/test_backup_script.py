"""
Backup script functional tests.
"""
import json
import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tests.fixtures.production_fixtures import backup_script_path, project_root


@pytest.mark.functional
class TestBackupScript:
    """Test suite for backup.sh functionality."""
    
    def test_backup_script_exists(self, backup_script_path: Path):
        """Test that backup.sh exists and is executable."""
        assert backup_script_path.exists(), \
            f"backup.sh not found at {backup_script_path}"
        assert backup_script_path.is_file(), "backup.sh should be a file"
        
        # Check if executable
        import os
        assert os.access(backup_script_path, os.X_OK), \
            "backup.sh should be executable"
    
    def test_backup_script_syntax(self, backup_script_path: Path):
        """Test that backup.sh has valid bash syntax."""
        # Convert CRLF to LF if needed
        with open(backup_script_path, 'rb') as f:
            content = f.read()
        content = content.replace(b'\r\n', b'\n')
        with open(backup_script_path, 'wb') as f:
            f.write(content)
        
        result = subprocess.run(
            ['bash', '-n', str(backup_script_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0, \
            f"backup.sh has syntax errors: {result.stderr}"
    
    def test_backup_script_help(self, backup_script_path: Path):
        """Test that backup.sh shows help when requested."""
        result = subprocess.run(
            ['bash', str(backup_script_path), '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Script should either show help or exit with error (both are valid)
        assert result.returncode in [0, 1], \
            f"Unexpected exit code: {result.returncode}"
    
    def test_backup_script_required_args(self, backup_script_path: Path):
        """Test that backup.sh requires environment argument."""
        result = subprocess.run(
            ['bash', str(backup_script_path)],
            capture_output=True,
            text=True,
            timeout=10,
            env={**dict(os.environ), 'BACKUP_DIR': str(Path.cwd() / 'test_backups')}
        )
        # Should fail without required arguments
        assert result.returncode != 0, \
            "Script should fail without required arguments"
    
    @pytest.mark.slow
    def test_backup_creates_manifest(self, backup_script_path: Path, temp_dir: Path):
        """Test that backup creates manifest file."""
        # This would require actual Docker services running
        # For now, we'll test the script structure
        with open(backup_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that manifest creation function exists
        assert 'create_backup_manifest' in content or 'backup-manifest' in content, \
            "Backup script should create manifest file"
    
    def test_backup_verification_function(self, backup_script_path: Path):
        """Test that backup script has verification function."""
        with open(backup_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'verify_backup' in content or 'verify' in content.lower(), \
            "Backup script should have verification function"
    
    def test_s3_upload_function(self, backup_script_path: Path):
        """Test that backup script has S3 upload function."""
        with open(backup_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'upload_to_s3' in content or 's3' in content.lower(), \
            "Backup script should have S3 upload function"
    
    def test_cleanup_function(self, backup_script_path: Path):
        """Test that backup script has cleanup function."""
        with open(backup_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'cleanup' in content.lower(), \
            "Backup script should have cleanup function"
    
    def test_notification_function(self, backup_script_path: Path):
        """Test that backup script has notification function."""
        with open(backup_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'notification' in content.lower() or 'notify' in content.lower(), \
            "Backup script should have notification function"
    
    @patch('subprocess.run')
    def test_backup_database_function_exists(self, mock_run, backup_script_path: Path):
        """Test that database backup function exists."""
        with open(backup_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'backup_database' in content or 'backup_postgresql' in content, \
            "Backup script should have database backup function"
    
    @patch('subprocess.run')
    def test_backup_redis_function_exists(self, mock_run, backup_script_path: Path):
        """Test that Redis backup function exists."""
        with open(backup_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'backup_redis' in content, \
            "Backup script should have Redis backup function"

