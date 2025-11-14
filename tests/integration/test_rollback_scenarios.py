"""
Integration tests for rollback scenarios in Progressive Delivery Pipeline.

Tests automatic rollback triggers, rollback decision engine, and recovery scenarios.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.deployment.health_checker import (
    DeploymentHealthChecker,
    HealthStatus,
    RollbackDecision,
    SLOThresholds,
)


@pytest.fixture
def health_checker():
    """Create a health checker instance for testing."""
    return DeploymentHealthChecker(
        service_url="http://localhost:8000",
        prometheus_url="http://localhost:9090",
        timeout=5,
    )


class TestRollbackScenarios:
    """Test suite for rollback scenarios."""
    
    @pytest.mark.asyncio
    async def test_rollback_on_success_rate_violation(self, health_checker):
        """Test rollback triggered by success rate dropping below threshold."""
        with patch.object(health_checker, 'check_success_rate', new_callable=AsyncMock) as mock_check:
            mock_check.return_value = MagicMock(
                status=HealthStatus.UNHEALTHY,
                metrics={"success_rate": 0.90}  # Below 95% threshold
            )
            
            with patch.object(health_checker, 'check_http_endpoint', new_callable=AsyncMock) as mock_http:
                mock_http.return_value = MagicMock(status=HealthStatus.HEALTHY)
            
            with patch.object(health_checker, 'check_latency_p95', new_callable=AsyncMock) as mock_latency:
                mock_latency.return_value = MagicMock(status=HealthStatus.HEALTHY)
            
            with patch.object(health_checker, 'check_error_budget', new_callable=AsyncMock) as mock_budget:
                mock_budget.return_value = MagicMock(status=HealthStatus.HEALTHY)
            
            result = await health_checker.check_comprehensive_health(
                "test-service",
                "test-namespace"
            )
            
            # Should recommend rollback due to SLO violation
            assert result.rollback_decision in [
                RollbackDecision.ROLLBACK_RECOMMENDED,
                RollbackDecision.ROLLBACK_REQUIRED
            ]
    
    @pytest.mark.asyncio
    async def test_rollback_on_latency_violation(self, health_checker):
        """Test rollback triggered by P95 latency exceeding threshold."""
        with patch.object(health_checker, 'check_latency_p95', new_callable=AsyncMock) as mock_check:
            mock_check.return_value = MagicMock(
                status=HealthStatus.UNHEALTHY,
                metrics={"latency_p95_ms": 4000.0}  # Above 3s threshold
            )
            
            with patch.object(health_checker, 'check_http_endpoint', new_callable=AsyncMock) as mock_http:
                mock_http.return_value = MagicMock(status=HealthStatus.HEALTHY)
            
            with patch.object(health_checker, 'check_success_rate', new_callable=AsyncMock) as mock_success:
                mock_success.return_value = MagicMock(status=HealthStatus.HEALTHY)
            
            with patch.object(health_checker, 'check_error_budget', new_callable=AsyncMock) as mock_budget:
                mock_budget.return_value = MagicMock(status=HealthStatus.HEALTHY)
            
            result = await health_checker.check_comprehensive_health(
                "test-service",
                "test-namespace"
            )
            
            assert result.rollback_decision in [
                RollbackDecision.ROLLBACK_RECOMMENDED,
                RollbackDecision.ROLLBACK_REQUIRED
            ]
    
    @pytest.mark.asyncio
    async def test_rollback_on_error_budget_depletion(self, health_checker):
        """Test rollback triggered by error budget depletion."""
        with patch.object(health_checker, 'check_error_budget', new_callable=AsyncMock) as mock_check:
            mock_check.return_value = MagicMock(
                status=HealthStatus.UNHEALTHY,
                metrics={"error_budget": 0.02}  # Below 5% threshold
            )
            
            with patch.object(health_checker, 'check_http_endpoint', new_callable=AsyncMock) as mock_http:
                mock_http.return_value = MagicMock(status=HealthStatus.HEALTHY)
            
            with patch.object(health_checker, 'check_success_rate', new_callable=AsyncMock) as mock_success:
                mock_success.return_value = MagicMock(status=HealthStatus.HEALTHY)
            
            with patch.object(health_checker, 'check_latency_p95', new_callable=AsyncMock) as mock_latency:
                mock_latency.return_value = MagicMock(status=HealthStatus.HEALTHY)
            
            result = await health_checker.check_comprehensive_health(
                "test-service",
                "test-namespace"
            )
            
            # Error budget depletion should trigger rollback
            assert result.rollback_decision == RollbackDecision.ROLLBACK_REQUIRED
    
    @pytest.mark.asyncio
    async def test_rollback_on_multiple_failures(self, health_checker):
        """Test rollback triggered by multiple health check failures."""
        with patch.object(health_checker, 'check_http_endpoint', new_callable=AsyncMock) as mock_http:
            mock_http.return_value = MagicMock(status=HealthStatus.UNHEALTHY)
        
        with patch.object(health_checker, 'check_success_rate', new_callable=AsyncMock) as mock_success:
            mock_success.return_value = MagicMock(
                status=HealthStatus.UNHEALTHY,
                metrics={"success_rate": 0.90}
            )
        
        with patch.object(health_checker, 'check_latency_p95', new_callable=AsyncMock) as mock_latency:
            mock_latency.return_value = MagicMock(
                status=HealthStatus.UNHEALTHY,
                metrics={"latency_p95_ms": 4000.0}
            )
        
        with patch.object(health_checker, 'check_error_budget', new_callable=AsyncMock) as mock_budget:
            mock_budget.return_value = MagicMock(status=HealthStatus.HEALTHY)
        
        result = await health_checker.check_comprehensive_health(
            "test-service",
            "test-namespace"
        )
        
        # Multiple failures should require rollback
        assert result.overall_status == HealthStatus.UNHEALTHY
        assert result.rollback_decision == RollbackDecision.ROLLBACK_REQUIRED
    
    @pytest.mark.asyncio
    async def test_no_rollback_on_single_minor_issue(self, health_checker):
        """Test that single minor issue doesn't trigger rollback."""
        with patch.object(health_checker, 'check_http_endpoint', new_callable=AsyncMock) as mock_http:
            mock_http.return_value = MagicMock(status=HealthStatus.HEALTHY)
        
        with patch.object(health_checker, 'check_success_rate', new_callable=AsyncMock) as mock_success:
            mock_success.return_value = MagicMock(
                status=HealthStatus.HEALTHY,
                metrics={"success_rate": 0.96}
            )
        
        with patch.object(health_checker, 'check_latency_p95', new_callable=AsyncMock) as mock_latency:
            mock_latency.return_value = MagicMock(
                status=HealthStatus.DEGRADED,  # Minor degradation
                metrics={"latency_p95_ms": 2500.0}
            )
        
        with patch.object(health_checker, 'check_error_budget', new_callable=AsyncMock) as mock_budget:
            mock_budget.return_value = MagicMock(
                status=HealthStatus.HEALTHY,
                metrics={"error_budget": 0.10}
            )
        
        result = await health_checker.check_comprehensive_health(
            "test-service",
            "test-namespace"
        )
        
        # Single minor issue shouldn't require rollback
        assert result.rollback_decision in [
            RollbackDecision.NO_ROLLBACK,
            RollbackDecision.ROLLBACK_RECOMMENDED
        ]
    
    @pytest.mark.asyncio
    async def test_rollback_timeout_scenario(self, health_checker):
        """Test rollback decision when health checks timeout."""
        with patch.object(health_checker, 'check_http_endpoint', new_callable=AsyncMock) as mock_http:
            mock_http.side_effect = asyncio.TimeoutError()
        
        with patch.object(health_checker, 'check_success_rate', new_callable=AsyncMock) as mock_success:
            mock_success.return_value = MagicMock(status=HealthStatus.UNKNOWN)
        
        result = await health_checker.check_comprehensive_health(
            "test-service",
            "test-namespace",
            check_metrics=False  # Only check endpoints
        )
        
        # Timeouts should result in unknown/degrated status
        assert result.overall_status in [
            HealthStatus.UNKNOWN,
            HealthStatus.DEGRADED,
            HealthStatus.UNHEALTHY
        ]


