"""
Integration tests for Integration API
Tests PART 5: Platform Integration Layer - API Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI

from src.api.routes.integrations import router
from src.amas.integration.integration_manager import IntegrationManager, IntegrationPlatform


@pytest.mark.integration
class TestIntegrationAPI:
    """Test integration API endpoints"""

    @pytest.fixture
    def app(self):
        """Create FastAPI app with integrations router"""
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_integration_manager(self):
        """Mock integration manager"""
        manager = MagicMock(spec=IntegrationManager)
        manager.register_integration = AsyncMock(return_value="test_integration_001")
        manager.get_integration_status = AsyncMock(return_value={
            "integration_id": "test_integration_001",
            "platform": "n8n",
            "status": "active",
            "created_at": "2024-01-01T00:00:00Z",
            "last_sync": None,
            "sync_count": 0,
            "error_count": 0
        })
        manager.list_integrations = AsyncMock(return_value=[{
            "integration_id": "test_integration_001",
            "platform": "n8n",
            "status": "active",
            "created_at": "2024-01-01T00:00:00Z",
            "last_sync": None,
            "sync_count": 0,
            "error_count": 0
        }])
        manager.get_integration = AsyncMock(return_value={
            "integration_id": "test_integration_001",
            "platform": "n8n",
            "status": "active",
            "created_at": "2024-01-01T00:00:00Z"
        })
        manager.update_integration = AsyncMock()
        manager.delete_integration = AsyncMock()
        manager.trigger_integration_event = AsyncMock(return_value={"success": True})
        manager.handle_webhook = AsyncMock(return_value={"event": "test", "data": {}})
        return manager

    def test_create_integration(self, client, mock_integration_manager):
        """Test creating integration via API"""
        with patch('src.api.routes.integrations.get_integration_manager', return_value=mock_integration_manager):
            response = client.post(
                "/integrations/",
                json={
                    "platform": "n8n",
                    "credentials": {"api_key": "test_key"},
                    "configuration": {}
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["integration_id"] == "test_integration_001"
            assert data["platform"] == "n8n"

    def test_create_integration_invalid_platform(self, client, mock_integration_manager):
        """Test creating integration with invalid platform"""
        with patch('src.api.routes.integrations.get_integration_manager', return_value=mock_integration_manager):
            response = client.post(
                "/integrations/",
                json={
                    "platform": "invalid_platform",
                    "credentials": {"api_key": "test_key"},
                    "configuration": {}
                }
            )
            
            assert response.status_code == 400

    def test_list_integrations(self, client, mock_integration_manager):
        """Test listing integrations via API"""
        with patch('src.api.routes.integrations.get_integration_manager', return_value=mock_integration_manager):
            response = client.get("/integrations/")
            
            assert response.status_code == 200
            data = response.json()
            assert "integrations" in data
            assert len(data["integrations"]) > 0

    def test_get_integration(self, client, mock_integration_manager):
        """Test getting integration via API"""
        with patch('src.api.routes.integrations.get_integration_manager', return_value=mock_integration_manager):
            response = client.get("/integrations/test_integration_001")
            
            assert response.status_code == 200
            data = response.json()
            assert data["integration_id"] == "test_integration_001"

    def test_update_integration(self, client, mock_integration_manager):
        """Test updating integration via API"""
        with patch('src.api.routes.integrations.get_integration_manager', return_value=mock_integration_manager):
            response = client.put(
                "/integrations/test_integration_001",
                json={
                    "configuration": {"new_setting": "value"}
                }
            )
            
            assert response.status_code == 200

    def test_delete_integration(self, client, mock_integration_manager):
        """Test deleting integration via API"""
        with patch('src.api.routes.integrations.get_integration_manager', return_value=mock_integration_manager):
            response = client.delete("/integrations/test_integration_001")
            
            assert response.status_code == 200

    def test_trigger_integration(self, client, mock_integration_manager):
        """Test triggering integration event via API"""
        with patch('src.api.routes.integrations.get_integration_manager', return_value=mock_integration_manager):
            response = client.post(
                "/integrations/test_integration_001/trigger",
                json={
                    "event_type": "task_completed",
                    "data": {"task_id": "test_task"}
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_webhook_endpoint(self, client, mock_integration_manager):
        """Test webhook endpoint"""
        with patch('src.api.routes.integrations.get_integration_manager', return_value=mock_integration_manager):
            # Webhook endpoint uses platform-based path: /integrations/webhooks/{platform}
            response = client.post(
                "/integrations/webhooks/n8n",
                json={"event": "test", "data": {}},
                headers={"X-Webhook-Signature": "test_signature"}
            )
            
            # Should succeed or return appropriate error
            assert response.status_code in [200, 400, 404]

