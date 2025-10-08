"""
Monitoring middleware for AMAS
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.config.settings import get_settings


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Monitoring middleware for metrics collection"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Collect metrics for monitoring"""
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate metrics
        process_time = time.time() - start_time
        
        # Collect metrics (this would integrate with Prometheus)
        if get_settings().monitoring.prometheus_enabled:
            # This would collect actual metrics
            pass
        
        return response