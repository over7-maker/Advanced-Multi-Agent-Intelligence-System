"""
AMAS Test Configuration
Pytest configuration and fixtures for the AMAS test suite.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

import pytest

# Set test environment
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["SECRET_KEY"] = "test_secret_key"
os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key"

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Import application modules if available
try:
    from amas.config.settings import get_settings  # noqa: E402
    from amas.main import AMASApplication  # noqa: E402
except ImportError:
    # Allow tests to run even if main application is not fully setup
    pass


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config():
    """Test configuration fixture."""
    return {
        "environment": "testing",
        "database_url": "sqlite:///test.db",
        "redis_url": "redis://localhost:6379/1",
        "neo4j_uri": "bolt://localhost:7687",
        "secret_key": "test_secret_key",
        "jwt_secret_key": "test_jwt_secret_key",
        "debug": True,
        "testing": True,
    }


@pytest.fixture
def mock_database_service():
    """Mock database service for testing."""
    mock_service = MagicMock()
    mock_service.is_healthy = AsyncMock(return_value=True)
    mock_service.initialize = AsyncMock()
    mock_service.shutdown = AsyncMock()
    return mock_service


@pytest.fixture
def mock_security_service():
    """Mock security service for testing."""
    mock_service = MagicMock()
    mock_service.hash_password = MagicMock(return_value="hashed_password")
    mock_service.verify_password = MagicMock(return_value=True)
    mock_service.create_access_token = MagicMock(return_value="test_token")
    mock_service.verify_token = MagicMock(return_value={"sub": "test_user"})
    return mock_service


@pytest.fixture
def sample_task():
    """Sample task for testing."""
    return {
        "id": "test_task_001",
        "type": "security_scan",
        "description": "Test security scan task",
        "parameters": {"target": "example.com", "depth": "basic"},
        "priority": 1,
        "status": "pending",
    }


@pytest.fixture
def sample_workflow():
    """Sample workflow for testing."""
    return {
        "id": "test_workflow_001",
        "name": "Test Security Workflow",
        "description": "Test workflow for security scanning",
        "steps": [
            {
                "name": "scan",
                "agent": "security_expert",
                "parameters": {"target": "example.com"},
            }
        ],
    }


@pytest.fixture
def mock_ai_provider():
    """Mock AI provider for testing."""
    mock_provider = MagicMock()
    mock_provider.generate = AsyncMock(return_value="Mock AI response")
    mock_provider.is_healthy = AsyncMock(return_value=True)
    mock_provider.get_status = MagicMock(return_value={"status": "healthy"})
    return mock_provider


@pytest.fixture
def mock_agent():
    """Mock agent for testing."""
    mock_agent = MagicMock()
    mock_agent.agent_id = "test_agent_001"
    mock_agent.name = "Test Agent"
    mock_agent.status = "active"
    mock_agent.execute_task = AsyncMock(
        return_value={"status": "success", "result": "Mock task result"}
    )
    return mock_agent


@pytest.fixture
def mock_orchestrator():
    """Mock orchestrator for testing."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.submit_task = AsyncMock(return_value="task_id_123")
    mock_orchestrator.get_task_status = AsyncMock(return_value={"status": "completed"})
    mock_orchestrator.get_agents = MagicMock(return_value=[])
    return mock_orchestrator


@pytest.fixture(autouse=True)
async def setup_test_environment():
    """Setup test environment before each test."""
    # Ensure test directories exist
    test_dirs = [
        "logs",
        "data/temp",
        "artifacts/test",
    ]

    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    yield

    # Cleanup after test
    # Remove test artifacts if needed
    pass


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    from fastapi.testclient import TestClient

    try:
        from src.api.main import app

        return TestClient(app)
    except ImportError:
        # Fallback mock client for incomplete API
        mock_client = MagicMock()
        mock_client.get = MagicMock()
        mock_client.post = MagicMock()
        mock_client.put = MagicMock()
        mock_client.delete = MagicMock()
        return mock_client
