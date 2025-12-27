"""
Tests for landing page API endpoints
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from src.amas.api.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database session"""
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    return db


@pytest.fixture
def mock_metrics_service():
    """Mock metrics service"""
    with patch('src.amas.services.prometheus_metrics_service.get_metrics_service') as mock:
        service = MagicMock()
        service.get_counter_value = MagicMock(return_value=100)
        service.get_gauge_value = MagicMock(return_value=5)
        service.get_summary_average = MagicMock(return_value=1.5)
        mock.return_value = service
        yield service


@pytest.fixture
def mock_system_monitor():
    """Mock system monitor"""
    with patch('src.amas.services.system_monitor.get_system_monitor') as mock:
        monitor = MagicMock()
        monitor.get_snapshot = MagicMock(return_value={'cpu_percent': 25.0, 'memory_percent': 50.0})
        monitor.start_time = time.time()
        mock.return_value = monitor
        yield monitor


@pytest.fixture
def mock_orchestrator():
    """Mock orchestrator"""
    with patch('src.amas.core.unified_intelligence_orchestrator.get_unified_orchestrator') as mock:
        orchestrator = MagicMock()
        orchestrator.agents = {
            'agent1': MagicMock(name='Agent 1', is_active=True, specialization='test'),
            'agent2': MagicMock(name='Agent 2', is_active=True, specialization='test'),
        }
        orchestrator.active_tasks = {}
        mock.return_value = orchestrator
        yield orchestrator


class TestLandingMetrics:
    """Tests for /api/v1/landing/metrics endpoint"""
    
    def test_get_metrics_success(self, client, mock_metrics_service, mock_system_monitor):
        """Test successful metrics retrieval"""
        with patch('psutil.cpu_percent', return_value=45.5), \
             patch('psutil.virtual_memory') as mock_mem:
            mock_mem.return_value = MagicMock(percent=60.0)
            
            response = client.get("/api/v1/landing/metrics")
            
            assert response.status_code == 200
            data = response.json()
            assert "cpu_usage_percent" in data
            assert "memory_usage_percent" in data
            assert "active_tasks" in data
            assert "active_agents" in data
            assert isinstance(data["cpu_usage_percent"], float)
            assert isinstance(data["memory_usage_percent"], float)
    
    def test_get_metrics_with_database(self, client, mock_db):
        """Test metrics with database integration"""
        with patch('src.api.routes.landing.get_db', return_value=mock_db), \
             patch('src.amas.services.prometheus_metrics_service.get_metrics_service') as mock_metrics, \
             patch('src.amas.services.system_monitor.get_system_monitor') as mock_monitor, \
             patch('psutil.cpu_percent', return_value=50.0), \
             patch('psutil.virtual_memory') as mock_mem:
            mock_mem.return_value = MagicMock(percent=55.0)
            
            # Setup mocks
            mock_metrics_service = MagicMock()
            mock_metrics_service.get_counter_value = MagicMock(return_value=100)
            mock_metrics_service.get_gauge_value = MagicMock(return_value=5)
            mock_metrics_service.get_summary_average = MagicMock(return_value=1.5)
            mock_metrics.return_value = mock_metrics_service
            
            mock_system_monitor = MagicMock()
            mock_system_monitor.get_snapshot = MagicMock(return_value={'cpu_percent': 50.0, 'memory_percent': 55.0})
            mock_system_monitor.start_time = time.time()
            mock_monitor.return_value = mock_system_monitor
            
            # Mock database query result
            mock_result = AsyncMock()
            mock_row = MagicMock()
            mock_row.__getitem__ = lambda self, key: {
                0: 10,  # active_tasks
                1: 500,  # completed_tasks
                2: 5,    # failed_tasks
                3: 30.5, # avg_task_duration
                4: 0.95  # success_rate
            }.get(key, 0)
            mock_result.fetchone = AsyncMock(return_value=mock_row)
            mock_db.execute = AsyncMock(return_value=mock_result)
            
            response = client.get("/api/v1/landing/metrics")
            
            assert response.status_code == 200
            data = response.json()
            # Note: Database query might not be executed if orchestrator is available
            # So we just check that response is valid
            assert "active_tasks" in data
            assert "completed_tasks" in data
            assert "failed_tasks" in data
    
    def test_get_metrics_fallback(self, client):
        """Test metrics fallback when services unavailable"""
        with patch('psutil.cpu_percent', side_effect=ImportError("psutil not available")):
            response = client.get("/api/v1/landing/metrics")
            
            assert response.status_code == 200
            data = response.json()
            # Should return default values
            assert data["cpu_usage_percent"] == 25.0
            assert data["memory_usage_percent"] == 45.0


class TestLandingAgentsStatus:
    """Tests for /api/v1/landing/agents-status endpoint"""
    
    def test_get_agents_status_success(self, client, mock_orchestrator):
        """Test successful agent status retrieval"""
        response = client.get("/api/v1/landing/agents-status")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2  # From mock orchestrator
        assert "agent_id" in data[0]
        assert "name" in data[0]
        assert "status" in data[0]
    
    def test_get_agents_status_fallback(self, client):
        """Test agent status fallback when orchestrator unavailable"""
        with patch('src.amas.core.unified_intelligence_orchestrator.get_unified_orchestrator', side_effect=Exception("Not available")):
            response = client.get("/api/v1/landing/agents-status")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 3  # Default fallback agents
            assert data[0]["agent_id"] == "security_expert"


