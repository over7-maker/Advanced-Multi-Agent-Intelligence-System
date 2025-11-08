"""
Unit tests for AMAS Observability Framework - OpenTelemetry Integration
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch

from src.amas.observability.tracing.tracer import (
    AmasTracer,
    initialize_observability,
    get_tracer
)


class TestAmasTracer:
    """Test cases for AmasTracer"""
    
    @pytest.fixture
    def tracer(self):
        """Create a tracer instance for testing"""
        with patch('src.amas.observability.tracing.tracer.OTLPSpanExporter'):
            with patch('src.amas.observability.tracing.tracer.OTLPMetricExporter'):
                tracer = AmasTracer(
                    service_name="test-service",
                    service_version="1.0.0",
                    otlp_endpoint="http://localhost:4317",
                    environment="test"
                )
                return tracer
    
    def test_tracer_initialization(self, tracer):
        """Test tracer initialization"""
        assert tracer.service_name == "test-service"
        assert tracer.service_version == "1.0.0"
        assert tracer.environment == "test"
        assert tracer.tracer is not None
        assert tracer.meter is not None
    
    @pytest.mark.asyncio
    async def test_trace_agent_execution_success(self, tracer):
        """Test tracing successful agent execution"""
        async with tracer.trace_agent_execution(
            agent_id="test_agent",
            operation="test_operation"
        ) as span:
            # Simulate some work
            await asyncio.sleep(0.01)
            assert span is not None
    
    @pytest.mark.asyncio
    async def test_trace_agent_execution_error(self, tracer):
        """Test tracing agent execution with error"""
        with pytest.raises(ValueError):
            async with tracer.trace_agent_execution(
                agent_id="test_agent",
                operation="test_operation"
            ):
                raise ValueError("Test error")
    
    @pytest.mark.asyncio
    async def test_trace_tool_call(self, tracer):
        """Test tracing tool calls"""
        async with tracer.trace_tool_call(
            agent_id="test_agent",
            tool_name="test_tool",
            parameters={"param1": "value1"}
        ) as span:
            assert span is not None
    
    def test_sanitize_parameters(self, tracer):
        """Test parameter sanitization"""
        params = {
            "password": "secret123",
            "api_key": "key123",
            "normal_param": "value",
            "token": "token123"
        }
        
        sanitized = tracer._sanitize_parameters(params)
        
        assert sanitized["password"] == "***REDACTED***"
        assert sanitized["api_key"] == "***REDACTED***"
        assert sanitized["token"] == "***REDACTED***"
        assert sanitized["normal_param"] == "value"
    
    def test_instrument_fastapi(self, tracer):
        """Test FastAPI instrumentation"""
        from fastapi import FastAPI
        app = FastAPI()
        
        # Should not raise exception
        tracer.instrument_fastapi(app)
        assert True
    
    def test_validate_endpoint(self, tracer):
        """Test endpoint validation"""
        # Valid endpoints
        assert tracer._validate_endpoint("http://localhost:4317") is True
        assert tracer._validate_endpoint("https://otel-collector:4317") is True
        
        # Invalid endpoints
        assert tracer._validate_endpoint("invalid-url") is False
        assert tracer._validate_endpoint("") is False
        assert tracer._validate_endpoint("ftp://example.com") is False
        
        # Endpoints with credentials should be rejected
        assert tracer._validate_endpoint("http://user:pass@localhost:4317") is False
    
    def test_record_token_usage(self, tracer):
        """Test recording token usage"""
        tracer.record_token_usage(
            agent_id="test_agent",
            tokens_used=1000,
            cost_usd=0.01,
            model_name="test-model"
        )
        # Metrics should be recorded (no exception means success)
        assert True
    
    def test_get_current_trace_id(self, tracer):
        """Test getting current trace ID"""
        trace_id = tracer.get_current_trace_id()
        # May be None if no active span
        assert trace_id is None or isinstance(trace_id, str)


class TestObservabilityIntegration:
    """Test cases for SLOManager"""
    
    @pytest.fixture
    def slo_config_file(self):
        """Create a temporary SLO configuration file"""
        config = {
            "slos": [
                {
                    "name": "test_availability",
                    "description": "Test availability SLO",
                    "metric_query": "test_query",
                    "threshold": 99.5,
                    "comparison": ">=",
                    "window_minutes": 5,
                    "error_budget_percent": 0.5,
                    "severity": "critical"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            yield f.name
        
        os.unlink(f.name)
    
    @pytest.fixture
    def slo_manager(self, slo_config_file):
        """Create SLO manager instance"""
        with patch('src.amas.observability.slo_manager.requests.get') as mock_get:
            # Mock Prometheus responses
            mock_response = Mock()
            mock_response.json.return_value = {
                "status": "success",
                "data": {
                    "result": [{"value": [1234567890, "99.8"]}]
                }
            }
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            manager = SLOManager(
                prometheus_url="http://localhost:9090",
                slo_config_path=slo_config_file
            )
            return manager
    
    def test_slo_manager_initialization(self, slo_manager):
        """Test SLO manager initialization"""
        assert len(slo_manager.slo_definitions) == 1
        assert "test_availability" in slo_manager.slo_definitions
    
    def test_load_slo_definitions(self, slo_manager):
        """Test loading SLO definitions"""
        assert "test_availability" in slo_manager.slo_definitions
        slo = slo_manager.slo_definitions["test_availability"]
        assert slo.threshold == 99.5
        assert slo.comparison == ">="
    
    def test_check_compliance(self, slo_manager):
        """Test compliance checking"""
        # Test >= comparison
        assert slo_manager._check_compliance(100.0, 99.5, ">=") is True
        assert slo_manager._check_compliance(99.0, 99.5, ">=") is False
        
        # Test <= comparison
        assert slo_manager._check_compliance(1.0, 1.5, "<=") is True
        assert slo_manager._check_compliance(2.0, 1.5, "<=") is False
    
    def test_evaluate_slo(self, slo_manager):
        """Test SLO evaluation"""
        status = slo_manager.evaluate_slo("test_availability")
        
        assert status is not None
        assert status.slo_name == "test_availability"
        assert status.current_value == 99.8
        assert status.status in ["compliant", "violated", "warning", "critical"]
    
    def test_get_slo_status(self, slo_manager):
        """Test getting SLO status"""
        status = slo_manager.get_slo_status("test_availability")
        assert status is not None
        assert isinstance(status, SLOStatus)
    
    def test_get_violations(self, slo_manager):
        """Test getting violations"""
        violations = slo_manager.get_violations()
        assert isinstance(violations, list)
    
    def test_parse_time_window(self, slo_manager):
        """Test parsing time windows"""
        assert slo_manager._parse_time_window("5m") == 5
        assert slo_manager._parse_time_window("1h") == 60
        assert slo_manager._parse_time_window("2d") == 2880
    
    def test_detect_performance_regression(self, slo_manager):
        """Test performance regression detection"""
        # No baseline yet
        regression = slo_manager.detect_performance_regression("test_op", 2.0)
        assert regression is None  # Should establish baseline
        
        # Now test with regression
        regression = slo_manager.detect_performance_regression("test_op", 4.0)  # 2x baseline
        assert regression is not None
        assert regression["type"] == "latency_regression"
        assert regression["severity"] in ["medium", "high"]


class TestObservabilityIntegration:
    """Integration tests for observability system"""
    
    @pytest.mark.asyncio
    async def test_initialize_observability(self):
        """Test initializing observability system"""
        with patch('src.amas.observability.tracing.tracer.OTLPSpanExporter'):
            with patch('src.amas.observability.tracing.tracer.OTLPMetricExporter'):
                tracer = initialize_observability(
                    service_name="test-service",
                    service_version="1.0.0"
                )
                assert tracer is not None
                assert tracer.service_name == "test-service"
    
    def test_get_tracer(self):
        """Test getting tracer instance"""
        with patch('src.amas.observability.tracing.tracer.OTLPSpanExporter'):
            with patch('src.amas.observability.tracing.tracer.OTLPMetricExporter'):
                tracer = get_tracer()
                assert tracer is not None
    
    @pytest.mark.asyncio
    async def test_trace_decorator(self):
        """Test tracing decorator"""
        from src.amas.observability.tracing.tracer import trace_agent_operation
        
        @trace_agent_operation("test_operation")
        async def test_function():
            return "success"
        
        with patch('src.amas.observability.tracing.tracer.get_tracer'):
            result = await test_function()
            assert result == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
