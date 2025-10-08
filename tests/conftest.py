"""
AMAS Test Configuration
Production-ready test setup with fixtures and mocks
"""

import asyncio
import os
import tempfile
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest

# Set test environment
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["SECRET_KEY"] = "test_secret_key"
os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key"

from src.config.settings import Settings, get_settings


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Get test settings with overridden values."""
    return get_settings()


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def mock_database():
    """Mock database connection."""
    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_db.fetch_one = AsyncMock()
    mock_db.fetch_all = AsyncMock()
    return mock_db


@pytest.fixture
def mock_redis():
    """Mock Redis connection."""
    mock_redis = MagicMock()
    mock_redis.get = AsyncMock()
    mock_redis.set = AsyncMock()
    mock_redis.delete = AsyncMock()
    mock_redis.exists = AsyncMock()
    return mock_redis


@pytest.fixture
def mock_neo4j():
    """Mock Neo4j connection."""
    mock_neo4j = MagicMock()
    mock_neo4j.run = AsyncMock()
    mock_neo4j.execute_read = AsyncMock()
    mock_neo4j.execute_write = AsyncMock()
    return mock_neo4j


@pytest.fixture
def mock_openai():
    """Mock OpenAI API."""
    mock_openai = MagicMock()
    mock_openai.chat.completions.create = AsyncMock()
    mock_openai.embeddings.create = AsyncMock()
    return mock_openai


@pytest.fixture
def mock_anthropic():
    """Mock Anthropic API."""
    mock_anthropic = MagicMock()
    mock_anthropic.messages.create = AsyncMock()
    return mock_anthropic


@pytest.fixture
def sample_agent_data():
    """Sample agent data for testing."""
    return {
        "id": "test-agent-1",
        "name": "Test Agent",
        "type": "research",
        "status": "active",
        "capabilities": ["web_search", "data_analysis"],
        "config": {"model": "gpt-4", "temperature": 0.7, "max_tokens": 2000},
    }


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "id": "test-task-1",
        "agent_id": "test-agent-1",
        "description": "Test task description",
        "status": "pending",
        "priority": "medium",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": "test-user-1",
        "username": "testuser",
        "email": "test@example.com",
        "role": "user",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for external API calls."""
    mock_client = MagicMock()
    mock_client.get = AsyncMock()
    mock_client.post = AsyncMock()
    mock_client.put = AsyncMock()
    mock_client.delete = AsyncMock()
    return mock_client


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    mock_logger = MagicMock()
    mock_logger.info = MagicMock()
    mock_logger.warning = MagicMock()
    mock_logger.error = MagicMock()
    mock_logger.debug = MagicMock()
    return mock_logger


# Test data fixtures
@pytest.fixture
def test_agents():
    """Test agent data."""
    return [
        {
            "id": "agent-1",
            "name": "Research Agent",
            "type": "research",
            "status": "active",
        },
        {
            "id": "agent-2",
            "name": "Analysis Agent",
            "type": "analysis",
            "status": "active",
        },
    ]


@pytest.fixture
def test_tasks():
    """Test task data."""
    return [
        {
            "id": "task-1",
            "agent_id": "agent-1",
            "description": "Research task",
            "status": "pending",
        },
        {
            "id": "task-2",
            "agent_id": "agent-2",
            "description": "Analysis task",
            "status": "in_progress",
        },
    ]


# Async test utilities
@pytest.fixture
async def async_test_client():
    """Async test client for API testing."""
    from fastapi.testclient import TestClient

    from main import app

    with TestClient(app) as client:
        yield client


# Database test utilities
@pytest.fixture
async def test_database():
    """Test database setup."""
    # This would set up a test database
    # Implementation depends on your database setup
    pass


@pytest.fixture
async def cleanup_database():
    """Cleanup test database after tests."""
    # This would clean up test data
    # Implementation depends on your database setup
    pass


# Performance testing fixtures
@pytest.fixture
def performance_metrics():
    """Performance testing metrics."""
    return {
        "response_time": 0.0,
        "memory_usage": 0.0,
        "cpu_usage": 0.0,
        "request_count": 0,
    }


# Security testing fixtures
@pytest.fixture
def security_test_cases():
    """Security test cases."""
    return [
        {
            "name": "SQL Injection",
            "payload": "'; DROP TABLE users; --",
            "expected_result": "safe",
        },
        {
            "name": "XSS Attack",
            "payload": "<script>alert('xss')</script>",
            "expected_result": "safe",
        },
    ]


# Load testing fixtures
@pytest.fixture
def load_test_config():
    """Load testing configuration."""
    return {
        "users": 100,
        "spawn_rate": 10,
        "run_time": "5m",
        "target_host": "http://localhost:8000",
    }
