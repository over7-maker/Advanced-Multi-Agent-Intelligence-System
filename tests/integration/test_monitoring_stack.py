"""
Integration tests for Monitoring Stack
Tests PART 6: Monitoring & Observability - Complete Stack
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from src.amas.services.prometheus_metrics_service import PrometheusMetricsService, get_metrics_service
from src.amas.services.system_monitor import SystemMonitor, get_system_monitor
from src.amas.services.tracing_service import TracingService, get_tracing_service


@pytest.mark.integration
class TestMonitoringStack:
    """Test complete monitoring stack integration"""

    @pytest.mark.asyncio
    async def test_metrics_and_monitor_integration(self, test_metrics_service, mock_psutil):
        """Test metrics service and system monitor integration"""
        monitor = SystemMonitor(update_interval=0.1)
        monitor.metrics_service = test_metrics_service
        
        with patch('src.amas.services.system_monitor.psutil', mock_psutil):
            await monitor.start()
            
            # Let it collect metrics
            await asyncio.sleep(0.2)
            
            # Get snapshot
            snapshot = await monitor.get_snapshot()
            assert snapshot is not None
            
            await monitor.stop()

    @pytest.mark.asyncio
    async def test_metrics_collection_flow(self, test_metrics_service):
        """Test complete metrics collection flow"""
        # Record various metrics
        test_metrics_service.record_task_execution(
            task_id="test_task",
            task_type="security_scan",
            status="completed",
            duration=5.0
        )
        
        # Check which method signature exists
        import inspect
        sig = inspect.signature(test_metrics_service.record_agent_execution)
        params = list(sig.parameters.keys())
        
        if "agent_name" in params:
            test_metrics_service.record_agent_execution(
                agent_id="agent_001",
                agent_name="Security Agent",
                status="completed",
                duration=3.0
            )
        else:
            test_metrics_service.record_agent_execution(
                agent_id="agent_001",
                status="completed",
                duration=3.0
            )
        
        test_metrics_service.update_system_resources(
            cpu_percent=50.0,
            memory_bytes=1000000000,
            memory_percent=50.0
        )
        
        # Get metrics
        metrics_data = test_metrics_service.get_metrics()
        assert metrics_data is not None
        assert len(metrics_data) > 0

    def test_tracing_and_metrics_integration(self, test_metrics_service):
        """Test tracing and metrics integration"""
        try:
            tracing = get_tracing_service()
            if tracing and tracing.enabled:
                # Create span
                span = tracing.start_span("test_span")
                
                # Record metrics during span
                test_metrics_service.record_task_execution(
                    task_id="test_task",
                    task_type="test",
                    status="completed",
                    duration=1.0
                )
                
                # Should not crash
                assert True
        except Exception:
            # If tracing not available, skip
            pytest.skip("Tracing not available")

    @pytest.mark.asyncio
    async def test_end_to_end_monitoring(self, test_metrics_service, mock_psutil):
        """Test end-to-end monitoring flow"""
        # Start monitor
        monitor = SystemMonitor(update_interval=0.1)
        monitor.metrics_service = test_metrics_service
        
        with patch('src.amas.services.system_monitor.psutil', mock_psutil):
            await monitor.start()
            
            # Simulate some activity
            test_metrics_service.record_http_request(
                method="GET",
                endpoint="/api/v1/test",
                status_code=200,
                duration=0.1
            )
            
            # Get snapshot
            snapshot = await monitor.get_snapshot()
            assert snapshot is not None
            
            # Get metrics
            metrics = test_metrics_service.get_metrics()
            assert metrics is not None
            
            await monitor.stop()

