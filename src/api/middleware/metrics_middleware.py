# src/api/middleware/metrics_middleware.py (AUTO-METRICS MIDDLEWARE)
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging
from src.amas.services.prometheus_metrics_service import get_metrics_service

logger = logging.getLogger(__name__)

class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically collect HTTP request metrics
    
    ✅ Request counter
    ✅ Request duration
    ✅ Active requests
    ✅ Status code distribution
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.metrics_service = get_metrics_service()
    
    async def dispatch(self, request: Request, call_next):
        # Skip metrics endpoint itself
        if request.url.path == "/metrics" or request.url.path.startswith("/metrics"):
            return await call_next(request)
        
        # Extract endpoint pattern (remove path parameters)
        endpoint = request.url.path
        method = request.method
        
        # Increment active requests
        self.metrics_service.metrics["amas_http_requests_active"].labels(
            method=method,
            endpoint=endpoint
        ).inc()
        
        # Record request start time
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            
            self.metrics_service.record_http_request(
                method=method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration=duration
            )
            
            return response
        
        except Exception as e:
            # Record error
            duration = time.time() - start_time
            
            self.metrics_service.record_http_request(
                method=method,
                endpoint=endpoint,
                status_code=500,
                duration=duration
            )
            
            # Record error metric
            self.metrics_service.metrics["errors_total"].labels(
                error_type=type(e).__name__,
                component="api"
            ).inc()
            
            raise
        
        finally:
            # Decrement active requests
            self.metrics_service.metrics["amas_http_requests_active"].labels(
                method=method,
                endpoint=endpoint
            ).dec()

