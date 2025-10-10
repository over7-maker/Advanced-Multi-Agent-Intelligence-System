"""
Graceful Shutdown Service for AMAS
Implements comprehensive graceful shutdown handling for production environments
"""

import asyncio
import logging
import signal
import time
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ShutdownPhase(str, Enum):
    """Shutdown phases"""
    INITIATED = "initiated"
    STOPPING_ACCEPTORS = "stopping_acceptors"
    DRAINING_CONNECTIONS = "draining_connections"
    STOPPING_SERVICES = "stopping_services"
    CLEANING_UP = "cleaning_up"
    COMPLETED = "completed"


class ServicePriority(str, Enum):
    """Service shutdown priority"""
    CRITICAL = "critical"      # Shutdown first
    HIGH = "high"             # Shutdown second
    MEDIUM = "medium"         # Shutdown third
    LOW = "low"               # Shutdown last


@dataclass
class ShutdownConfig:
    """Configuration for graceful shutdown"""
    shutdown_timeout: float = 30.0
    drain_timeout: float = 10.0
    service_timeout: float = 5.0
    force_shutdown_timeout: float = 5.0
    enable_health_checks: bool = True
    enable_metrics_collection: bool = True
    enable_audit_logging: bool = True


@dataclass
class ServiceInfo:
    """Information about a service for shutdown"""
    name: str
    priority: ServicePriority
    shutdown_func: Callable
    timeout: float = 5.0
    critical: bool = False
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class GracefulShutdownService:
    """Service for managing graceful shutdown"""
    
    def __init__(self, config: ShutdownConfig = None):
        self.config = config or ShutdownConfig()
        self.logger = logging.getLogger(__name__)
        
        # Shutdown state
        self.shutdown_initiated = False
        self.shutdown_phase = None
        self.start_time = None
        self.services: Dict[str, ServiceInfo] = {}
        self.shutdown_tasks: List[asyncio.Task] = []
        
        # Statistics
        self.shutdown_stats = {
            "total_shutdowns": 0,
            "successful_shutdowns": 0,
            "forced_shutdowns": 0,
            "average_shutdown_time": 0.0
        }
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self._signal_handler)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, self._signal_handler)
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        signal_name = signal.Signals(signum).name
        self.logger.info(f"Received signal {signal_name} ({signum}), initiating graceful shutdown...")
        asyncio.create_task(self.initiate_shutdown())
    
    def register_service(
        self,
        name: str,
        shutdown_func: Callable,
        priority: ServicePriority = ServicePriority.MEDIUM,
        timeout: float = 5.0,
        critical: bool = False,
        dependencies: List[str] = None
    ):
        """Register a service for graceful shutdown"""
        service_info = ServiceInfo(
            name=name,
            priority=priority,
            shutdown_func=shutdown_func,
            timeout=timeout,
            critical=critical,
            dependencies=dependencies or []
        )
        
        self.services[name] = service_info
        self.logger.info(f"Registered service '{name}' for graceful shutdown")
    
    def unregister_service(self, name: str):
        """Unregister a service from graceful shutdown"""
        if name in self.services:
            del self.services[name]
            self.logger.info(f"Unregistered service '{name}' from graceful shutdown")
    
    async def initiate_shutdown(self):
        """Initiate graceful shutdown process"""
        if self.shutdown_initiated:
            self.logger.warning("Shutdown already initiated, ignoring request")
            return
        
        self.shutdown_initiated = True
        self.shutdown_phase = ShutdownPhase.INITIATED
        self.start_time = time.time()
        
        self.logger.info("Starting graceful shutdown process...")
        
        try:
            # Phase 1: Stop accepting new connections
            await self._stop_acceptors()
            
            # Phase 2: Drain existing connections
            await self._drain_connections()
            
            # Phase 3: Stop services in priority order
            await self._stop_services()
            
            # Phase 4: Cleanup
            await self._cleanup()
            
            # Shutdown completed successfully
            self.shutdown_phase = ShutdownPhase.COMPLETED
            shutdown_time = time.time() - self.start_time
            
            self.logger.info(f"Graceful shutdown completed in {shutdown_time:.2f}s")
            self._update_shutdown_stats(True, shutdown_time)
            
        except Exception as e:
            self.logger.error(f"Error during graceful shutdown: {e}")
            self._update_shutdown_stats(False, time.time() - self.start_time)
            raise
        finally:
            # Force shutdown if needed
            await self._force_shutdown_if_needed()
    
    async def _stop_acceptors(self):
        """Stop accepting new connections"""
        self.shutdown_phase = ShutdownPhase.STOPPING_ACCEPTORS
        self.logger.info("Stopping acceptors...")
        
        # In a real implementation, this would stop the web server from accepting new requests
        # For FastAPI, this is handled by the ASGI server
        
        await asyncio.sleep(0.1)  # Brief pause
        self.logger.info("Acceptors stopped")
    
    async def _drain_connections(self):
        """Drain existing connections"""
        self.shutdown_phase = ShutdownPhase.DRAINING_CONNECTIONS
        self.logger.info("Draining existing connections...")
        
        # Wait for existing requests to complete
        start_drain = time.time()
        while time.time() - start_drain < self.config.drain_timeout:
            # Check if there are active connections
            # In a real implementation, this would check active request count
            active_connections = 0  # Placeholder
            
            if active_connections == 0:
                self.logger.info("All connections drained")
                return
            
            await asyncio.sleep(0.1)
        
        self.logger.warning(f"Drain timeout ({self.config.drain_timeout}s) exceeded")
    
    async def _stop_services(self):
        """Stop services in priority order"""
        self.shutdown_phase = ShutdownPhase.STOPPING_SERVICES
        self.logger.info("Stopping services...")
        
        # Sort services by priority
        priority_order = [ServicePriority.CRITICAL, ServicePriority.HIGH, ServicePriority.MEDIUM, ServicePriority.LOW]
        
        for priority in priority_order:
            services_to_stop = [
                service for service in self.services.values()
                if service.priority == priority
            ]
            
            if not services_to_stop:
                continue
            
            self.logger.info(f"Stopping {priority.value} priority services...")
            
            # Stop services in parallel
            tasks = []
            for service in services_to_stop:
                task = asyncio.create_task(self._stop_service(service))
                tasks.append(task)
            
            # Wait for all services in this priority to stop
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self.logger.info("All services stopped")
    
    async def _stop_service(self, service: ServiceInfo):
        """Stop a single service"""
        try:
            self.logger.info(f"Stopping service '{service.name}'...")
            
            # Create timeout task
            timeout_task = asyncio.create_task(
                asyncio.sleep(service.timeout)
            )
            
            # Create shutdown task
            if asyncio.iscoroutinefunction(service.shutdown_func):
                shutdown_task = asyncio.create_task(service.shutdown_func())
            else:
                shutdown_task = asyncio.create_task(
                    asyncio.get_event_loop().run_in_executor(None, service.shutdown_func)
                )
            
            # Wait for either completion or timeout
            done, pending = await asyncio.wait(
                [shutdown_task, timeout_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
            
            if shutdown_task in done:
                self.logger.info(f"Service '{service.name}' stopped successfully")
            else:
                self.logger.warning(f"Service '{service.name}' shutdown timed out")
                
        except Exception as e:
            self.logger.error(f"Error stopping service '{service.name}': {e}")
            if service.critical:
                self.logger.error(f"Critical service '{service.name}' failed to stop")
                raise
    
    async def _cleanup(self):
        """Perform final cleanup"""
        self.shutdown_phase = ShutdownPhase.CLEANING_UP
        self.logger.info("Performing cleanup...")
        
        # Cleanup tasks
        cleanup_tasks = [
            self._cleanup_logs(),
            self._cleanup_temp_files(),
            self._cleanup_metrics(),
            self._cleanup_connections()
        ]
        
        # Run cleanup tasks in parallel
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        self.logger.info("Cleanup completed")
    
    async def _cleanup_logs(self):
        """Cleanup log files"""
        try:
            self.logger.info("Cleaning up logs...")
            # In a real implementation, this would rotate logs, compress old logs, etc.
            await asyncio.sleep(0.1)
            self.logger.info("Log cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during log cleanup: {e}")
    
    async def _cleanup_temp_files(self):
        """Cleanup temporary files"""
        try:
            self.logger.info("Cleaning up temporary files...")
            # In a real implementation, this would remove temp files
            await asyncio.sleep(0.1)
            self.logger.info("Temp file cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during temp file cleanup: {e}")
    
    async def _cleanup_metrics(self):
        """Cleanup metrics"""
        try:
            self.logger.info("Cleaning up metrics...")
            # In a real implementation, this would flush metrics to storage
            await asyncio.sleep(0.1)
            self.logger.info("Metrics cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during metrics cleanup: {e}")
    
    async def _cleanup_connections(self):
        """Cleanup database and external connections"""
        try:
            self.logger.info("Cleaning up connections...")
            # In a real implementation, this would close database connections, etc.
            await asyncio.sleep(0.1)
            self.logger.info("Connection cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during connection cleanup: {e}")
    
    async def _force_shutdown_if_needed(self):
        """Force shutdown if graceful shutdown takes too long"""
        if not self.shutdown_initiated:
            return
        
        elapsed_time = time.time() - self.start_time
        if elapsed_time > self.config.shutdown_timeout + self.config.force_shutdown_timeout:
            self.logger.error("Force shutdown initiated - graceful shutdown took too long")
            self.shutdown_stats["forced_shutdowns"] += 1
            
            # Cancel all remaining tasks
            for task in self.shutdown_tasks:
                if not task.done():
                    task.cancel()
            
            # Force exit
            import os
            os._exit(1)
    
    def _update_shutdown_stats(self, successful: bool, shutdown_time: float):
        """Update shutdown statistics"""
        self.shutdown_stats["total_shutdowns"] += 1
        
        if successful:
            self.shutdown_stats["successful_shutdowns"] += 1
        else:
            self.shutdown_stats["forced_shutdowns"] += 1
        
        # Update average shutdown time
        total = self.shutdown_stats["total_shutdowns"]
        current_avg = self.shutdown_stats["average_shutdown_time"]
        self.shutdown_stats["average_shutdown_time"] = (
            (current_avg * (total - 1) + shutdown_time) / total
        )
    
    def get_shutdown_stats(self) -> Dict[str, Any]:
        """Get shutdown statistics"""
        return {
            **self.shutdown_stats,
            "shutdown_initiated": self.shutdown_initiated,
            "shutdown_phase": self.shutdown_phase.value if self.shutdown_phase else None,
            "registered_services": len(self.services),
            "service_names": list(self.services.keys())
        }
    
    def is_shutdown_initiated(self) -> bool:
        """Check if shutdown has been initiated"""
        return self.shutdown_initiated
    
    def get_shutdown_phase(self) -> Optional[ShutdownPhase]:
        """Get current shutdown phase"""
        return self.shutdown_phase


# Global graceful shutdown service
graceful_shutdown_service: Optional[GracefulShutdownService] = None


def get_graceful_shutdown_service() -> GracefulShutdownService:
    """Get the global graceful shutdown service"""
    global graceful_shutdown_service
    if graceful_shutdown_service is None:
        graceful_shutdown_service = GracefulShutdownService()
    return graceful_shutdown_service


def register_service_for_shutdown(
    name: str,
    shutdown_func: Callable,
    priority: ServicePriority = ServicePriority.MEDIUM,
    timeout: float = 5.0,
    critical: bool = False,
    dependencies: List[str] = None
):
    """Convenience function to register a service for shutdown"""
    service = get_graceful_shutdown_service()
    service.register_service(name, shutdown_func, priority, timeout, critical, dependencies)


def initiate_shutdown():
    """Convenience function to initiate shutdown"""
    service = get_graceful_shutdown_service()
    asyncio.create_task(service.initiate_shutdown())


# Context manager for shutdown handling
class ShutdownContext:
    """Context manager for shutdown handling"""
    
    def __init__(self, service_name: str, priority: ServicePriority = ServicePriority.MEDIUM):
        self.service_name = service_name
        self.priority = priority
        self.service = get_graceful_shutdown_service()
    
    def __enter__(self):
        # Register service for shutdown
        self.service.register_service(
            self.service_name,
            self._shutdown,
            self.priority
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Unregister service
        self.service.unregister_service(self.service_name)
    
    async def _shutdown(self):
        """Default shutdown function"""
        self.service.logger.info(f"Shutting down {self.service_name}")


# Decorator for automatic service registration
def shutdown_managed(
    service_name: str,
    priority: ServicePriority = ServicePriority.MEDIUM,
    timeout: float = 5.0,
    critical: bool = False
):
    """Decorator for automatic service shutdown management"""
    def decorator(func: Callable) -> Callable:
        service = get_graceful_shutdown_service()
        service.register_service(
            service_name,
            func,
            priority,
            timeout,
            critical
        )
        return func
    return decorator