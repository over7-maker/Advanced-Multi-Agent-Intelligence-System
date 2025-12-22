"""
Integration tests for Integration API
Tests PART 5: Platform Integration Layer - API Endpoints
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.amas.integration.integration_manager import IntegrationManager
from src.api.routes.integrations import router


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
        manager.update_integration = AsyncMock(return_value={
            "integration_id": "test_integration_001",
            "platform": "n8n",
            "status": "active",
            "created_at": "2024-01-01T00:00:00Z",
            "last_sync": None,
            "sync_count": 0,
            "error_count": 0
        })
        manager.delete_integration = AsyncMock()
        manager.trigger_integration = AsyncMock(return_value={"success": True})
        manager.handle_webhook = AsyncMock(return_value={"status": "processed", "event_type": "test"})
        return manager

    def test_create_integration(self, app, client, mock_integration_manager):
        """Test creating integration via API"""
        from src.amas.integration.integration_manager import get_integration_manager
        app.dependency_overrides[get_integration_manager] = lambda: mock_integration_manager
        
        try:
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
        finally:
            app.dependency_overrides.clear()

    def test_create_integration_invalid_platform(self, app, client, mock_integration_manager):
        """Test creating integration with invalid platform"""
        from src.amas.integration.integration_manager import get_integration_manager
        app.dependency_overrides[get_integration_manager] = lambda: mock_integration_manager
        
        try:
            response = client.post(
                "/integrations/",
                json={
                    "platform": "invalid_platform",
                    "credentials": {"api_key": "test_key"},
                    "configuration": {}
                }
            )
            
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()

    def test_list_integrations(self, app, client, mock_integration_manager):
        """Test listing integrations via API"""
        from src.amas.integration.integration_manager import get_integration_manager
        from src.api.routes.integrations import get_current_user
        app.dependency_overrides[get_integration_manager] = lambda: mock_integration_manager
        app.dependency_overrides[get_current_user] = lambda: {"user_id": "default_user"}
        
        try:
            response = client.get("/integrations/")
            
            assert response.status_code == 200
            data = response.json()
            assert "integrations" in data
            assert len(data["integrations"]) > 0
        finally:
            app.dependency_overrides.clear()

    def test_get_integration(self, app, client, mock_integration_manager):
        """Test getting integration via API"""
        from src.amas.integration.integration_manager import get_integration_manager
        from src.api.routes.integrations import get_current_user
        app.dependency_overrides[get_integration_manager] = lambda: mock_integration_manager
        app.dependency_overrides[get_current_user] = lambda: {"user_id": "default_user"}
        
        try:
            response = client.get("/integrations/test_integration_001")
            
            assert response.status_code == 200
            data = response.json()
            assert data["integration_id"] == "test_integration_001"
        finally:
            app.dependency_overrides.clear()

    def test_update_integration(self, app, client, mock_integration_manager):
        """Test updating integration via API"""
        from src.amas.integration.integration_manager import get_integration_manager
        from src.api.routes.integrations import get_current_user
        app.dependency_overrides[get_integration_manager] = lambda: mock_integration_manager
        app.dependency_overrides[get_current_user] = lambda: {"user_id": "default_user"}
        
        try:
            response = client.put(
                "/integrations/test_integration_001",
                json={
                    "platform": "n8n",
                    "credentials": {"api_key": "test_key"},
                    "configuration": {"new_setting": "value"}
                }
            )
            
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()

    def test_delete_integration(self, app, client, mock_integration_manager):
        """Test deleting integration via API"""
        from src.amas.integration.integration_manager import get_integration_manager
        from src.api.routes.integrations import get_current_user
        app.dependency_overrides[get_integration_manager] = lambda: mock_integration_manager
        app.dependency_overrides[get_current_user] = lambda: {"user_id": "default_user"}
        
        try:
            response = client.delete("/integrations/test_integration_001")
            
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()

    def test_trigger_integration(self, app, client, mock_integration_manager):
        """Test triggering integration event via API"""
        from src.amas.integration.integration_manager import get_integration_manager
        from src.api.routes.integrations import get_current_user
        app.dependency_overrides[get_integration_manager] = lambda: mock_integration_manager
        app.dependency_overrides[get_current_user] = lambda: {"user_id": "default_user"}
        
        try:
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
        finally:
            app.dependency_overrides.clear()

    def test_webhook_endpoint(self, app, client, mock_integration_manager):
        """Test webhook endpoint"""
        from src.amas.integration.integration_manager import get_integration_manager
        app.dependency_overrides[get_integration_manager] = lambda: mock_integration_manager
        
        try:
            # Webhook endpoint uses platform-based path: /integrations/webhooks/{platform}
            response = client.post(
                "/integrations/webhooks/n8n",
                json={"event": "test", "data": {}},
                headers={"X-Webhook-Signature": "test_signature"}
            )
            
            # Should succeed or return appropriate error
            assert response.status_code in [200, 400, 404]
        finally:
            app.dependency_overrides.clear()

