"""
Unit tests for Performance Monitor - Regression Detection
"""

import pytest
from unittest.mock import Mock
from datetime import datetime, timezone

from src.amas.observability.tracing.tracer import PerformanceMonitor


class TestPerformanceMonitor:
    """Test cases for PerformanceMonitor"""
    
    @pytest.fixture
    def monitor(self):
        """Create a performance monitor instance"""
        tracer_mock = Mock()
        monitor = PerformanceMonitor(tracer_mock)
        return monitor
    
    @pytest.mark.asyncio
    async def test_check_performance_regression_latency(self, monitor):
        """Test latency regression detection"""
        regression = await monitor.check_performance_regression(
            operation="test_operation",
            duration_seconds=3.0,  # 2x baseline of 1.5
            success=True
        )
        
        assert regression is not None
        assert regression["type"] == "latency_regression"
        assert regression["severity"] in ["medium", "high"]
        assert regression["operation"] == "test_operation"
        assert regression["current_duration"] == 3.0
    
    @pytest.mark.asyncio
    async def test_check_performance_regression_success_rate(self, monitor):
        """Test success rate regression detection"""
        regression = await monitor.check_performance_regression(
            operation="test_operation",
            duration_seconds=1.0,
            success=False
        )
        
        assert regression is not None
        assert regression["type"] == "success_rate_regression"
        assert regression["severity"] == "high"
        assert regression["operation"] == "test_operation"
    
    @pytest.mark.asyncio
    async def test_check_performance_regression_no_regression(self, monitor):
        """Test that no regression is detected for normal performance"""
        regression = await monitor.check_performance_regression(
            operation="test_operation",
            duration_seconds=1.0,  # Within baseline
            success=True
        )
        
        # Should not detect regression for normal performance
        assert regression is None or regression.get("type") != "latency_regression"
    
    def test_get_recent_violations(self, monitor):
        """Test getting recent violations"""
        violations = monitor.get_recent_violations(hours=24)
        assert isinstance(violations, list)
    
    def test_get_recent_violations_empty(self, monitor):
        """Test getting recent violations when none exist"""
        violations = monitor.get_recent_violations(hours=1)
        assert isinstance(violations, list)
        # Initially should be empty
        assert len(violations) == 0
    
    def test_update_baseline(self, monitor):
        """Test updating performance baseline"""
        monitor.update_baseline("test_operation", 2.0)
        assert "test_operation_p95_seconds" in monitor._performance_baselines
        assert monitor._performance_baselines["test_operation_p95_seconds"] == 2.0
    
    def test_update_baseline_unchanged(self, monitor):
        """Test that baseline doesn't update for small changes"""
        monitor.update_baseline("test_operation", 1.5)
        original = monitor._performance_baselines["test_operation_p95_seconds"]
        
        # Small change (<20%) should not update
        monitor.update_baseline("test_operation", 1.6)
        assert monitor._performance_baselines["test_operation_p95_seconds"] == original
    
    def test_performance_baselines_initialization(self, monitor):
        """Test that performance baselines are initialized"""
        assert "agent_execution_p95_seconds" in monitor._performance_baselines
        assert "tool_call_p95_seconds" in monitor._performance_baselines
        assert monitor._performance_baselines["agent_execution_p95_seconds"] == 1.5
        assert monitor._performance_baselines["tool_call_p95_seconds"] == 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