class TestRollbackDecisionEngine:
    """Test suite for rollback decision engine logic."""
    
    @pytest.mark.asyncio
    async def test_decision_with_custom_thresholds(self):
        """Test rollback decision with custom SLO thresholds."""
        custom_thresholds = SLOThresholds(
            success_rate_min=0.99,  # Stricter threshold
            latency_p95_max_ms=2000.0,  # Stricter threshold
            error_budget_min=0.10,  # Stricter threshold
        )
        
        health_checker = DeploymentHealthChecker(
            service_url="http://localhost:8000",
            slo_thresholds=custom_thresholds,
        )
        
        with patch.object(health_checker, 'check_success_rate', new_callable=AsyncMock) as mock_success:
            mock_success.return_value = MagicMock(
                status=HealthStatus.UNHEALTHY,
                metrics={"success_rate": 0.98}  # Would pass default threshold but fails custom
            )
        
        with patch.object(health_checker, 'check_http_endpoint', new_callable=AsyncMock) as mock_http:
            mock_http.return_value = MagicMock(status=HealthStatus.HEALTHY)
        
        with patch.object(health_checker, 'check_latency_p95', new_callable=AsyncMock) as mock_latency:
            mock_latency.return_value = MagicMock(status=HealthStatus.HEALTHY)
        
        with patch.object(health_checker, 'check_error_budget', new_callable=AsyncMock) as mock_budget:
            mock_budget.return_value = MagicMock(status=HealthStatus.HEALTHY)
        
        result = await health_checker.check_comprehensive_health(
            "test-service",
            "test-namespace"
        )
        
        # Should trigger rollback with stricter thresholds
        assert result.rollback_decision in [
            RollbackDecision.ROLLBACK_RECOMMENDED,
            RollbackDecision.ROLLBACK_REQUIRED
        ]
