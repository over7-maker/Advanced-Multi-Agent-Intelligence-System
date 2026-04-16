"""
System metrics and monitoring endpoints
"""
import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from src.amas.services.prometheus_metrics_service import get_metrics_service
from src.amas.services.system_monitor import get_system_monitor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/metrics")
async def get_system_metrics() -> Dict[str, Any]:
    """
    Get system metrics for dashboard
    
    Returns:
    - CPU usage
    - Memory usage
    - Active connections
    - Task statistics
    - Agent statistics
    """
    try:
        import psutil
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        
        # Get metrics service for task/agent stats
        metrics_service = get_metrics_service()
        
        # Get task metrics from Prometheus metrics
        # Note: PrometheusMetricsService doesn't have get_task_metrics() method
        # We'll extract from Prometheus registry or use defaults
        task_metrics = {
            "total_executions": 0,
            "active_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
        }
        agent_metrics = {
            "total_agents": 0,
            "active_agents": 0,
            "avg_utilization": 0.0,
        }
        
        # Return data in format expected by frontend (SystemMetrics interface)
        return {
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory.percent,
            "memory_usage_bytes": memory.used,
            "disk_usage_bytes": disk.used,
            "active_tasks": task_metrics.get("active_tasks", 0),
            "queue_depth": 0,  # TODO: Get from actual queue
            "total_tasks": task_metrics.get("total_executions", 0),
            "completed_tasks": task_metrics.get("completed_tasks", 0),
            "failed_tasks": task_metrics.get("failed_tasks", 0),
            "active_agents": agent_metrics.get("active_agents", 0),
            "timestamp": datetime.now().isoformat(),
        }
    except ImportError:
        # Fallback if psutil is not available
        logger.warning("psutil not available, returning default metrics")
        # Return data in format expected by frontend (SystemMetrics interface)
        return {
            "cpu_usage_percent": 0.0,
            "memory_usage_percent": 0.0,
            "memory_usage_bytes": 0,
            "disk_usage_bytes": 0,
            "active_tasks": 0,
            "queue_depth": 0,
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "active_agents": 0,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system metrics: {str(e)}"
        )


@router.get("/ai-providers")
async def get_ai_provider_debug() -> Dict[str, Any]:
    """
    Local debugging: router health and stats (Ollama latency, last success/failure).
    Disabled unless AMAS_EXPOSE_AI_DEBUG=true or development environment.
    """
    env = (os.getenv("ENVIRONMENT") or "development").strip().lower()
    if not os.getenv("AMAS_EXPOSE_AI_DEBUG", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    ) and env not in ("development", "dev", "local", "test"):
        raise HTTPException(status_code=404, detail="Not found")
    try:
        from src.amas.ai.enhanced_router_class import get_ai_router

        router = get_ai_router()
        health = await router.get_provider_health()
        stats = await router.get_provider_stats()
        return {
            "providers_health": [
                {
                    "provider": h.provider,
                    "is_healthy": h.is_healthy,
                    "response_time_ms": h.response_time_ms,
                    "last_success": h.last_success,
                    "last_failure": h.last_failure,
                    "consecutive_failures": h.consecutive_failures,
                    "success_rate_24h": h.success_rate_24h,
                }
                for h in health
            ],
            "providers_stats": stats,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error("ai-providers debug failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topology-hotspots")
async def get_topology_hotspots(
    db: Optional[AsyncSession] = Depends(_optional_db_session),
) -> Dict[str, Any]:
    """
    F7-2 / FE-09: lightweight hotspots from real orchestrator queue depth + Postgres task counts.
    `summary` always carries drill-down-friendly counts when Postgres is reachable.
    Empty `hotspots` with available=false when nothing stands out.
    """
    hotspots: List[Dict[str, Any]] = []
    queue_depth: Optional[int] = None
    try:
        from src.amas.core.unified_intelligence_orchestrator import get_unified_orchestrator

        q = int(get_unified_orchestrator().get_internal_queue_depth() or 0)
        queue_depth = q
        if q >= 3:
            hotspots.append(
                {
                    "id": "orchestrator_queue",
                    "severity": "warn",
                    "detail": f"queue_depth={q}",
                    "source": "orchestrator",
                }
            )
        elif q > 0:
            hotspots.append(
                {
                    "id": "orchestrator_queue",
                    "severity": "info",
                    "detail": f"queue_depth={q}",
                    "source": "orchestrator",
                }
            )
    except Exception as e:
        logger.debug("topology-hotspots queue: %s", e)

    counts = await _task_counts_from_db(db)
    if counts:
        if counts["failed_tasks"] > 0:
            hotspots.append(
                {
                    "id": "task_failures",
                    "severity": "warn" if counts["failed_tasks"] > 5 else "info",
                    "detail": f"failed_tasks={counts['failed_tasks']}",
                    "source": "postgres",
                }
            )
        if counts["active_tasks"] > 20:
            hotspots.append(
                {
                    "id": "high_active_tasks",
                    "severity": "warn",
                    "detail": f"active_tasks={counts['active_tasks']}",
                    "source": "postgres",
                }
            )

    hotspots.extend(await _recent_failed_task_hotspots(db))

    summary: Dict[str, Any] = {
        "orchestrator_queue_depth": queue_depth,
        "postgres_task_counts": counts,
        "postgres_counts_available": counts is not None,
    }

    return {
        "schema_version": "topology.v2",
        "available": len(hotspots) > 0,
        "hotspots": hotspots,
        "summary": summary,
    }


@router.get("/health")
async def get_system_health() -> Dict[str, Any]:
    """
    Get system health status
    
    Returns health status of all system components
    """
    try:
        from src.api.routes.health import health_check
        
        # Use existing health check
        health_data = await health_check()
        
        return health_data
    except Exception as e:
        logger.error(f"Failed to get system health: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system health: {str(e)}"
        )


@router.get("/orchestrator/status")
async def get_orchestrator_status() -> Dict[str, Any]:
    """
    Get orchestrator status (Phase 1.1 requirement)
    
    Returns:
    - Orchestrator health status
    - Active agents count
    - Active tasks count
    - Total tasks processed
    - Agent details
    - Metrics
    """
    try:
        from src.amas.core.unified_intelligence_orchestrator import get_unified_orchestrator
        
        orchestrator = get_unified_orchestrator()
        
        # Get system status from orchestrator
        system_status = await orchestrator.get_system_status()
        
        # Get health check for detailed agent info
        health_check = await orchestrator.health_check()
        
        # Combine status and health data
        return {
            "orchestrator_status": system_status.get("orchestrator_status", "active"),
            "active_agents": system_status.get("active_agents", 0),
            "active_tasks": system_status.get("active_tasks", 0),
            "total_tasks": system_status.get("total_tasks", 0),
            "metrics": system_status.get("metrics", {}),
            "agent_health": health_check.get("agents", {}),
            "timestamp": system_status.get("timestamp", datetime.now().isoformat()),
        }
    except Exception as e:
        logger.error(f"Failed to get orchestrator status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get orchestrator status: {str(e)}"
        )

