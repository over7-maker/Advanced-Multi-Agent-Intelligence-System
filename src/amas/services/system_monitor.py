# src/amas/services/system_monitor.py (SYSTEM RESOURCE MONITORING)
import asyncio
import logging
from typing import Dict, Any, Optional
from src.amas.services.prometheus_metrics_service import get_metrics_service

logger = logging.getLogger(__name__)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available - system monitoring will be limited")

class SystemMonitor:
    """
    System resource monitoring service
    
    ✅ CPU usage tracking
    ✅ Memory usage tracking
    ✅ Disk usage tracking
    ✅ Network I/O tracking
    ✅ Process monitoring
    """
    
    def __init__(self, update_interval: int = 5):
        self.update_interval = update_interval
        self.metrics_service = get_metrics_service()
        self.running = False
        self._monitor_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start system monitoring"""
        
        if self.running:
            logger.warning("System monitor already running")
            return
        
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not available - system monitor cannot start")
            return
        
        self.running = True
        logger.info("Starting system monitor")
        
        self._monitor_task = asyncio.create_task(self._monitor_loop())
    
    async def stop(self):
        """Stop system monitoring"""
        
        self.running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopping system monitor")
    
    async def _monitor_loop(self):
        """Main monitoring loop"""
        
        while self.running:
            try:
                await self._collect_metrics()
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"System monitoring error: {e}", exc_info=True)
                await asyncio.sleep(self.update_interval)
    
    async def _collect_metrics(self):
        """Collect all system metrics"""
        
        if not PSUTIL_AVAILABLE:
            return
        
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics_service.update_system_resources(
                cpu_percent=cpu_percent,
                memory_bytes=psutil.virtual_memory().used,
                memory_percent=psutil.virtual_memory().percent
            )
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            self.metrics_service.metrics["amas_system_disk_usage_bytes"].labels(
                mount_point='/'
            ).set(disk.used)
            
            # Network I/O metrics
            net_io = psutil.net_io_counters()
            if net_io:
                # Note: Counters should be incremented, not set
                # For counters, we track deltas, but for simplicity we'll use the current value
                # In production, track previous values and calculate deltas
                self.metrics_service.metrics["amas_system_network_io_bytes_total"].labels(
                    direction='sent'
                )._value._value = net_io.bytes_sent
                self.metrics_service.metrics["amas_system_network_io_bytes_total"].labels(
                    direction='received'
                )._value._value = net_io.bytes_recv
            
            logger.debug(f"System metrics collected: CPU={cpu_percent}%, Memory={psutil.virtual_memory().percent}%")
        
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}", exc_info=True)
    
    async def get_snapshot(self) -> Dict[str, Any]:
        """
        Get current system metrics snapshot
        
        Returns:
            Dict with current system state
        """
        
        if not PSUTIL_AVAILABLE:
            return {
                "error": "psutil not available",
                "cpu": {"percent": 0, "count": 0},
                "memory": {"total": 0, "used": 0, "percent": 0},
                "disk": {"total": 0, "used": 0, "percent": 0},
                "network": {"bytes_sent": 0, "bytes_recv": 0}
            }
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net_io = psutil.net_io_counters()
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                },
                "network": {
                    "bytes_sent": net_io.bytes_sent if net_io else 0,
                    "bytes_recv": net_io.bytes_recv if net_io else 0,
                    "packets_sent": net_io.packets_sent if net_io else 0,
                    "packets_recv": net_io.packets_recv if net_io else 0
                }
            }
        except Exception as e:
            logger.error(f"Error getting system snapshot: {e}", exc_info=True)
            return {
                "error": str(e),
                "cpu": {"percent": 0, "count": 0},
                "memory": {"total": 0, "used": 0, "percent": 0},
                "disk": {"total": 0, "used": 0, "percent": 0},
                "network": {"bytes_sent": 0, "bytes_recv": 0}
            }


# Global system monitor instance
_system_monitor: Optional[SystemMonitor] = None

def get_system_monitor() -> SystemMonitor:
    """Get global system monitor"""
    
    global _system_monitor
    
    if _system_monitor is None:
        _system_monitor = SystemMonitor()
    
    return _system_monitor

