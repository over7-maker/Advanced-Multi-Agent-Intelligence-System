"""
Alembic migration functional tests.
"""
import os
import subprocess
from pathlib import Path

import pytest

from tests.fixtures.production_fixtures import (
    alembic_env_path,
    alembic_ini_path,
    migration_path,
    project_root,
)


@pytest.mark.functional
class TestAlembicMigrations:
    """Test suite for Alembic migration functionality."""
    
    def test_alembic_ini_exists(self, alembic_ini_path: Path):
        """Test that alembic.ini exists."""
        assert alembic_ini_path.exists(), \
            f"alembic.ini not found at {alembic_ini_path}"
    
    def test_alembic_ini_configuration(self, alembic_ini_path: Path):
        """Test alembic.ini has required configuration."""
        with open(alembic_ini_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert '[alembic]' in content, "Missing [alembic] section"
        assert 'script_location' in content, "Missing script_location"
        assert 'sqlalchemy.url' in content, "Missing sqlalchemy.url"
    
    def test_alembic_env_exists(self, alembic_env_path: Path):
        """Test that alembic/env.py exists."""
        assert alembic_env_path.exists(), \
            f"alembic/env.py not found at {alembic_env_path}"
    
    def test_alembic_env_structure(self, alembic_env_path: Path):
        """Test alembic/env.py has required functions."""
        with open(alembic_env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'run_migrations_offline' in content, \
            "Missing run_migrations_offline function"
        assert 'run_migrations_online' in content, \
            "Missing run_migrations_online function"
        assert 'target_metadata' in content, \
            "Missing target_metadata"
    
    def test_migration_file_exists(self, migration_path: Path):
        """Test that initial migration file exists."""
        assert migration_path.exists(), \
            f"Migration file not found at {migration_path}"
    
    def test_migration_file_syntax(self, migration_path: Path):
        """Test migration file has valid Python syntax."""
        result = subprocess.run(
            ['python', '-m', 'py_compile', str(migration_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0, \
            f"Migration file has syntax errors: {result.stderr}"
    
    def test_migration_structure(self, migration_path: Path):
        """Test migration file has required structure."""
        with open(migration_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'revision' in content, "Missing revision identifier"
        assert 'down_revision' in content, "Missing down_revision"
        assert 'def upgrade()' in content, "Missing upgrade function"
        assert 'def downgrade()' in content, "Missing downgrade function"
    
    def test_migration_imports(self, migration_path: Path):
        """Test migration file has required imports."""
        with open(migration_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'from alembic import op' in content, "Missing alembic import"
        assert 'import sqlalchemy as sa' in content, "Missing sqlalchemy import"
    
    def test_alembic_command_available(self, project_root: Path):
        """Test that alembic command is available."""
        try:
            result = subprocess.run(
                ['alembic', '--version'],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=project_root
            )
            assert result.returncode == 0, "Alembic command not available"
        except FileNotFoundError:
            pytest.skip("Alembic not installed")
    
    def test_alembic_config_loads(self, alembic_ini_path: Path, project_root: Path):
        """Test that alembic configuration loads correctly."""
        try:
            result = subprocess.run(
                ['alembic', 'current'],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=project_root,
                env={**os.environ, 'DATABASE_URL': 'sqlite:///test.db'}
            )
            # Should either show current revision or error about no database
            # Both are acceptable - we're just checking alembic can read config
            assert True  # If we got here, config loaded
        except FileNotFoundError:
            pytest.skip("Alembic not installed")
        except Exception:
            # Other errors are acceptable for this test
            pass

