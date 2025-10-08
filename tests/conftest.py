"""

Test configuration and fixtures for AMAS test suite
"""

import asyncio
import os
import sys
from typing import Any, AsyncGenerator, Dict

import httpx
import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from amas.config.settings import get_settings
from amas.main import AMASApplication


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def amas_app() -> AsyncGenerator[AMASApplication, None]:
    """Create and initialize AMAS application for testing"""
    app = AMASApplication()
    await app.initialize()
    yield app
    await app.shutdown()


@pytest.fixture
async def test_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create test client for API testing"""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        yield client


@pytest.fixture
def test_config() -> Dict[str, Any]:
    """Test configuration"""
    return {
        "llm": {
            "provider": "ollama",
            "model": "llama2",
            "base_url": "http://localhost:11434",
        },
        "vector": {"provider": "faiss", "dimension": 768},
        "knowledge_graph": {
            "provider": "neo4j",
            "uri": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "password",
        },
        "database": {"url": "postgresql://test:test@localhost:5432/amas_test"},
        "security": {
            "jwt_secret": "test_secret_key",
            "encryption_key": "test_encryption_key_32_bytes",
            "audit_enabled": True,
        },
    }


@pytest.fixture
def sample_task() -> Dict[str, Any]:
    """Sample task for testing"""
    return {
        "type": "osint",
        "description": "Test OSINT task",
        "parameters": {
            "keywords": ["test", "osint"],
            "sources": ["web", "social_media"],
        },
        "priority": 1,
    }


@pytest.fixture
def sample_workflow() -> Dict[str, Any]:
    """Sample workflow for testing"""
    return {
        "workflow_id": "test_workflow",
        "parameters": {"target": "test_target", "depth": 2},
    }