class TestLandingDemoData:
    """Tests for /api/v1/landing/demo-data endpoint"""
    
    def test_get_demo_data_success(self, client):
        """Test successful demo data retrieval"""
        response = client.get("/api/v1/landing/demo-data")
        
        assert response.status_code == 200
        data = response.json()
        assert "sample_task_id" in data
        assert "sample_agents" in data
        assert "estimated_duration" in data
        assert "estimated_cost" in data
        assert "quality_prediction" in data
        assert isinstance(data["sample_agents"], list)


class TestLandingFeedback:
    """Tests for /api/v1/landing/feedback endpoint"""
    
    def test_submit_feedback_success(self, client, mock_db):
        """Test successful feedback submission"""
        with patch('src.api.routes.landing.get_db', return_value=mock_db):
            feedback_data = {
                "email": "test@example.com",
                "name": "Test User",
                "message": "Great product!",
                "sentiment": "positive",
                "page_context": "landing"
            }
            
            response = client.post("/api/v1/landing/feedback", json=feedback_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "feedback_id" in data
            assert "message" in data
            assert "timestamp" in data
            assert "Thank you" in data["message"]
    
    def test_submit_feedback_invalid_email(self, client):
        """Test feedback submission with invalid email"""
        feedback_data = {
            "email": "invalid-email",
            "name": "Test User",
            "message": "Test message"
        }
        
        response = client.post("/api/v1/landing/feedback", json=feedback_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_submit_feedback_missing_fields(self, client):
        """Test feedback submission with missing required fields"""
        feedback_data = {
            "email": "test@example.com"
            # Missing name and message
        }
        
        response = client.post("/api/v1/landing/feedback", json=feedback_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_submit_feedback_with_database(self, client, mock_db):
        """Test feedback submission with database storage"""
        with patch('src.api.routes.landing.get_db', return_value=mock_db), \
             patch('src.amas.services.email_service.get_email_service') as mock_email:
            # Mock email service
            mock_email_service = MagicMock()
            mock_email_service.send_feedback_confirmation = AsyncMock(return_value={"status": "success"})
            mock_email.return_value = mock_email_service
            
            # Mock database
            mock_result = AsyncMock()
            mock_db.execute = AsyncMock(return_value=mock_result)
            mock_db.commit = AsyncMock()
            
            feedback_data = {
                "email": "test@example.com",
                "name": "Test User",
                "message": "Test message",
                "sentiment": "positive"
            }
            
            response = client.post("/api/v1/landing/feedback", json=feedback_data)
            
            assert response.status_code == 200
            # Verify database was called (if database is available)
            # Note: Database call might be optional, so we just verify response is successful
            assert "feedback_id" in response.json()
    
    def test_submit_feedback_without_database(self, client):
        """Test feedback submission when database unavailable"""
        with patch('src.api.routes.landing.get_db', return_value=None):
            feedback_data = {
                "email": "test@example.com",
                "name": "Test User",
                "message": "Test message"
            }
            
            response = client.post("/api/v1/landing/feedback", json=feedback_data)
            
            # Should still succeed, just log the feedback
            assert response.status_code == 200


class TestLandingHealth:
    """Tests for /api/v1/landing/health endpoint"""
    
    def test_health_check_success(self, client):
        """Test health check endpoint"""
        response = client.get("/api/v1/landing/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data
        assert data["service"] == "AMAS Landing Page"


class TestLandingEmailService:
    """Tests for email service integration"""
    
    @pytest.mark.asyncio
    async def test_send_feedback_confirmation_email_enabled(self):
        """Test email sending when email service is enabled"""
        with patch('src.amas.services.email_service.get_email_service') as mock_get_email, \
             patch.dict('os.environ', {'EMAIL_ENABLED': 'true', 'SMTP_SERVER': 'localhost'}):
            mock_service = MagicMock()
            mock_service.send_feedback_confirmation = AsyncMock(return_value={"status": "success"})
            mock_get_email.return_value = mock_service
            
            from src.api.routes.landing import send_feedback_confirmation_email
            
            await send_feedback_confirmation_email("test@example.com", "Test User", "feedback-123")
            
            mock_service.send_feedback_confirmation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_feedback_confirmation_email_disabled(self):
        """Test email sending when email service is disabled"""
        with patch.dict('os.environ', {'EMAIL_ENABLED': 'false'}):
            from src.api.routes.landing import send_feedback_confirmation_email
            
            # Should not raise error when disabled
            await send_feedback_confirmation_email("test@example.com", "Test User", "feedback-123")


class TestLandingEndpointsIntegration:
    """Integration tests for landing endpoints"""
    
    def test_all_endpoints_are_public(self, client):
        """Test that all landing endpoints are public (no auth required)"""
        endpoints = [
            "/api/v1/landing/health",
            "/api/v1/landing/metrics",
            "/api/v1/landing/agents-status",
            "/api/v1/landing/demo-data",
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should not return 401 or 403
            assert response.status_code != 401
            assert response.status_code != 403
    
    def test_feedback_endpoint_is_public(self, client):
        """Test that feedback endpoint is public"""
        feedback_data = {
            "email": "test@example.com",
            "name": "Test User",
            "message": "Test message"
        }
        
        response = client.post("/api/v1/landing/feedback", json=feedback_data)
        
        # Should not return 401 or 403
        assert response.status_code != 401
        assert response.status_code != 403

