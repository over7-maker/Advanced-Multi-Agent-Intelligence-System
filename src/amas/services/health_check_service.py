#!/usr/bin/env python3
"""
Enhanced Health Check Service for AMAS
Implements comprehensive health monitoring with dependency checks, metrics, and observability
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import psutil
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status levels"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class DependencyType(str, Enum):
    """Types of dependencies"""

    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_API = "external_api"
    FILE_SYSTEM = "file_system"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    SERVICE = "service"


@dataclass
class HealthCheckResult:
    """Result of a health check"""

    name: str
    status: HealthStatus
    message: str
    response_time_ms: float
    timestamp: datetime
    metadata: Dict[str, Any] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class DependencyHealthCheck:
    """Base class for dependency health checks"""

    def __init__(
        self,
        name: str,
        dependency_type: DependencyType,
        timeout: float = 5.0,
        critical: bool = True,
    ):
        self.name = name
        self.dependency_type = dependency_type
        self.timeout = timeout
        self.critical = critical
        self.logger = logging.getLogger(f"health_check.{name}")

    async def check(self) -> HealthCheckResult:
        """Perform health check"""
        start_time = time.time()

        try:
            result = await asyncio.wait_for(self._check_impl(), timeout=self.timeout)
            response_time = (time.time() - start_time) * 1000

            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message=result.get("message", "OK"),
                response_time_ms=response_time,
                timestamp=datetime.now(timezone.utc),
                metadata=result.get("metadata", {}),
            )
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timed out after {self.timeout}s",
                response_time_ms=response_time,
                timestamp=datetime.now(timezone.utc),
                error="timeout",
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.logger.error(f"Health check failed for {self.name}: {e}")
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                response_time_ms=response_time,
                timestamp=datetime.now(timezone.utc),
                error=str(e),
            )

    async def _check_impl(self) -> Dict[str, Any]:
        """Implementation of the health check"""
        raise NotImplementedError


class DatabaseHealthCheck(DependencyHealthCheck):
    """Health check for database connections"""

    def __init__(self, name: str, connection_func, timeout: float = 5.0):
        super().__init__(name, DependencyType.DATABASE, timeout)
        self.connection_func = connection_func

    async def _check_impl(self) -> Dict[str, Any]:
        """Check database connection"""
        try:
            # Attempt to connect to database
            connection = await self.connection_func()

            # Test basic query
            cursor = connection.cursor()
            await cursor.execute("SELECT 1")
            result = await cursor.fetchone()
            await cursor.close()
            await connection.close()

            return {
                "message": "Database connection successful",
                "metadata": {
                    "query_result": result[0] if result else None,
                },
            }
        except Exception as e:
            raise Exception(f"Database connection failed: {e}")


class CacheHealthCheck(DependencyHealthCheck):
    """Health check for cache systems (Redis, etc.)"""

    def __init__(self, name: str, cache_client, timeout: float = 5.0):
        super().__init__(name, DependencyType.CACHE, timeout)
        self.cache_client = cache_client

    async def _check_impl(self) -> Dict[str, Any]:
        """Check cache connection"""
        try:
            # Test cache operations
            test_key = f"health_check_{int(time.time())}"
            test_value = "test_value"

            # Set and get test value
            await self.cache_client.set(test_key, test_value, ex=60)
            retrieved_value = await self.cache_client.get(test_key)
            await self.cache_client.delete(test_key)

            if retrieved_value != test_value:
                raise Exception("Cache value mismatch")

            return {
                "message": "Cache connection successful",
                "metadata": {
                    "test_key": test_key,
                    "test_value": test_value,
                },
            }
        except Exception as e:
            raise Exception(f"Cache connection failed: {e}")


class ExternalAPIHealthCheck(DependencyHealthCheck):
    """Health check for external APIs"""

    def __init__(self, name: str, api_url: str, api_func, timeout: float = 10.0):
        super().__init__(name, DependencyType.EXTERNAL_API, timeout)
        self.api_url = api_url
        self.api_func = api_func

    async def _check_impl(self) -> Dict[str, Any]:
        """Check external API"""
        try:
            # Make API call
            response = await self.api_func()

            return {
                "message": "External API accessible",
                "metadata": {
                    "api_url": self.api_url,
                    "response_status": response.get("status", "unknown"),
                },
            }
        except Exception as e:
            raise Exception(f"External API check failed: {e}")


class FileSystemHealthCheck(DependencyHealthCheck):
    """Health check for file system access"""

    def __init__(self, name: str, path: str, timeout: float = 5.0):
        super().__init__(name, DependencyType.FILE_SYSTEM, timeout)
        self.path = path

    async def _check_impl(self) -> Dict[str, Any]:
        """Check file system access"""
        try:
            # Check if path exists and is accessible
            if not os.path.exists(self.path):
                raise Exception(f"Path does not exist: {self.path}")

            if not os.access(self.path, os.R_OK):
                raise Exception(f"Path is not readable: {self.path}")

            # Check if it's a directory
            is_dir = os.path.isdir(self.path)

            # Get disk usage
            stat = os.statvfs(self.path)
            total_space = stat.f_frsize * stat.f_blocks
            free_space = stat.f_frsize * stat.f_bavail
            used_space = total_space - free_space

            return {
                "message": "File system accessible",
                "metadata": {
                    "path": self.path,
                    "is_directory": is_dir,
                    "total_space_bytes": total_space,
                    "free_space_bytes": free_space,
                    "used_space_bytes": used_space,
                    "usage_percent": (
                        (used_space / total_space) * 100 if total_space > 0 else 0
                    ),
                },
            }
        except Exception as e:
            raise Exception(f"File system check failed: {e}")


class MemoryHealthCheck(DependencyHealthCheck):
    """Health check for memory usage"""

    def __init__(
        self, name: str, max_usage_percent: float = 90.0, timeout: float = 5.0
    ):
        super().__init__(name, DependencyType.MEMORY, timeout)
        self.max_usage_percent = max_usage_percent

    async def _check_impl(self) -> Dict[str, Any]:
        """Check memory usage"""
        try:
            # Get memory information
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            available_mb = memory.available / (1024 * 1024)
            total_mb = memory.total / (1024 * 1024)
            used_mb = memory.used / (1024 * 1024)

            if usage_percent > self.max_usage_percent:
                raise Exception(f"Memory usage too high: {usage_percent:.1f}%")

            return {
                "message": "Memory usage within limits",
                "metadata": {
                    "usage_percent": usage_percent,
                    "available_mb": available_mb,
                    "total_mb": total_mb,
                    "used_mb": used_mb,
                    "max_usage_percent": self.max_usage_percent,
                },
            }
        except Exception as e:
            raise Exception(f"Memory check failed: {e}")


class DiskHealthCheck(DependencyHealthCheck):
    """Health check for disk usage"""

    def __init__(
        self,
        name: str,
        path: str = "/",
        max_usage_percent: float = 90.0,
        timeout: float = 5.0,
    ):
        super().__init__(name, DependencyType.DISK, timeout)
        self.path = path
        self.max_usage_percent = max_usage_percent

    async def _check_impl(self) -> Dict[str, Any]:
        """Check disk usage"""
        try:
            # Get disk usage
            disk_usage = psutil.disk_usage(self.path)
            usage_percent = (disk_usage.used / disk_usage.total) * 100

            if usage_percent > self.max_usage_percent:
                raise Exception(f"Disk usage too high: {usage_percent:.1f}%")

            return {
                "message": "Disk usage within limits",
                "metadata": {
                    "path": self.path,
                    "usage_percent": usage_percent,
                    "total_bytes": disk_usage.total,
                    "used_bytes": disk_usage.used,
                    "free_bytes": disk_usage.free,
                    "max_usage_percent": self.max_usage_percent,
                },
            }
        except Exception as e:
            raise Exception(f"Disk check failed: {e}")


class NetworkHealthCheck(DependencyHealthCheck):
    """Health check for network connectivity"""

    def __init__(self, name: str, host: str, port: int, timeout: float = 5.0):
        super().__init__(name, DependencyType.NETWORK, timeout)
        self.host = host
        self.port = port

    async def _check_impl(self) -> Dict[str, Any]:
        """Check network connectivity"""
        try:
            # Test network connection
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port), timeout=self.timeout
            )
            writer.close()
            await writer.wait_closed()

            return {
                "message": "Network connection successful",
                "metadata": {
                    "host": self.host,
                    "port": self.port,
                },
            }
        except Exception as e:
            raise Exception(f"Network connection failed: {e}")


class ServiceHealthCheck(DependencyHealthCheck):
    """Health check for internal services"""

    def __init__(self, name: str, service_func, timeout: float = 5.0):
        super().__init__(name, DependencyType.SERVICE, timeout)
        self.service_func = service_func

    async def _check_impl(self) -> Dict[str, Any]:
        """Check service health"""
        try:
            # Call service health check function
            result = await self.service_func()

            return {
                "message": "Service is healthy",
                "metadata": result,
            }
        except Exception as e:
            raise Exception(f"Service health check failed: {e}")


class HealthCheckService:
    """Service for managing health checks"""

    def __init__(self):
        self.checks: List[DependencyHealthCheck] = []
        self.logger = logging.getLogger(__name__)
        self.start_time = time.time()

    def add_check(self, check: DependencyHealthCheck):
        """Add a health check"""
        self.checks.append(check)
        self.logger.info(f"Added health check: {check.name}")

    def remove_check(self, name: str) -> bool:
        """Remove a health check by name"""
        for i, check in enumerate(self.checks):
            if check.name == name:
                del self.checks[i]
                self.logger.info(f"Removed health check: {name}")
                return True
        return False

    async def check_all(self) -> Dict[str, Any]:
        """Run all health checks"""
        self.logger.debug("Running all health checks")

        # Run all checks concurrently
        check_tasks = [check.check() for check in self.checks]
        results = await asyncio.gather(*check_tasks, return_exceptions=True)

        # Process results
        check_results = []
        overall_status = HealthStatus.HEALTHY
        critical_failures = 0

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Handle exceptions from gather
                check_result = HealthCheckResult(
                    name=self.checks[i].name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed: {str(result)}",
                    response_time_ms=0.0,
                    timestamp=datetime.now(timezone.utc),
                    error=str(result),
                )
            else:
                check_result = result

            check_results.append(check_result)

            # Update overall status
            if check_result.status == HealthStatus.UNHEALTHY:
                if self.checks[i].critical:
                    critical_failures += 1
                    overall_status = HealthStatus.UNHEALTHY
                elif overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
            elif (
                check_result.status == HealthStatus.DEGRADED
                and overall_status == HealthStatus.HEALTHY
            ):
                overall_status = HealthStatus.DEGRADED

        # Get system information
        system_info = self._get_system_info()

        return {
            "status": overall_status.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": time.time() - self.start_time,
            "checks": [result.__dict__ for result in check_results],
            "system": system_info,
            "summary": {
                "total_checks": len(self.checks),
                "healthy_checks": len(
                    [r for r in check_results if r.status == HealthStatus.HEALTHY]
                ),
                "degraded_checks": len(
                    [r for r in check_results if r.status == HealthStatus.DEGRADED]
                ),
                "unhealthy_checks": len(
                    [r for r in check_results if r.status == HealthStatus.UNHEALTHY]
                ),
                "critical_failures": critical_failures,
            },
        }

    async def check_dependency(self, name: str) -> Optional[HealthCheckResult]:
        """Check a specific dependency"""
        for check in self.checks:
            if check.name == name:
                return await check.check()
        return None

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            # Get process information
            process = psutil.Process()

            # Get system information
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            cpu_percent = psutil.cpu_percent(interval=1)

            return {
                "process": {
                    "pid": process.pid,
                    "memory_mb": process.memory_info().rss / (1024 * 1024),
                    "cpu_percent": process.cpu_percent(),
                    "num_threads": process.num_threads(),
                    "create_time": process.create_time(),
                },
                "system": {
                    "memory": {
                        "total_mb": memory.total / (1024 * 1024),
                        "available_mb": memory.available / (1024 * 1024),
                        "used_mb": memory.used / (1024 * 1024),
                        "percent": memory.percent,
                    },
                    "disk": {
                        "total_gb": disk.total / (1024 * 1024 * 1024),
                        "used_gb": disk.used / (1024 * 1024 * 1024),
                        "free_gb": disk.free / (1024 * 1024 * 1024),
                        "percent": (disk.used / disk.total) * 100,
                    },
                    "cpu_percent": cpu_percent,
                },
                "python": {
                    "version": f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}.{psutil.sys.version_info.micro}",
                    "platform": psutil.sys.platform,
                },
            }
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            return {"error": str(e)}


# Global health check service
_health_check_service: Optional[HealthCheckService] = None


def get_health_check_service() -> HealthCheckService:
    """Get the global health check service"""
    global _health_check_service
    if _health_check_service is None:
        _health_check_service = HealthCheckService()
    return _health_check_service


def add_health_check(check: DependencyHealthCheck):
    """Add a health check to the global service"""
    service = get_health_check_service()
    service.add_check(check)


def remove_health_check(name: str) -> bool:
    """Remove a health check from the global service"""
    service = get_health_check_service()
    return service.remove_check(name)


async def check_health() -> Dict[str, Any]:
    """Check health of all dependencies"""
    service = get_health_check_service()
    return await service.check_all()


async def check_dependency_health(name: str) -> Optional[HealthCheckResult]:
    """Check health of a specific dependency"""
    service = get_health_check_service()
    return await service.check_dependency(name)


# Convenience functions for common health checks
def add_database_health_check(name: str, connection_func, timeout: float = 5.0):
    """Add database health check"""
    check = DatabaseHealthCheck(name, connection_func, timeout)
    add_health_check(check)


def add_cache_health_check(name: str, cache_client, timeout: float = 5.0):
    """Add cache health check"""
    check = CacheHealthCheck(name, cache_client, timeout)
    add_health_check(check)


def add_external_api_health_check(
    name: str, api_url: str, api_func, timeout: float = 10.0
):
    """Add external API health check"""
    check = ExternalAPIHealthCheck(name, api_url, api_func, timeout)
    add_health_check(check)


def add_file_system_health_check(name: str, path: str, timeout: float = 5.0):
    """Add file system health check"""
    check = FileSystemHealthCheck(name, path, timeout)
    add_health_check(check)


def add_memory_health_check(
    name: str, max_usage_percent: float = 90.0, timeout: float = 5.0
):
    """Add memory health check"""
    check = MemoryHealthCheck(name, max_usage_percent, timeout)
    add_health_check(check)


def add_disk_health_check(
    name: str, path: str = "/", max_usage_percent: float = 90.0, timeout: float = 5.0
):
    """Add disk health check"""
    check = DiskHealthCheck(name, path, max_usage_percent, timeout)
    add_health_check(check)


def add_network_health_check(name: str, host: str, port: int, timeout: float = 5.0):
    """Add network health check"""
    check = NetworkHealthCheck(name, host, port, timeout)
    add_health_check(check)


def add_service_health_check(name: str, service_func, timeout: float = 5.0):
    """Add service health check"""
    check = ServiceHealthCheck(name, service_func, timeout)
    add_health_check(check)


if __name__ == "__main__":
    # Test the health check service
    import asyncio

    async def test_health_checks():
        # Add some test health checks
        add_memory_health_check("memory", 90.0)
        add_disk_health_check("disk", "/", 90.0)
        add_file_system_health_check("temp", "/tmp")

        # Run health checks
        result = await check_health()
        print(json.dumps(result, indent=2, default=str))

    asyncio.run(test_health_checks())
