"""
Pytest configuration and fixtures for AMAS testing

This file provides shared fixtures and configuration for all AMAS tests.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from amas.core.unified_orchestrator import UnifiedIntelligenceOrchestrator
from amas.agents.osint.osint_agent import OSINTAgent
from amas.agents.forensics.forensics_agent import ForensicsAgent
from amas.config.minimal_config import get_minimal_config_manager, MinimalMode


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def temp_dir() -> Path:
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    import os
    original_env = os.environ.copy()
    
    # Set minimal required environment variables
    os.environ.update({
        "DEEPSEEK_API_KEY": "test_deepseek_key",
        "GLM_API_KEY": "test_glm_key",
        "GROK_API_KEY": "test_grok_key",
        "AMAS_CONFIG_MODE": "basic",
        "AMAS_DEBUG": "true"
    })
    
    yield os.environ
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
async def minimal_config_manager(mock_env_vars):
    """Create a minimal configuration manager for testing."""
    return get_minimal_config_manager(MinimalMode.BASIC)


@pytest.fixture
async def osint_agent(mock_env_vars):
    """Create an OSINT agent for testing."""
    agent = OSINTAgent()
    return agent


@pytest.fixture
async def forensics_agent(mock_env_vars):
    """Create a forensics agent for testing."""
    agent = ForensicsAgent()
    return agent


@pytest.fixture
async def unified_orchestrator(mock_env_vars):
    """Create a unified orchestrator for testing."""
    orchestrator = UnifiedIntelligenceOrchestrator()
    await orchestrator.initialize()
    yield orchestrator
    await orchestrator.shutdown()


@pytest.fixture
def mock_http_session():
    """Mock aiohttp session for testing."""
    session = AsyncMock()
    session.get = AsyncMock()
    session.close = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session


@pytest.fixture
def sample_html_content():
    """Sample HTML content for testing web scraping."""
    return """
    <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <h1>Welcome to Test Page</h1>
            <p>This is a test page for OSINT analysis.</p>
            <a href="https://example.com">Example Link</a>
            <img src="https://example.com/image.jpg" alt="Test Image">
            <div class="content">
                <p>Contact us at test@example.com</p>
                <p>Phone: +1-555-123-4567</p>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def sample_file_content():
    """Sample file content for testing forensics analysis."""
    return """This is a test file for forensics analysis.
It contains some sample text for testing purposes.
Email: test@example.com
URL: https://example.com
Phone: +1-555-123-4567
"""


@pytest.fixture
async def sample_file(temp_dir, sample_file_content):
    """Create a sample file for testing."""
    file_path = temp_dir / "test_file.txt"
    file_path.write_text(sample_file_content)
    return file_path


@pytest.fixture
def mock_provider_responses():
    """Mock responses from AI providers."""
    return {
        "deepseek": {
            "choices": [{"message": {"content": "Mock DeepSeek response"}}]
        },
        "glm": {
            "choices": [{"message": {"content": "Mock GLM response"}}]
        },
        "grok": {
            "choices": [{"message": {"content": "Mock Grok response"}}]
        }
    }


@pytest.fixture
def mock_circuit_breaker():
    """Mock circuit breaker for testing."""
    breaker = MagicMock()
    breaker.can_execute.return_value = True
    breaker.record_success = MagicMock()
    breaker.record_failure = MagicMock()
    return breaker


# Pytest markers for test categorization
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests"
    )
    config.addinivalue_line(
        "markers", "benchmark: Performance benchmark tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "real: Tests that use real external services"
    )
    config.addinivalue_line(
        "markers", "mock: Tests that use mocked services"
    )


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add markers based on test file names
        if "test_unified_orchestrator" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        if "e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
        
        if "benchmark" in item.nodeid:
            item.add_marker(pytest.mark.benchmark)
        
        # Add slow marker for tests that might take time
        if any(keyword in item.nodeid.lower() for keyword in ["real", "http", "file"]):
            item.add_marker(pytest.mark.slow)


# Test session hooks
def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    print("\n🚀 Starting AMAS Test Suite")
    print("=" * 50)


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished, right before returning the exit status."""
    if exitstatus == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit status: {exitstatus}")
    print("=" * 50)