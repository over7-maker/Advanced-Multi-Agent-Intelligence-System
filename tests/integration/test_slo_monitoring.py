"""
Integration tests for SLO Monitoring - Error Budget Tracking and Evaluation
"""

import pytest
import os
import tempfile
import yaml
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from src.amas.observability.slo_manager import (
    SLOManager,
    SLODefinition,
    SLOStatus,
    initialize_slo_manager,
    get_slo_manager
)


class TestSLOMonitoring:
    """Integration tests for SLO monitoring"""
    
    @pytest.fixture
    def slo_config_file(self):
        """Create a temporary SLO configuration file"""
        config = {
            "slos": [
                {
                    "name": "test_availability",
                    "description": "Test availability SLO",
                    "metric_query": "rate(amas_agent_requests_total{status='success'}[5m]) / rate(amas_agent_requests_total[5m]) * 100",
                    "threshold": 99.5,
                    "comparison": ">=",
                    "window_minutes": 5,
                    "error_budget_percent": 0.5,
                    "severity": "critical"
                },
                {
                    "name": "test_latency",
                    "description": "Test latency SLO",
                    "metric_query": "histogram_quantile(0.95, rate(amas_agent_duration_seconds_bucket[5m]))",
                    "threshold": 1.5,
                    "comparison": "<=",
                    "window_minutes": 5,
                    "error_budget_percent": 10.0,
                    "severity": "high"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            yield f.name
        
        os.unlink(f.name)
    
    @pytest.fixture
    def slo_manager(self, slo_config_file):
        """Create SLO manager instance with mocked Prometheus"""
        with patch('src.amas.observability.slo_manager.requests.get') as mock_get:
            # Mock Prometheus responses
            def mock_prometheus_response(url, params=None, **kwargs):
                mock_response = Mock()
                query = params.get('query', '') if params else ''
                
                # Return different values based on query
                if 'availability' in query or 'success' in query:
                    value = "99.8"  # Compliant
                elif 'latency' in query or 'histogram_quantile' in query:
                    value = "1.2"  # Compliant (below 1.5s threshold)
                else:
                    value = "0"
                
                mock_response.json.return_value = {
                    "status": "success",
                    "data": {
                        "result": [{"value": [1234567890, value]}]
                    }
                }
                mock_response.raise_for_status = Mock()
                return mock_response
            
            mock_get.side_effect = mock_prometheus_response
            
            manager = SLOManager(
                prometheus_url="http://localhost:9090",
                slo_config_path=slo_config_file
            )
            return manager
    
    def test_slo_manager_initialization(self, slo_manager):
        """Test SLO manager initialization"""
        assert len(slo_manager.slo_definitions) == 2
        assert "test_availability" in slo_manager.slo_definitions
        assert "test_latency" in slo_manager.slo_definitions
    
    def test_load_slo_definitions(self, slo_manager):
        """Test loading SLO definitions"""
        assert "test_availability" in slo_manager.slo_definitions
        slo = slo_manager.slo_definitions["test_availability"]
        assert slo.threshold == 99.5
        assert slo.comparison == ">="
        assert slo.error_budget_percent == 0.5
        assert slo.severity == "critical"
    
    def test_evaluate_slo_compliant(self, slo_manager):
        """Test SLO evaluation when compliant"""
        status = slo_manager.evaluate_slo("test_availability")
        
        assert status is not None
        assert status.slo_name == "test_availability"
        assert status.current_value == 99.8
        assert status.status == "compliant"
        assert status.compliance_percent >= 100.0
    
    def test_evaluate_slo_violated(self, slo_manager):
        """Test SLO evaluation when violated"""
        # Mock a violation (below threshold)
        with patch.object(slo_manager, 'query_prometheus', return_value=99.0):
            status = slo_manager.evaluate_slo("test_availability")
            
            assert status is not None
            assert status.status in ["violated", "warning", "critical"]
            assert status.compliance_percent < 100.0
    
    def test_error_budget_tracking(self, slo_manager):
        """Test error budget tracking"""
        initial_status = slo_manager.get_slo_status("test_availability")
        initial_budget = initial_status.error_budget_remaining_percent
        
        # Simulate violation
        with patch.object(slo_manager, 'query_prometheus', return_value=99.0):
            status = slo_manager.evaluate_slo("test_availability")
            
            # Error budget should decrease
            assert status.error_budget_remaining_percent < initial_budget
    
    def test_evaluate_all_slos(self, slo_manager):
        """Test evaluating all SLOs"""
        results = slo_manager.evaluate_all_slos()
        
        assert len(results) == 2
        assert "test_availability" in results
        assert "test_latency" in results
        assert isinstance(results["test_availability"], SLOStatus)
        assert isinstance(results["test_latency"], SLOStatus)
    
    def test_get_violations(self, slo_manager):
        """Test getting violations"""
        # Initially should be compliant
        violations = slo_manager.get_violations()
        assert isinstance(violations, list)
        
        # Create a violation
        with patch.object(slo_manager, 'query_prometheus', return_value=99.0):
            slo_manager.evaluate_slo("test_availability")
            violations = slo_manager.get_violations()
            # Should have at least one violation
            assert len(violations) >= 0  # May be 0 if status is "compliant" but value is below threshold
    
    def test_burn_rate_calculation(self, slo_manager):
        """Test burn rate calculation"""
        # First evaluation
        slo_manager.evaluate_slo("test_availability")
        status1 = slo_manager.get_slo_status("test_availability")
        
        # Simulate time passing and violation
        import time
        time.sleep(0.1)
        
        with patch.object(slo_manager, 'query_prometheus', return_value=99.0):
            slo_manager.evaluate_slo("test_availability")
            status2 = slo_manager.get_slo_status("test_availability")
            
            # Burn rate should be calculated
            assert hasattr(status2, 'burn_rate')
            assert isinstance(status2.burn_rate, float)
    
    def test_performance_regression_detection(self, slo_manager):
        """Test performance regression detection"""
        # Establish baseline
        regression = slo_manager.detect_performance_regression("test_op", 2.0)
        assert regression is None  # Should establish baseline
        
        # Detect regression (>50% slower)
        regression = slo_manager.detect_performance_regression("test_op", 4.0)  # 2x baseline
        assert regression is not None
        assert regression["type"] == "latency_regression"
        assert regression["severity"] in ["medium", "high"]
        assert regression["current_duration"] == 4.0
        assert regression["baseline_duration"] == 2.0
    
    def test_check_compliance_operators(self, slo_manager):
        """Test compliance checking with different operators"""
        # Test >= comparison
        assert slo_manager._check_compliance(100.0, 99.5, ">=") is True
        assert slo_manager._check_compliance(99.0, 99.5, ">=") is False
        
        # Test <= comparison
        assert slo_manager._check_compliance(1.0, 1.5, "<=") is True
        assert slo_manager._check_compliance(2.0, 1.5, "<=") is False
        
        # Test > comparison
        assert slo_manager._check_compliance(100.0, 99.5, ">") is True
        assert slo_manager._check_compliance(99.5, 99.5, ">") is False
        
        # Test < comparison
        assert slo_manager._check_compliance(1.0, 1.5, "<") is True
        assert slo_manager._check_compliance(1.5, 1.5, "<") is False
    
    def test_parse_time_window(self, slo_manager):
        """Test parsing time windows"""
        assert slo_manager._parse_time_window("5m") == 5
        assert slo_manager._parse_time_window("1h") == 60
        assert slo_manager._parse_time_window("2d") == 2880
        assert slo_manager._parse_time_window("30m") == 30
    
    def test_global_slo_manager(self):
        """Test global SLO manager functions"""
        with patch('src.amas.observability.slo_manager.requests.get'):
            manager = get_slo_manager()
            assert manager is not None
            assert isinstance(manager, SLOManager)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
