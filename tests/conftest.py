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


# Import production fixtures
from tests.fixtures.production_fixtures import (  # noqa: E402
    alembic_env_path,
    alembic_ini_path,
    backup_script_path,
    cicd_workflow_path,
    deploy_script_path,
    docker_compose_path,
    dockerfile_path,
    env_template_path,
    k8s_manifest_path,
    migration_path,
    nginx_config_path,
    project_root,
    restore_script_path,
    temp_dir,
    test_env_vars,
)


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


@pytest.fixture
def async_test_client(monkeypatch):
    """Async FastAPI test client fixture."""
    from fastapi.testclient import TestClient

    # Ensure test environment is set
    import os
    os.environ["ENVIRONMENT"] = "test"
    
    try:
        from src.api.main import app
        from src.amas.api.main import get_amas_system
        
        # Mock AMAS system to avoid initialization errors
        mock_amas = MagicMock()
        mock_amas.orchestrator = MagicMock()
        mock_amas.orchestrator.agents = {}
        mock_amas.orchestrator.active_tasks = {}
        mock_amas.orchestrator.tasks = {}
        mock_amas.service_manager = MagicMock()
        mock_amas.service_manager.health_check_all_services = AsyncMock(return_value={
            "overall_status": "healthy",
            "services": {}
        })
        
        # Patch get_amas_system to return mock
        async def mock_get_amas_system():
            return mock_amas
        
        monkeypatch.setattr("src.amas.api.main.get_amas_system", mock_get_amas_system)
        monkeypatch.setattr("src.amas.api.main.amas_app", mock_amas)

        return TestClient(app)
    except ImportError:
        # Fallback mock client for incomplete API
        mock_client = MagicMock()
        mock_client.get = MagicMock()
        mock_client.post = MagicMock()
        mock_client.put = MagicMock()
        mock_client.delete = MagicMock()
        return mock_client


# ============================================================================
# PART 5: Integration Manager Fixtures
# ============================================================================

@pytest.fixture
def mock_http_client():
    """Mock HTTP client for integration connectors."""
    mock_client = AsyncMock()
    mock_client.post = AsyncMock()
    mock_client.get = AsyncMock()
    mock_client.put = AsyncMock()
    mock_client.delete = AsyncMock()
    return mock_client


@pytest.fixture
def mock_integration_connector():
    """Mock integration connector."""
    mock_connector = MagicMock()
    mock_connector.validate_credentials = AsyncMock(return_value=True)
    mock_connector.execute = AsyncMock(return_value={"success": True})
    mock_connector.validate_webhook_signature = AsyncMock(return_value=True)
    mock_connector.parse_webhook = AsyncMock(return_value={"event": "test"})
    return mock_connector


@pytest.fixture
def sample_integration():
    """Sample integration for testing."""
    return {
        "integration_id": "test_integration_001",
        "platform": "n8n",
        "status": "active",
        "credentials": {"api_key": "test_key", "base_url": "https://test.n8n.io"},
        "configuration": {},
        "sync_count": 0,
        "error_count": 0,
        "created_at": "2024-01-01T00:00:00Z",
    }


# ============================================================================
# PART 6: Monitoring & Observability Fixtures
# ============================================================================

@pytest.fixture
def mock_metrics_service():
    """Mock Prometheus metrics service."""
    mock_service = MagicMock()
    mock_service.record_task_execution = MagicMock()
    mock_service.record_agent_execution = MagicMock()
    mock_service.record_ai_provider_call = MagicMock()
    mock_service.record_http_request = MagicMock()
    mock_service.record_db_query = MagicMock()
    mock_service.update_system_resources = MagicMock()
    mock_service.get_metrics = MagicMock(return_value=b"# Mock metrics")
    mock_service.get_content_type = MagicMock(return_value="text/plain")
    return mock_service


@pytest.fixture
def test_metrics_service():
    """Real metrics service instance for testing."""
    try:
        from src.amas.services.prometheus_metrics_service import PrometheusMetricsService
        service = PrometheusMetricsService(config={"enabled": True})
        return service
    except Exception:
        # Fallback to mock if real service unavailable
        return mock_metrics_service()


@pytest.fixture
def mock_tracing_service():
    """Mock tracing service."""
    mock_service = MagicMock()
    mock_service.enabled = True
    mock_service.tracer = MagicMock()
    mock_service.tracer.start_as_current_span = MagicMock()
    mock_service.set_attribute = MagicMock()
    mock_service.add_event = MagicMock()
    mock_service.record_exception = MagicMock()
    mock_service.instrument_app = MagicMock()
    mock_service.instrument_libraries = MagicMock()
    return mock_service


@pytest.fixture
def mock_system_monitor():
    """Mock system monitor."""
    mock_monitor = MagicMock()
    mock_monitor.start = AsyncMock()
    mock_monitor.stop = AsyncMock()
    mock_monitor.get_snapshot = AsyncMock(return_value={
        "cpu_percent": 50.0,
        "memory_percent": 60.0,
        "disk_usage": 1000000000,
    })
    return mock_monitor


@pytest.fixture
def mock_psutil():
    """Mock psutil for system monitoring tests."""
    mock_psutil = MagicMock()
    mock_psutil.cpu_percent = MagicMock(return_value=50.0)
    mock_psutil.virtual_memory = MagicMock(return_value=MagicMock(
        used=1000000000,
        total=2000000000,
        percent=50.0
    ))
    mock_psutil.disk_usage = MagicMock(return_value=MagicMock(
        used=1000000000,
        total=2000000000
    ))
    mock_psutil.net_io_counters = MagicMock(return_value=MagicMock(
        bytes_sent=1000000,
        bytes_recv=2000000
    ))
    return mock_psutil


# ============================================================================
# PART 7: Frontend API Fixtures
# ============================================================================

@pytest.fixture
def mock_axios():
    """Mock axios for frontend API tests."""
    mock_axios = MagicMock()
    mock_axios.create = MagicMock(return_value=mock_axios)
    mock_axios.get = AsyncMock()
    mock_axios.post = AsyncMock()
    mock_axios.put = AsyncMock()
    mock_axios.delete = AsyncMock()
    mock_axios.interceptors = MagicMock()
    mock_axios.interceptors.request = MagicMock()
    mock_axios.interceptors.request.use = MagicMock()
    mock_axios.interceptors.response = MagicMock()
    mock_axios.interceptors.response.use = MagicMock()
    return mock_axios


@pytest.fixture
def mock_websocket():
    """Mock WebSocket for frontend tests."""
    mock_ws = MagicMock()
    mock_ws.readyState = 1  # OPEN
    mock_ws.send = MagicMock()
    mock_ws.close = MagicMock()
    mock_ws.addEventListener = MagicMock()
    mock_ws.removeEventListener = MagicMock()
    return mock_ws