# src/api/routes/metrics.py (PROMETHEUS METRICS ENDPOINT)
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Response

from src.amas.services.prometheus_metrics_service import get_metrics_service

router = APIRouter(prefix="/metrics", tags=["Monitoring"])

@router.get("")
async def prometheus_metrics(
    metrics_service: Any = Depends(get_metrics_service)
):
    """
    Prometheus metrics endpoint
    
    This endpoint is scraped by Prometheus server
    Format: Prometheus text exposition format
    """
    
    metrics_data = metrics_service.get_metrics()
    
    return Response(
        content=metrics_data,
        media_type=metrics_service.get_content_type()
    )

@router.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    
    Used by Kubernetes liveness/readiness probes
    """
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "amas-backend"
    }

