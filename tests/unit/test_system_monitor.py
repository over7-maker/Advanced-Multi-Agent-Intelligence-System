"""
Unit tests for System Monitor Service
Tests PART 6: Monitoring & Observability - System Resource Monitoring
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

from src.amas.services.system_monitor import SystemMonitor, get_system_monitor


@pytest.mark.unit
class TestSystemMonitor:
    """Test SystemMonitor"""

    @pytest.fixture
    def system_monitor(self):
        """Create SystemMonitor instance"""
        return SystemMonitor(update_interval=1)

    @pytest.mark.asyncio
    async def test_start_stop(self, system_monitor, mock_psutil):
        """Test starting and stopping monitor"""
        with patch('src.amas.services.system_monitor.psutil', mock_psutil):
            await system_monitor.start()
            assert system_monitor.running is True
            
            await system_monitor.stop()
            assert system_monitor.running is False

    @pytest.mark.asyncio
    async def test_start_when_already_running(self, system_monitor, mock_psutil):
        """Test starting monitor when already running"""
        with patch('src.amas.services.system_monitor.psutil', mock_psutil):
            await system_monitor.start()
            await system_monitor.start()  # Should not crash
            assert system_monitor.running is True
            
            await system_monitor.stop()

    @pytest.mark.asyncio
    async def test_start_without_psutil(self, system_monitor):
        """Test starting monitor without psutil"""
        with patch('src.amas.services.system_monitor.PSUTIL_AVAILABLE', False):
            await system_monitor.start()
            # Should not crash, but may not actually start
            await system_monitor.stop()

    @pytest.mark.asyncio
    async def test_collect_metrics(self, system_monitor, mock_psutil, mock_metrics_service):
        """Test collecting system metrics"""
        system_monitor.metrics_service = mock_metrics_service
        
        with patch('src.amas.services.system_monitor.psutil', mock_psutil):
            await system_monitor._collect_metrics()
            
            # Verify metrics service was called
            mock_metrics_service.update_system_resources.assert_called()

    @pytest.mark.asyncio
    async def test_get_snapshot(self, system_monitor, mock_psutil):
        """Test getting system snapshot"""
        with patch('src.amas.services.system_monitor.psutil', mock_psutil):
            snapshot = await system_monitor.get_snapshot()
            
            assert snapshot is not None
            assert "cpu" in snapshot
            assert "memory" in snapshot
            assert "disk" in snapshot
            assert "network" in snapshot

    @pytest.mark.asyncio
    async def test_get_snapshot_without_psutil(self, system_monitor):
        """Test getting snapshot without psutil"""
        with patch('src.amas.services.system_monitor.PSUTIL_AVAILABLE', False):
            snapshot = await system_monitor.get_snapshot()
            
            assert snapshot is not None
            assert "error" in snapshot

    @pytest.mark.asyncio
    async def test_monitor_loop(self, system_monitor, mock_psutil):
        """Test monitor loop execution"""
        system_monitor.update_interval = 0.1  # Short interval for testing
        
        with patch('src.amas.services.system_monitor.psutil', mock_psutil):
            await system_monitor.start()
            
            # Let it run for a short time
            await asyncio.sleep(0.2)
            
            await system_monitor.stop()
            
            # Verify it ran
            assert system_monitor.running is False

    @pytest.mark.asyncio
    async def test_monitor_loop_error_handling(self, system_monitor, mock_psutil):
        """Test monitor loop error handling"""
        # Make psutil raise an error
        mock_psutil.cpu_percent.side_effect = Exception("Test error")
        
        system_monitor.update_interval = 0.1
        
        with patch('src.amas.services.system_monitor.psutil', mock_psutil):
            await system_monitor.start()
            
            # Let it run and encounter error
            await asyncio.sleep(0.2)
            
            await system_monitor.stop()
            
            # Should have handled error gracefully
            assert system_monitor.running is False

    def test_get_system_monitor_singleton(self):
        """Test get_system_monitor returns singleton"""
        monitor1 = get_system_monitor()
        monitor2 = get_system_monitor()
        
        # Should return same instance
        assert monitor1 is monitor2

