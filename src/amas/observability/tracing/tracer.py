"""
OpenTelemetry Tracing and Metrics for AMAS

Provides comprehensive observability with distributed tracing,
metrics collection, and SLO monitoring capabilities.
"""

import os
import logging
import time
import asyncio
from typing import Dict, Any, Optional, List, Callable, Union
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

# OpenTelemetry imports
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.trace import Status, StatusCode
from opentelemetry.semconv.trace import SpanAttributes

logger = logging.getLogger(__name__)

class AmasTracer:
    """Central tracing and metrics system for AMAS"""
    
    def __init__(self, 
                 service_name: str = "amas-orchestrator",
                 service_version: str = "1.0.0",
                 otlp_endpoint: Optional[str] = None,
                 environment: Optional[str] = None) -> None:
        """
        Initialize AMAS Tracer
        
        Args:
            service_name: Name of the service being traced
            service_version: Version of the service
            otlp_endpoint: OTLP endpoint URL (defaults to OTLP_ENDPOINT env var or http://localhost:4317)
            environment: Environment name (defaults to ENVIRONMENT env var or 'development')
            
        Raises:
            ValueError: If otlp_endpoint is not a valid URL format
        """
        # Validate inputs
        if not service_name or not isinstance(service_name, str):
            raise ValueError("service_name must be a non-empty string")
        if not service_version or not isinstance(service_version, str):
            raise ValueError("service_version must be a non-empty string")
        
        self.service_name = service_name
        self.service_version = service_version
        
        # Validate and set OTLP endpoint
        endpoint = otlp_endpoint or os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
        if not self._validate_endpoint(endpoint):
            raise ValueError(f"Invalid OTLP endpoint format: {endpoint}")
        self.otlp_endpoint = endpoint
        
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        
        # Setup resource information
        self.resource = Resource.create({
            "service.name": self.service_name,
            "service.version": self.service_version,
            "service.environment": self.environment,
            "service.instance.id": os.getenv("HOSTNAME", "unknown"),
        })
        
        self._setup_tracing()
        self._setup_metrics()
        self._setup_instrumentation()
        
        self.tracer = trace.get_tracer(__name__, self.service_version)
        self.meter = metrics.get_meter(__name__, self.service_version)
        self._create_metrics()
        
        logger.info(f"AMAS Tracer initialized for {service_name} v{service_version} in {self.environment}")
    
    def _validate_endpoint(self, endpoint: str) -> bool:
        """
        Validate OTLP endpoint URL format
        
        Args:
            endpoint: Endpoint URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            parsed = urlparse(endpoint)
            return parsed.scheme in ('http', 'https', 'grpc') and parsed.netloc
        except Exception:
            return False
    
    def _setup_tracing(self) -> None:
        """Configure OpenTelemetry tracing"""
        try:
            trace_exporter = OTLPSpanExporter(
                endpoint=self.otlp_endpoint,
                insecure=True
            )
            
            tracer_provider = TracerProvider(resource=self.resource)
            span_processor = BatchSpanProcessor(
                trace_exporter,
                max_queue_size=512,
                max_export_batch_size=128,
                export_timeout_millis=30000
            )
            
            tracer_provider.add_span_processor(span_processor)
            trace.set_tracer_provider(tracer_provider)
            
            logger.info(f"Tracing configured with endpoint: {self.otlp_endpoint}")
            
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to setup tracing due to invalid configuration: {e}", exc_info=True)
            trace.set_tracer_provider(TracerProvider(resource=self.resource))
        except Exception as e:
            logger.error(f"Failed to setup tracing: {e}", exc_info=True)
            # Use no-op tracer as fallback
            trace.set_tracer_provider(TracerProvider(resource=self.resource))
    
    def _setup_metrics(self) -> None:
        """Configure OpenTelemetry metrics"""
        try:
            metric_exporter = OTLPMetricExporter(
                endpoint=self.otlp_endpoint,
                insecure=True
            )
            
            metric_reader = PeriodicExportingMetricReader(
                exporter=metric_exporter,
                export_interval_millis=10000  # Export every 10 seconds
            )
            
            meter_provider = MeterProvider(
                resource=self.resource,
                metric_readers=[metric_reader]
            )
            
            metrics.set_meter_provider(meter_provider)
            
            logger.info("Metrics configured with OTLP exporter")
            
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to setup metrics due to invalid configuration: {e}", exc_info=True)
            metrics.set_meter_provider(MeterProvider(resource=self.resource))
        except Exception as e:
            logger.error(f"Failed to setup metrics: {e}", exc_info=True)
            # Use no-op meter as fallback
            metrics.set_meter_provider(MeterProvider(resource=self.resource))
    
    def _setup_instrumentation(self) -> None:
        """Setup automatic instrumentation"""
        try:
            # Instrument HTTP clients
            HTTPXClientInstrumentor().instrument()
            
            # Instrument logging
            LoggingInstrumentor().instrument(set_logging_format=True)
            
            logger.info("Automatic instrumentation configured")
            
        except Exception as e:
            logger.warning(f"Some instrumentation failed: {e}", exc_info=True)
    
    def _create_metrics(self) -> None:
        """Create application-specific metrics"""
        # Counter metrics for requests and errors
        self.agent_requests_total = self.meter.create_counter(
            name="amas_agent_requests_total",
            description="Total number of agent requests",
            unit="1"
        )
        
        self.agent_errors_total = self.meter.create_counter(
            name="amas_agent_errors_total",
            description="Total number of agent errors by type",
            unit="1"
        )
        
        # Histogram metrics for latencies
        self.agent_duration_seconds = self.meter.create_histogram(
            name="amas_agent_duration_seconds",
            description="Duration of agent operations in seconds",
            unit="s",
            boundaries=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
        )
        
        self.tool_call_duration_seconds = self.meter.create_histogram(
            name="amas_tool_call_duration_seconds",
            description="Duration of individual tool calls in seconds",
            unit="s",
            boundaries=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        # Gauge metrics for current state
        self.active_agents = self.meter.create_up_down_counter(
            name="amas_active_agents_current",
            description="Number of currently active agents",
            unit="1"
        )
        
        self.queue_depth = self.meter.create_up_down_counter(
            name="amas_queue_depth_current",
            description="Current depth of agent processing queue",
            unit="1"
        )
        
        # Token usage metrics
        self.token_usage_total = self.meter.create_counter(
            name="amas_tokens_used_total",
            description="Total tokens consumed by agents",
            unit="1"
        )
        
        self.cost_usd_total = self.meter.create_counter(
            name="amas_cost_usd_total",
            description="Total cost in USD for agent operations",
            unit="USD"
        )
    
    @asynccontextmanager
    async def trace_agent_execution(self, 
                                  agent_id: str,
                                  operation: str,
                                  user_id: Optional[str] = None,
                                  **attributes):
        """Context manager for tracing agent execution"""
        
        # Create span with comprehensive attributes
        span_attributes = {
            "agent.id": agent_id,
            "agent.operation": operation,
            "user.id": user_id or "anonymous",
            "service.name": self.service_name,
            "environment": self.environment,
            **attributes
        }
        
        with self.tracer.start_as_current_span(
            name=f"agent.{operation}",
            attributes=span_attributes
        ) as span:
            
            # Record start metrics
            start_time = time.time()
            self.active_agents.add(1, {"agent_id": agent_id})
            
            try:
                yield span
                
                # Mark span as successful
                span.set_status(Status(StatusCode.OK))
                
                # Record success metrics
                duration = time.time() - start_time
                labels = {"agent_id": agent_id, "operation": operation, "status": "success"}
                self.agent_requests_total.add(1, labels)
                self.agent_duration_seconds.record(duration, labels)
                
            except Exception as e:
                # Record error in span
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                
                # Record error metrics
                duration = time.time() - start_time
                error_labels = {
                    "agent_id": agent_id, 
                    "operation": operation, 
                    "status": "error",
                    "error_type": type(e).__name__
                }
                self.agent_requests_total.add(1, error_labels)
                self.agent_duration_seconds.record(duration, error_labels)
                self.agent_errors_total.add(1, error_labels)
                
                raise
            
            finally:
                # Always decrement active agents
                self.active_agents.add(-1, {"agent_id": agent_id})
    
    @asynccontextmanager
    async def trace_tool_call(self,
                            agent_id: str,
                            tool_name: str,
                            parameters: Optional[Dict] = None):
        """Context manager for tracing tool calls"""
        
        span_attributes = {
            "tool.name": tool_name,
            "agent.id": agent_id,
            "tool.parameters_count": len(parameters) if parameters else 0
        }
        
        # Add non-sensitive parameters to trace
        if parameters:
            safe_params = self._sanitize_parameters(parameters)
            for key, value in safe_params.items():
                if len(str(value)) < 100:  # Only include short values
                    span_attributes[f"tool.param.{key}"] = str(value)
        
        with self.tracer.start_as_current_span(
            name=f"tool.{tool_name}",
            attributes=span_attributes
        ) as span:
            
            start_time = time.time()
            
            try:
                yield span
                
                span.set_status(Status(StatusCode.OK))
                
                # Record tool success metrics
                duration = time.time() - start_time
                tool_labels = {
                    "agent_id": agent_id,
                    "tool_name": tool_name,
                    "status": "success"
                }
                self.tool_call_duration_seconds.record(duration, tool_labels)
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                
                # Record tool error metrics
                duration = time.time() - start_time
                tool_labels = {
                    "agent_id": agent_id,
                    "tool_name": tool_name,
                    "status": "error",
                    "error_type": type(e).__name__
                }
                self.tool_call_duration_seconds.record(duration, tool_labels)
                
                raise
    
    def _sanitize_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove sensitive data from parameters for tracing
        
        Args:
            parameters: Dictionary of parameters to sanitize
            
        Returns:
            Dictionary with sensitive values redacted
        """
        if not isinstance(parameters, dict):
            logger.warning(f"Expected dict for parameters, got {type(parameters)}")
            return {}
        
        sensitive_keys = {
            "password", "token", "secret", "key", "credential", "auth", "authorization",
            "api_key", "access_token", "refresh_token", "private_key", "cert", "certificate"
        }
        
        sanitized: Dict[str, Any] = {}
        for key, value in parameters.items():
            if not isinstance(key, str):
                continue
            key_lower = key.lower()
            if any(sensitive_key in key_lower for sensitive_key in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            else:
                sanitized[key] = f"[{type(value).__name__}]"
        
        return sanitized
    
    def record_token_usage(self, 
                          agent_id: str,
                          tokens_used: int,
                          cost_usd: float = 0.0,
                          model_name: Optional[str] = None) -> None:
        """
        Record token usage and cost metrics
        
        Args:
            agent_id: Identifier for the agent
            tokens_used: Number of tokens consumed
            cost_usd: Cost in USD (default: 0.0)
            model_name: Optional model name for labeling
            
        Raises:
            ValueError: If tokens_used is negative or cost_usd is negative
        """
        if not isinstance(agent_id, str) or not agent_id:
            raise ValueError("agent_id must be a non-empty string")
        if tokens_used < 0:
            raise ValueError(f"tokens_used must be non-negative, got {tokens_used}")
        if cost_usd < 0:
            raise ValueError(f"cost_usd must be non-negative, got {cost_usd}")
        
        labels: Dict[str, str] = {"agent_id": agent_id}
        if model_name:
            labels["model_name"] = model_name
        
        self.token_usage_total.add(tokens_used, labels)
        if cost_usd > 0:
            self.cost_usd_total.add(cost_usd, labels)
    
    def record_queue_metrics(self, queue_name: str, depth: int) -> None:
        """
        Record queue depth metrics
        
        Args:
            queue_name: Name of the queue
            depth: Current queue depth
            
        Raises:
            ValueError: If queue_name is empty or depth is negative
        """
        if not isinstance(queue_name, str) or not queue_name:
            raise ValueError("queue_name must be a non-empty string")
        if depth < 0:
            raise ValueError(f"depth must be non-negative, got {depth}")
        
        self.queue_depth.add(depth - self._get_current_queue_depth(queue_name), 
                            {"queue_name": queue_name})
    
    def _get_current_queue_depth(self, queue_name: str) -> int:
        """Get current queue depth (placeholder implementation)"""
        # In real implementation, this would query the actual queue
        return 0
    
    def get_current_trace_id(self) -> Optional[str]:
        """Get current trace ID for correlation"""
        current_span = trace.get_current_span()
        if current_span and current_span.get_span_context().trace_id:
            return format(current_span.get_span_context().trace_id, '032x')
        return None
    
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add event to current span"""
        current_span = trace.get_current_span()
        if current_span:
            current_span.add_event(name, attributes or {})
    
    def set_attribute(self, key: str, value: Any):
        """Set attribute on current span"""
        current_span = trace.get_current_span()
        if current_span:
            current_span.set_attribute(key, value)
    
    def instrument_fastapi(self, app: Any) -> None:
        """
        Instrument FastAPI application with OpenTelemetry
        
        Args:
            app: FastAPI application instance
            
        Raises:
            TypeError: If app is not a FastAPI application
        """
        if app is None:
            raise TypeError("app parameter cannot be None")
        
        # Check if app has FastAPI-like attributes
        if not hasattr(app, 'add_middleware') and not hasattr(app, 'router'):
            logger.warning("App may not be a FastAPI application, instrumentation may fail")
        
        try:
            FastAPIInstrumentor.instrument_app(
                app, 
                tracer_provider=trace.get_tracer_provider(),
                excluded_urls="health,metrics"
            )
            logger.info("FastAPI instrumentation enabled")
        except TypeError as e:
            logger.error(f"Failed to instrument FastAPI - invalid app type: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Failed to instrument FastAPI: {e}", exc_info=True)

# Performance monitoring utilities
class PerformanceMonitor:
    """Performance monitoring and SLO tracking"""
    
    def __init__(self, tracer: AmasTracer):
        self.tracer = tracer
        self._slo_violations: List[Dict[str, Any]] = []
        self._performance_baselines: Dict[str, float] = {
            "agent_execution_p95_seconds": 1.5,
            "tool_call_p95_seconds": 0.5,
            "success_rate_percent": 99.5
        }
    
    async def check_performance_regression(self, 
                                         operation: str,
                                         duration_seconds: float,
                                         success: bool) -> Optional[Dict[str, Any]]:
        """Check if current operation represents performance regression"""
        
        baseline_key = f"{operation}_p95_seconds"
        baseline_duration = self._performance_baselines.get(baseline_key, 10.0)
        
        regression_detected = None
        
        # Check latency regression (>50% slower than baseline)
        if duration_seconds > baseline_duration * 1.5:
            regression_detected = {
                "type": "latency_regression",
                "operation": operation,
                "current_duration": duration_seconds,
                "baseline_duration": baseline_duration,
                "regression_percent": ((duration_seconds - baseline_duration) / baseline_duration) * 100,
                "severity": "high" if duration_seconds > baseline_duration * 2.0 else "medium"
            }
        
        # Check success rate
        if not success:
            regression_detected = {
                "type": "success_rate_regression",
                "operation": operation,
                "success": success,
                "severity": "high"
            }
        
        if regression_detected:
            regression_detected["detected_at"] = datetime.now(timezone.utc).isoformat()
            regression_detected["trace_id"] = self.tracer.get_current_trace_id()
            
            # Add to violations list
            self._slo_violations.append(regression_detected)
            
            # Log the regression
            logger.warning(f"Performance regression detected: {regression_detected}")
        
        return regression_detected
    
    def get_recent_violations(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent SLO violations"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        return [
            violation for violation in self._slo_violations
            if datetime.fromisoformat(violation["detected_at"]) >= cutoff_time
        ]
    
    def update_baseline(self, operation: str, p95_duration: float):
        """Update performance baseline for operation"""
        baseline_key = f"{operation}_p95_seconds"
        old_baseline = self._performance_baselines.get(baseline_key, 0.0)
        
        # Only update if new baseline is significantly different
        if abs(p95_duration - old_baseline) / max(old_baseline, 0.1) > 0.2:
            self._performance_baselines[baseline_key] = p95_duration
            logger.info(f"Updated performance baseline for {operation}: {p95_duration:.3f}s")

# Decorators for easy tracing
def trace_agent_operation(operation_name: str, agent_id_param: str = "agent_id"):
    """Decorator to automatically trace agent operations"""
    def decorator(func: Callable):
        async def async_wrapper(*args, **kwargs):
            # Get tracer instance
            tracer_instance = get_tracer()
            
            # Extract agent_id from parameters
            agent_id = kwargs.get(agent_id_param, "unknown")
            
            async with tracer_instance.trace_agent_execution(
                agent_id=agent_id,
                operation=operation_name,
                function_name=func.__name__
            ):
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            # Handle sync functions
            return asyncio.create_task(async_wrapper(*args, **kwargs))
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator

def trace_tool_call(tool_name: str, agent_id_param: str = "agent_id"):
    """Decorator to automatically trace tool calls"""
    def decorator(func: Callable):
        async def async_wrapper(*args, **kwargs):
            tracer_instance = get_tracer()
            agent_id = kwargs.get(agent_id_param, "unknown")
            
            # Extract parameters for tracing
            parameters = {k: v for k, v in kwargs.items() if k != agent_id_param}
            
            async with tracer_instance.trace_tool_call(
                agent_id=agent_id,
                tool_name=tool_name,
                parameters=parameters
            ):
                return await func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else func
    
    return decorator

# Global tracer instance
_global_tracer: Optional[AmasTracer] = None
_performance_monitor: Optional[PerformanceMonitor] = None

def initialize_observability(service_name: str = "amas-orchestrator",
                           service_version: str = "1.0.0",
                           otlp_endpoint: Optional[str] = None,
                           environment: Optional[str] = None) -> AmasTracer:
    """Initialize global observability system"""
    global _global_tracer, _performance_monitor
    
    _global_tracer = AmasTracer(
        service_name=service_name,
        service_version=service_version,
        otlp_endpoint=otlp_endpoint,
        environment=environment
    )
    
    _performance_monitor = PerformanceMonitor(_global_tracer)
    
    logger.info("Global observability system initialized")
    return _global_tracer

def get_tracer() -> AmasTracer:
    """Get global tracer instance"""
    if _global_tracer is None:
        return initialize_observability()
    return _global_tracer

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    if _performance_monitor is None:
        initialize_observability()
    return _performance_monitor

# Health check endpoint data
async def get_observability_health() -> Dict[str, Any]:
    """Get observability system health status"""
    tracer_instance = get_tracer()
    monitor = get_performance_monitor()
    
    # Check if tracing is working
    with tracer_instance.tracer.start_as_current_span("health_check") as span:
        span.set_attribute("health_check.type", "observability")
        
        recent_violations = monitor.get_recent_violations(hours=1)
        
        return {
            "status": "healthy" if len(recent_violations) == 0 else "degraded",
            "service_name": tracer_instance.service_name,
            "environment": tracer_instance.environment,
            "otlp_endpoint": tracer_instance.otlp_endpoint,
            "recent_violations_count": len(recent_violations),
            "trace_id": tracer_instance.get_current_trace_id(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
