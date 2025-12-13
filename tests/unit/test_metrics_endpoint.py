"""
Unit tests for Metrics Endpoint
Tests PART 6: Monitoring & Observability - Metrics API
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.api.routes.metrics import router
from fastapi import FastAPI


@pytest.mark.unit
class TestMetricsEndpoint:
    """Test metrics API endpoints"""

    @pytest.fixture
    def app(self):
        """Create FastAPI app with metrics router"""
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)

    def test_metrics_endpoint(self, client, mock_metrics_service):
        """Test /metrics endpoint"""
        with patch('src.api.routes.metrics.get_metrics_service', return_value=mock_metrics_service):
            response = client.get("/metrics")
            
            assert response.status_code == 200
            # Content type may include charset and version
            content_type = response.headers.get("content-type", "")
            assert "text/plain" in content_type

    def test_health_endpoint(self, client):
        """Test /health endpoint"""
        # Health endpoint might be at /health or /metrics/health
        response = client.get("/health")
        if response.status_code == 404:
            response = client.get("/metrics/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy" or data.get("status") == "ok"
        assert "timestamp" in data or "service" in data

    def test_metrics_content_type(self, client, mock_metrics_service):
        """Test metrics endpoint content type"""
        with patch('src.api.routes.metrics.get_metrics_service', return_value=mock_metrics_service):
            response = client.get("/metrics")
            
            # Content type should be text/plain (may have charset)
            content_type = response.headers.get("content-type", "")
            assert "text/plain" in content_type

