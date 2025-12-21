"""
Performance test fixtures and configuration
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def performance_thresholds():
    """Performance thresholds for tests"""
    return {
        "api_response_p95": 0.2,  # 200ms
        "task_creation": 0.5,  # 500ms
        "task_execution": 30.0,  # 30s
        "websocket_latency": 0.1,  # 100ms
        "concurrent_tasks": 10
    }

