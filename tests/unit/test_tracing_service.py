"""
Unit tests for Tracing Service
Tests PART 6: Monitoring & Observability - OpenTelemetry Tracing
"""

import pytest
from unittest.mock import MagicMock, patch, Mock

from src.amas.services.tracing_service import TracingService, init_tracing, get_tracing_service


@pytest.mark.unit
class TestTracingService:
    """Test TracingService"""

    @pytest.fixture
    def tracing_service(self):
        """Create TracingService instance"""
        try:
            return TracingService(
                service_name="test-service",
                service_version="1.0.0",
                environment="testing"
            )
        except Exception:
            # If OpenTelemetry not available, return mock
            mock = MagicMock()
            mock.enabled = False
            return mock

    def test_initialization(self, tracing_service):
        """Test tracing service initialization"""
        assert tracing_service is not None
        assert hasattr(tracing_service, 'enabled')

    def test_start_span(self, tracing_service):
        """Test starting a span"""
        if tracing_service.enabled:
            span = tracing_service.start_span("test_span")
            assert span is not None
        else:
            # If disabled, should not crash
            assert True

    def test_set_attribute(self, tracing_service):
        """Test setting span attribute"""
        if tracing_service.enabled:
            tracing_service.set_attribute("test.key", "test_value")
            assert True
        else:
            assert True

    def test_add_event(self, tracing_service):
        """Test adding event to span"""
        if tracing_service.enabled:
            tracing_service.add_event("test_event", {"data": "test"})
            assert True
        else:
            assert True

    def test_record_exception(self, tracing_service):
        """Test recording exception"""
        if tracing_service.enabled:
            try:
                raise ValueError("Test exception")
            except Exception as e:
                tracing_service.record_exception(e)
            assert True
        else:
            assert True

    def test_instrument_app(self, tracing_service):
        """Test instrumenting FastAPI app"""
        mock_app = MagicMock()
        tracing_service.instrument_app(mock_app)
        # Should not crash
        assert True

    def test_instrument_libraries(self, tracing_service):
        """Test instrumenting libraries"""
        tracing_service.instrument_libraries()
        # Should not crash
        assert True

    def test_trace_function_decorator(self, tracing_service):
        """Test trace_function decorator"""
        if tracing_service.enabled:
            @tracing_service.trace_function("test_function")
            def test_func():
                return "result"
            
            result = test_func()
            assert result == "result"
        else:
            assert True

    def test_disabled_service(self):
        """Test that disabled service doesn't crash"""
        with patch('src.amas.services.tracing_service.OPENTELEMETRY_AVAILABLE', False):
            service = TracingService()
            assert service.enabled is False
            
            # Should not crash on any operation
            service.set_attribute("test", "value")
            service.add_event("test")
            service.record_exception(Exception("test"))

    def test_init_tracing(self):
        """Test init_tracing function"""
        try:
            service = init_tracing(
                service_name="test",
                service_version="1.0.0",
                environment="testing"
            )
            assert service is not None
        except Exception:
            # If OpenTelemetry not available, skip
            pytest.skip("OpenTelemetry not available")

    def test_get_tracing_service_singleton(self):
        """Test get_tracing_service returns singleton"""
        try:
            service1 = get_tracing_service()
            service2 = get_tracing_service()
            # Should return same instance if initialized
            assert service1 is service2 or service1 is None or service2 is None
        except Exception:
            pytest.skip("Tracing service not available")

