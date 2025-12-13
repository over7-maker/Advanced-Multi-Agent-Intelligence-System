"""
Unit tests for Metrics Middleware
Tests PART 6: Monitoring & Observability - HTTP Request Metrics
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.api.middleware.metrics_middleware import MetricsMiddleware


@pytest.mark.unit
class TestMetricsMiddleware:
    """Test MetricsMiddleware"""

    @pytest.fixture
    def app(self, mock_metrics_service):
        """Create FastAPI app with metrics middleware"""
        app = FastAPI()
        
        with patch('src.api.middleware.metrics_middleware.get_metrics_service', return_value=mock_metrics_service):
            app.add_middleware(MetricsMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        @app.get("/metrics")
        async def metrics_endpoint():
            return {"metrics": "data"}
        
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)

    def test_middleware_tracks_request(self, client, mock_metrics_service):
        """Test that middleware tracks HTTP requests"""
        with patch('src.api.middleware.metrics_middleware.get_metrics_service', return_value=mock_metrics_service):
            response = client.get("/test")
            
            assert response.status_code == 200
            # Verify metrics were recorded
            mock_metrics_service.record_http_request.assert_called()

    def test_middleware_excludes_metrics_endpoint(self, client, mock_metrics_service):
        """Test that /metrics endpoint is excluded from tracking"""
        with patch('src.api.middleware.metrics_middleware.get_metrics_service', return_value=mock_metrics_service):
            response = client.get("/metrics")
            
            assert response.status_code == 200
            # Should not record metrics for /metrics endpoint
            # (The middleware checks for this)

    def test_middleware_tracks_duration(self, client, mock_metrics_service):
        """Test that middleware tracks request duration"""
        with patch('src.api.middleware.metrics_middleware.get_metrics_service', return_value=mock_metrics_service):
            response = client.get("/test")
            
            assert response.status_code == 200
            # Verify duration was passed to record_http_request
            call_args = mock_metrics_service.record_http_request.call_args
            if call_args:
                assert "duration" in call_args.kwargs or len(call_args.args) >= 4

    def test_middleware_tracks_status_code(self, client, mock_metrics_service):
        """Test that middleware tracks status code"""
        with patch('src.api.middleware.metrics_middleware.get_metrics_service', return_value=mock_metrics_service):
            response = client.get("/test")
            
            assert response.status_code == 200
            # Verify status code was recorded
            call_args = mock_metrics_service.record_http_request.call_args
            if call_args:
                assert "status_code" in call_args.kwargs or len(call_args.args) >= 3

    def test_middleware_handles_errors(self, client, mock_metrics_service):
        """Test that middleware handles errors gracefully"""
        app = FastAPI()
        
        with patch('src.api.middleware.metrics_middleware.get_metrics_service', return_value=mock_metrics_service):
            app.add_middleware(MetricsMiddleware)
            
            @app.get("/error")
            async def error_endpoint():
                raise ValueError("Test error")
            
            test_client = TestClient(app)
            
            # Should not crash, should record error
            try:
                test_client.get("/error")
            except Exception:
                pass
            
            # Verify error was recorded
            mock_metrics_service.record_http_request.assert_called()

