"""
Health Check and Monitoring Utilities

Provides health check endpoints and monitoring capabilities for the orchestration system.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field

from .agent_hierarchy import get_hierarchy_manager
from .agent_communication import get_communication_bus
from .workflow_executor import get_workflow_executor
from .config import get_config

logger = logging.getLogger(__name__)

@dataclass
class HealthStatus:
    """Health status for a component"""
    component: str
    status: str  # healthy, degraded, unhealthy, unknown
    message: str
    last_check: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "component": self.component,
            "status": self.status,
            "message": self.message,
            "last_check": self.last_check.isoformat(),
            "details": self.details
        }

class HealthChecker:
    """Comprehensive health checker for orchestration system"""
    
    def __init__(self):
        self.config = get_config()
        self.last_full_check: Optional[datetime] = None
        self.health_history: List[HealthStatus] = []
        self._max_history = 100
    
    async def check_all(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of all orchestration components.
        
        Returns:
            Dictionary with overall health status and component details
        """
        checks = {
            "overall_status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {},
            "summary": {
                "healthy": 0,
                "degraded": 0,
                "unhealthy": 0,
                "unknown": 0
            }
        }
        
        # Check each component
        component_checks = [
            ("hierarchy", self._check_hierarchy),
            ("communication", self._check_communication),
            ("workflow_executor", self._check_workflow_executor),
            ("system_resources", self._check_system_resources),
        ]
        
        for component_name, check_func in component_checks:
            try:
                status = await check_func()
                checks["components"][component_name] = status.to_dict()
                checks["summary"][status.status] = checks["summary"].get(status.status, 0) + 1
            except Exception as e:
                logger.error(f"Error checking {component_name}: {e}")
                status = HealthStatus(
                    component=component_name,
                    status="unknown",
                    message=f"Health check failed: {e}",
                    details={"error": str(e)}
                )
                checks["components"][component_name] = status.to_dict()
                checks["summary"]["unknown"] = checks["summary"].get("unknown", 0) + 1
        
        # Determine overall status
        if checks["summary"]["unhealthy"] > 0:
            checks["overall_status"] = "unhealthy"
        elif checks["summary"]["degraded"] > 0:
            checks["overall_status"] = "degraded"
        elif checks["summary"]["unknown"] > len(component_checks) / 2:
            checks["overall_status"] = "unknown"
        else:
            checks["overall_status"] = "healthy"
        
        self.last_full_check = datetime.now(timezone.utc)
        return checks
    
    async def _check_hierarchy(self) -> HealthStatus:
        """Check agent hierarchy health"""
        try:
            hierarchy = get_hierarchy_manager()
            status = hierarchy.get_hierarchy_status()
            
            total_agents = status["total_agents"]
            healthy_agents = status["health_summary"]["healthy"]
            failed_agents = status["health_summary"]["failed"]
            
            health_ratio = healthy_agents / total_agents if total_agents > 0 else 0.0
            
            if health_ratio >= 0.95:
                health_status = "healthy"
                message = f"Hierarchy healthy: {healthy_agents}/{total_agents} agents"
            elif health_ratio >= 0.80:
                health_status = "degraded"
                message = f"Hierarchy degraded: {healthy_agents}/{total_agents} agents healthy"
            else:
                health_status = "unhealthy"
                message = f"Hierarchy unhealthy: {failed_agents} failed agents"
            
            return HealthStatus(
                component="hierarchy",
                status=health_status,
                message=message,
                details={
                    "total_agents": total_agents,
                    "healthy_agents": healthy_agents,
                    "failed_agents": failed_agents,
                    "active_workflows": status["active_workflows"],
                    "layer_breakdown": status["layer_breakdown"]
                }
            )
        except Exception as e:
            return HealthStatus(
                component="hierarchy",
                status="unknown",
                message=f"Failed to check hierarchy: {e}",
                details={"error": str(e)}
            )
    
    async def _check_communication(self) -> HealthStatus:
        """Check communication bus health"""
        try:
            bus = get_communication_bus()
            metrics = await bus.get_communication_metrics()
            
            success_rate = metrics.get("success_rate_percent", 0.0)
            total_messages = metrics.get("total_messages", 0)
            failed_deliveries = metrics.get("failed_deliveries", 0)
            
            if success_rate >= 99.0:
                health_status = "healthy"
                message = f"Communication healthy: {success_rate:.1f}% success rate"
            elif success_rate >= 95.0:
                health_status = "degraded"
                message = f"Communication degraded: {success_rate:.1f}% success rate"
            else:
                health_status = "unhealthy"
                message = f"Communication unhealthy: {failed_deliveries} failed deliveries"
            
            return HealthStatus(
                component="communication",
                status=health_status,
                message=message,
                details={
                    "success_rate": success_rate,
                    "total_messages": total_messages,
                    "failed_deliveries": failed_deliveries,
                    "active_channels": metrics.get("active_channels", 0),
                    "queue_size": metrics.get("total_queue_size", 0)
                }
            )
        except Exception as e:
            return HealthStatus(
                component="communication",
                status="unknown",
                message=f"Failed to check communication: {e}",
                details={"error": str(e)}
            )
    
    async def _check_workflow_executor(self) -> HealthStatus:
        """Check workflow executor health"""
        try:
            executor = get_workflow_executor()
            active_executions = len(executor.active_executions)
            
            # Check for stuck executions
            stuck_count = 0
            current_time = datetime.now(timezone.utc)
            
            for exec_id, context in executor.active_executions.items():
                if context.started_at:
                    running_hours = (current_time - context.started_at).total_seconds() / 3600
                    if running_hours > self.config.workflow_execution_timeout_hours:
                        stuck_count += 1
            
            if stuck_count == 0 and active_executions < self.config.max_active_workflows:
                health_status = "healthy"
                message = f"Executor healthy: {active_executions} active workflows"
            elif stuck_count > 0:
                health_status = "degraded"
                message = f"Executor degraded: {stuck_count} stuck workflows"
            else:
                health_status = "unhealthy"
                message = f"Executor at capacity: {active_executions} workflows"
            
            return HealthStatus(
                component="workflow_executor",
                status=health_status,
                message=message,
                details={
                    "active_executions": active_executions,
                    "stuck_executions": stuck_count,
                    "max_workflows": self.config.max_active_workflows
                }
            )
        except Exception as e:
            return HealthStatus(
                component="workflow_executor",
                status="unknown",
                message=f"Failed to check executor: {e}",
                details={"error": str(e)}
            )
    
    async def _check_system_resources(self) -> HealthStatus:
        """Check system resource usage"""
        try:
            try:
                import psutil
                import os
            except ImportError:
                # psutil not available, skip resource check
                return HealthStatus(
                    component="system_resources",
                    status="unknown",
                    message="Resource monitoring unavailable (psutil not installed)",
                    details={"note": "Install psutil for resource monitoring"}
                )
            
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent(interval=0.1)
            
            memory_limit = self.config.memory_limit_mb
            memory_usage_ratio = memory_mb / memory_limit if memory_limit > 0 else 0.0
            
            if memory_usage_ratio < 0.80 and cpu_percent < 80.0:
                health_status = "healthy"
                message = f"Resources healthy: {memory_mb:.1f}MB memory, {cpu_percent:.1f}% CPU"
            elif memory_usage_ratio < 0.95 and cpu_percent < 95.0:
                health_status = "degraded"
                message = f"Resources degraded: {memory_mb:.1f}MB memory, {cpu_percent:.1f}% CPU"
            else:
                health_status = "unhealthy"
                message = f"Resources unhealthy: {memory_mb:.1f}MB memory, {cpu_percent:.1f}% CPU"
            
            return HealthStatus(
                component="system_resources",
                status=health_status,
                message=message,
                details={
                    "memory_mb": round(memory_mb, 1),
                    "memory_limit_mb": memory_limit,
                    "memory_usage_percent": round(memory_usage_ratio * 100, 1),
                    "cpu_percent": round(cpu_percent, 1)
                }
            )
        except Exception as e:
            return HealthStatus(
                component="system_resources",
                status="unknown",
                message=f"Failed to check resources: {e}",
                details={"error": str(e)}
            )
    
    async def start_health_monitoring(self):
        """Start background health monitoring"""
        while True:
            try:
                health_status = await self.check_all()
                self.health_history.append(health_status)
                
                # Keep only recent history
                if len(self.health_history) > self._max_history:
                    self.health_history = self.health_history[-self._max_history:]
                
                # Log if unhealthy
                if health_status["overall_status"] != "healthy":
                    logger.warning(
                        f"Health check: {health_status['overall_status']}. "
                        f"Components: {health_status['summary']}"
                    )
                
                await asyncio.sleep(self.config.health_check_interval_seconds)
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(self.config.health_check_interval_seconds)
    
    def get_health_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent health check history"""
        return [check for check in self.health_history[-limit:]]

# Global health checker
_global_health_checker: Optional[HealthChecker] = None

def get_health_checker() -> HealthChecker:
    """Get global health checker instance"""
    global _global_health_checker
    if _global_health_checker is None:
        _global_health_checker = HealthChecker()
    return _global_health_checker
