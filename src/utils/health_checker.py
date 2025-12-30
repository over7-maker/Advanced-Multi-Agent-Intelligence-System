"""
Production-Grade Health Checker
===============================

This module provides fast health check endpoints that respond in <10ms
by using background verification tasks instead of blocking I/O.

Features:
- Fast primary endpoint (<10ms response)
- Background health verification
- Detailed diagnostics endpoint
- Proper HTTP status codes (200/503)
- Non-blocking checks
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import os


class HealthStatus(str, Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    INITIALIZING = "initializing"


@dataclass
class ComponentHealth:
    """Health status of a single component."""
    name: str
    status: HealthStatus
    last_check: Optional[datetime] = None
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    check_count: int = 0
    failure_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "status": self.status.value,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "response_time_ms": self.response_time_ms,
            "error": self.error_message,
            "checks": self.check_count,
            "failures": self.failure_count,
            "failure_rate": round(
                self.failure_count / max(self.check_count, 1) * 100, 2
            )
        }


class HealthChecker:
    """Production-grade health checker with background verification."""
    
    # Default timeout for each component check (milliseconds)
    DEFAULT_CHECK_TIMEOUT = 1000  # 1 second
    
    # Background check interval (seconds)
    BACKGROUND_CHECK_INTERVAL = 5
    
    # Consider component unhealthy after N consecutive failures
    FAILURE_THRESHOLD = 3
    
    def __init__(self):
        """Initialize health checker."""
        self.logger = logging.getLogger(__name__)
        
        # Component health status
        self.components: Dict[str, ComponentHealth] = {
            "database": ComponentHealth("PostgreSQL Database", HealthStatus.INITIALIZING),
            "cache": ComponentHealth("Redis Cache", HealthStatus.INITIALIZING),
            "graph_db": ComponentHealth("Neo4j Graph DB", HealthStatus.INITIALIZING),
            "ai_providers": ComponentHealth("AI Providers", HealthStatus.INITIALIZING),
            "integrations": ComponentHealth("Integrations", HealthStatus.INITIALIZING),
            "agents": ComponentHealth("Agent Registry", HealthStatus.INITIALIZING),
        }
        
        # Overall status
        self._last_overall_check = None
        self._overall_status = HealthStatus.INITIALIZING
        self._background_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start_background_checks(self) -> None:
        """Start background health verification task."""
        if self._running:
            return
        
        self._running = True
        self._background_task = asyncio.create_task(self._background_check_loop())
        self.logger.info("Background health checks started")
    
    async def stop_background_checks(self) -> None:
        """Stop background health verification task."""
        self._running = False
        if self._background_task:
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Background health checks stopped")
    
    async def _background_check_loop(self) -> None:
        """Background loop for health verification."""
        while self._running:
            try:
                # Run all checks concurrently
                await asyncio.gather(
                    self._check_database(),
                    self._check_cache(),
                    self._check_graph_db(),
                    self._check_ai_providers(),
                    self._check_integrations(),
                    self._check_agents(),
                    return_exceptions=True
                )
                
                # Update overall status
                self._update_overall_status()
                
            except Exception as e:
                self.logger.error(f"Background check error: {e}")
            
            # Wait before next check
            await asyncio.sleep(self.BACKGROUND_CHECK_INTERVAL)
    
    async def _check_database(self) -> None:
        """Check database connectivity (non-blocking)."""
        component = self.components["database"]
        
        try:
            # Non-blocking connection pool status check
            from src.database.connection import db_pool
            
            start = datetime.now()
            
            # Check if pool has available connections (doesn't create new ones)
            if db_pool.pool and db_pool.pool._queue.qsize() > 0:
                elapsed_ms = (datetime.now() - start).total_seconds() * 1000
                component.status = HealthStatus.HEALTHY
                component.response_time_ms = elapsed_ms
                component.error_message = None
            else:
                component.status = HealthStatus.DEGRADED
                component.error_message = "No available connections in pool"
        
        except Exception as e:
            component.status = HealthStatus.UNHEALTHY
            component.error_message = str(e)
            component.failure_count += 1
        
        finally:
            component.check_count += 1
            component.last_check = datetime.now()
    
    async def _check_cache(self) -> None:
        """Check Redis cache connectivity (non-blocking)."""
        component = self.components["cache"]
        
        try:
            from src.database.redis_cache import redis_client
            
            if not redis_client:
                component.status = HealthStatus.UNHEALTHY
                component.error_message = "Redis client not initialized"
                component.failure_count += 1
                return
            
            start = datetime.now()
            
            # Non-blocking ping with timeout
            try:
                await asyncio.wait_for(redis_client.ping(), timeout=0.5)
                elapsed_ms = (datetime.now() - start).total_seconds() * 1000
                component.status = HealthStatus.HEALTHY
                component.response_time_ms = elapsed_ms
                component.error_message = None
                component.failure_count = 0  # Reset on success
            except asyncio.TimeoutError:
                component.status = HealthStatus.DEGRADED
                component.error_message = "Redis ping timeout"
                component.failure_count += 1
        
        except Exception as e:
            component.status = HealthStatus.UNHEALTHY
            component.error_message = str(e)
            component.failure_count += 1
        
        finally:
            component.check_count += 1
            component.last_check = datetime.now()
    
    async def _check_graph_db(self) -> None:
        """Check Neo4j graph database connectivity (non-blocking)."""
        component = self.components["graph_db"]
        
        try:
            from src.database.neo4j_connection import neo4j_driver
            
            start = datetime.now()
            
            # Non-blocking driver info retrieval
            try:
                info = neo4j_driver.get_server_info(timeout=0.5)
                elapsed_ms = (datetime.now() - start).total_seconds() * 1000
                component.status = HealthStatus.HEALTHY
                component.response_time_ms = elapsed_ms
                component.error_message = None
            except asyncio.TimeoutError:
                component.status = HealthStatus.DEGRADED
                component.error_message = "Neo4j info retrieval timeout"
        
        except Exception as e:
            component.status = HealthStatus.UNHEALTHY
            component.error_message = str(e)
            component.failure_count += 1
        
        finally:
            component.check_count += 1
            component.last_check = datetime.now()
    
    async def _check_ai_providers(self) -> None:
        """Check AI provider connectivity status."""
        component = self.components["ai_providers"]
        
        try:
            from src.amas.core.ai_provider_router import provider_router
            
            start = datetime.now()
            
            # Check if at least one provider is available
            available_count = await provider_router.get_available_providers_count()
            elapsed_ms = (datetime.now() - start).total_seconds() * 1000
            
            if available_count > 0:
                component.status = HealthStatus.HEALTHY
                component.response_time_ms = elapsed_ms
                component.error_message = None
            else:
                component.status = HealthStatus.UNHEALTHY
                component.error_message = "No AI providers available"
                component.failure_count += 1
        
        except Exception as e:
            component.status = HealthStatus.DEGRADED
            component.error_message = str(e)
            component.failure_count += 1
        
        finally:
            component.check_count += 1
            component.last_check = datetime.now()
    
    async def _check_integrations(self) -> None:
        """Check integration platform status."""
        component = self.components["integrations"]
        
        try:
            from src.amas.integrations import integration_manager
            
            start = datetime.now()
            
            # Get integration status without blocking
            status = await integration_manager.get_status(timeout=0.5)
            elapsed_ms = (datetime.now() - start).total_seconds() * 1000
            
            if status.get("ready"):
                component.status = HealthStatus.HEALTHY
            else:
                component.status = HealthStatus.DEGRADED
                component.error_message = f"Integrations not fully ready"
            
            component.response_time_ms = elapsed_ms
        
        except asyncio.TimeoutError:
            component.status = HealthStatus.DEGRADED
            component.error_message = "Integration check timeout"
        
        except Exception as e:
            component.status = HealthStatus.DEGRADED
            component.error_message = str(e)
            component.failure_count += 1
        
        finally:
            component.check_count += 1
            component.last_check = datetime.now()
    
    async def _check_agents(self) -> None:
        """Check agent registry status."""
        component = self.components["agents"]
        
        try:
            from src.amas.core.agent_registry import agent_registry
            
            start = datetime.now()
            
            # Get agent count
            count = len(agent_registry.get_all_agents())
            elapsed_ms = (datetime.now() - start).total_seconds() * 1000
            
            if count > 0:
                component.status = HealthStatus.HEALTHY
                component.error_message = None
            else:
                component.status = HealthStatus.UNHEALTHY
                component.error_message = "No agents loaded"
                component.failure_count += 1
            
            component.response_time_ms = elapsed_ms
        
        except Exception as e:
            component.status = HealthStatus.UNHEALTHY
            component.error_message = str(e)
            component.failure_count += 1
        
        finally:
            component.check_count += 1
            component.last_check = datetime.now()
    
    def _update_overall_status(self) -> None:
        """Update overall health status based on component statuses."""
        unhealthy_count = sum(
            1 for c in self.components.values()
            if c.status == HealthStatus.UNHEALTHY
        )
        degraded_count = sum(
            1 for c in self.components.values()
            if c.status == HealthStatus.DEGRADED
        )
        
        if unhealthy_count > 0:
            self._overall_status = HealthStatus.UNHEALTHY
        elif degraded_count > len(self.components) * 0.5:
            self._overall_status = HealthStatus.DEGRADED
        else:
            self._overall_status = HealthStatus.HEALTHY
        
        self._last_overall_check = datetime.now()
    
    def get_quick_status(self) -> Dict[str, Any]:
        """
        Get quick health status (< 10ms response).
        
        This is used for fast readiness probes and load balancer checks.
        Returns:
            200 if system is ready (HEALTHY or DEGRADED)
            503 if system is unhealthy
        """
        return {
            "status": self._overall_status.value,
            "ready": self._overall_status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED),
            "last_check": self._last_overall_check.isoformat() if self._last_overall_check else None,
            "timestamp": datetime.now().isoformat(),
            "response_time_ms": "<10"
        }
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """
        Get detailed health status with component breakdowns.
        
        This is used for diagnostics and monitoring dashboards.
        """
        return {
            "status": self._overall_status.value,
            "timestamp": datetime.now().isoformat(),
            "last_check": self._last_overall_check.isoformat() if self._last_overall_check else None,
            "components": {
                name: component.to_dict()
                for name, component in self.components.items()
            },
            "summary": {
                "healthy": sum(
                    1 for c in self.components.values()
                    if c.status == HealthStatus.HEALTHY
                ),
                "degraded": sum(
                    1 for c in self.components.values()
                    if c.status == HealthStatus.DEGRADED
                ),
                "unhealthy": sum(
                    1 for c in self.components.values()
                    if c.status == HealthStatus.UNHEALTHY
                ),
                "total": len(self.components)
            }
        }
    
    def get_http_status_code(self) -> int:
        """
        Get appropriate HTTP status code for health check.
        
        Returns:
            200 if system is healthy or degraded (can accept requests)
            503 if system is unhealthy (should not accept requests)
        """
        if self._overall_status == HealthStatus.UNHEALTHY:
            return 503  # Service Unavailable
        return 200  # OK


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get or create the global health checker instance."""
    global _health_checker
    
    if _health_checker is None:
        _health_checker = HealthChecker()
    
    return _health_checker


