"""
Production test fixtures for component testing.
"""
import os
import tempfile
from pathlib import Path
from typing import Dict
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def dockerfile_path(project_root: Path) -> Path:
    """Get Dockerfile path."""
    return project_root / "Dockerfile"


@pytest.fixture
def docker_compose_path(project_root: Path) -> Path:
    """Get docker-compose.prod.yml path."""
    return project_root / "docker-compose.prod.yml"


@pytest.fixture
def nginx_config_path(project_root: Path) -> Path:
    """Get nginx.conf path."""
    return project_root / "nginx" / "nginx.conf"


@pytest.fixture
def k8s_manifest_path(project_root: Path) -> Path:
    """Get k8s/deployment.yaml path."""
    return project_root / "k8s" / "deployment.yaml"


@pytest.fixture
def cicd_workflow_path(project_root: Path) -> Path:
    """Get .github/workflows/deploy.yml path."""
    return project_root / ".github" / "workflows" / "deploy.yml"


@pytest.fixture
def env_template_path(project_root: Path) -> Path:
    """Get .env.production.example path."""
    return project_root / ".env.production.example"


@pytest.fixture
def backup_script_path(project_root: Path) -> Path:
    """Get scripts/backup.sh path."""
    return project_root / "scripts" / "backup.sh"


@pytest.fixture
def restore_script_path(project_root: Path) -> Path:
    """Get scripts/restore.sh path."""
    return project_root / "scripts" / "restore.sh"


@pytest.fixture
def deploy_script_path(project_root: Path) -> Path:
    """Get scripts/deploy-production.sh path."""
    return project_root / "scripts" / "deploy-production.sh"


@pytest.fixture
def alembic_ini_path(project_root: Path) -> Path:
    """Get alembic.ini path."""
    return project_root / "alembic.ini"


@pytest.fixture
def alembic_env_path(project_root: Path) -> Path:
    """Get alembic/env.py path."""
    return project_root / "alembic" / "env.py"


@pytest.fixture
def migration_path(project_root: Path) -> Path:
    """Get alembic/versions/001_initial_schema.py path."""
    return project_root / "alembic" / "versions" / "001_initial_schema.py"


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_env_vars():
    """Test environment variables."""
    return {
        'ENVIRONMENT': 'test',
        'SECRET_KEY': 'test-secret-key-32-chars-minimum-required',
        'JWT_SECRET': 'test-jwt-secret-32-chars-minimum-required',
        'DB_PASSWORD': 'test_db_password',
        'REDIS_PASSWORD': 'test_redis_password',
        'NEO4J_PASSWORD': 'test_neo4j_password',
        'DATABASE_URL': 'postgresql://test:test@localhost:5432/test',
        'REDIS_URL': 'redis://localhost:6379/0',
    }


@pytest.fixture
def mock_docker():
    """Mock Docker client."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
        yield mock_run


@pytest.fixture
def mock_s3():
    """Mock AWS S3 client."""
    with patch('boto3.client') as mock_client:
        mock_s3_client = MagicMock()
        mock_client.return_value = mock_s3_client
        yield mock_s3_client


@pytest.fixture
def mock_aws_cli():
    """Mock AWS CLI."""
    with patch('subprocess.run') as mock_run:
        def side_effect(cmd, **kwargs):
            if 'aws' in cmd and 's3' in cmd:
                return MagicMock(returncode=0, stdout='', stderr='')
            return MagicMock(returncode=0, stdout='', stderr='')
        mock_run.side_effect = side_effect
        yield mock_run


@pytest.fixture
def test_database_url():
    """Test database URL."""
    return "postgresql://test:test@localhost:5432/test_db"


@pytest.fixture
def mock_postgres():
    """Mock PostgreSQL connection."""
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        yield mock_conn


@pytest.fixture
def mock_redis():
    """Mock Redis connection."""
    with patch('redis.Redis') as mock_redis_class:
        mock_redis_instance = MagicMock()
        mock_redis_class.return_value = mock_redis_instance
        yield mock_redis_instance


@pytest.fixture
def sample_backup_file(temp_dir: Path) -> Path:
    """Create sample backup file for testing."""
    backup_file = temp_dir / "test_backup.sql.gz"
    backup_file.write_bytes(b"fake backup data")
    return backup_file


@pytest.fixture
def sample_backup_manifest(temp_dir: Path) -> Path:
    """Create sample backup manifest."""
    import json
    manifest = {
        "backup_info": {
            "environment": "test",
            "backup_type": "full",
            "timestamp": "20250101-120000",
            "created_at": "2025-01-01T12:00:00Z"
        },
        "backup_contents": {
            "database": True,
            "redis": True
        }
    }
    manifest_file = temp_dir / "backup-manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2))
    return manifest_file

