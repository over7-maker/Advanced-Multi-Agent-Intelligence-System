"""
Analytics endpoints for dashboard statistics
"""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query

from src.amas.services.prometheus_metrics_service import get_metrics_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/tasks")
async def get_task_analytics(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    task_type: Optional[str] = Query(None, description="Filter by task type"),
) -> Dict[str, Any]:
    """
    Get task analytics for dashboard
    
    Returns:
    - Total tasks
    - Completed tasks
    - Failed tasks
    - Average duration
    - Average quality score
    - Total cost
    - Success rate
    - Task distribution by type
    """
    try:
        metrics_service = get_metrics_service()
        
        # Get task metrics from Prometheus metrics
        # Note: PrometheusMetricsService doesn't have get_task_metrics() method
        # We'll use defaults for now - in production, these would come from database
        total_tasks = 0
        completed_tasks = 0
        failed_tasks = 0
        avg_duration = 0.0
        avg_quality_score = 0.0
        total_cost = 0.0
        task_distribution = {}
        
        # Calculate success rate
        success_rate = 0.0
        if total_tasks > 0:
            success_rate = (completed_tasks / total_tasks) * 100.0
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "avg_duration": avg_duration,
            "avg_quality_score": avg_quality_score,
            "total_cost": total_cost,
            "success_rate": success_rate,
            "task_distribution": task_distribution,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to get task analytics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task analytics: {str(e)}"
        )


@router.get("/agents")
async def get_agent_analytics() -> Dict[str, Any]:
    """
    Get agent analytics for dashboard
    
    Returns:
    - Total agents
    - Active agents
    - Average utilization
    - Top performing agents
    """
    try:
        metrics_service = get_metrics_service()
        
        # Get agent metrics from Prometheus metrics
        # Note: PrometheusMetricsService doesn't have get_agent_metrics() method
        # We'll use defaults for now - in production, these would come from database
        total_agents = 0
        active_agents = 0
        avg_utilization = 0.0
        top_agents = []
        
        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "avg_utilization": avg_utilization,
            "top_agents": top_agents,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to get agent analytics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent analytics: {str(e)}"
        )