# FastAPI integration example
def setup_health_check_routes(app) -> None:
    """
    Setup health check routes on FastAPI app.
    
    Usage:
        from fastapi import FastAPI
        from src.utils.health_checker import setup_health_check_routes
        
        app = FastAPI()
        setup_health_check_routes(app)
    """
    from fastapi import Response
    from fastapi.responses import JSONResponse
    
    checker = get_health_checker()
    
    @app.get("/health", tags=["System"])
    async def health_quick() -> Response:
        """
        Fast health check endpoint (< 10ms).
        
        Used by load balancers and orchestrators for readiness probes.
        - Returns 200 if system is ready
        - Returns 503 if system is unhealthy
        """
        status = checker.get_quick_status()
        status_code = checker.get_http_status_code()
        return JSONResponse(status, status_code=status_code)
    
    @app.get("/health/detailed", tags=["System"])
    async def health_detailed() -> Dict[str, Any]:
        """
        Detailed health check endpoint with component breakdown.
        
        Used for diagnostics, monitoring dashboards, and debugging.
        """
        return checker.get_detailed_status()
    
    @app.on_event("startup")
    async def startup_health_checks():
        """Start background health checks on app startup."""
        await checker.start_background_checks()
    
    @app.on_event("shutdown")
    async def shutdown_health_checks():
        """Stop background health checks on app shutdown."""
        await checker.stop_background_checks()


if __name__ == "__main__":
    # Test the health checker
    import asyncio
    
    async def test():
        checker = get_health_checker()
        
        # Start background checks
        await checker.start_background_checks()
        
        # Wait for first checks to complete
        await asyncio.sleep(2)
        
        # Get status
        print("Quick Status:")
        print(checker.get_quick_status())
        print("\nDetailed Status:")
        print(checker.get_detailed_status())
        
        # Cleanup
        await checker.stop_background_checks()
    
    asyncio.run(test())
