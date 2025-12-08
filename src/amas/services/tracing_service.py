# src/amas/services/tracing_service.py (OPENTELEMETRY DISTRIBUTED TRACING)
import asyncio
import logging
import os
from typing import Optional, Dict, Any
from functools import wraps

logger = logging.getLogger(__name__)

# Try to import OpenTelemetry - make it optional
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.trace import Status, StatusCode
    OPENTELEMETRY_AVAILABLE = True
    
    try:
        from opentelemetry.exporter.jaeger.thrift import JaegerExporter
        JAEGER_AVAILABLE = True
    except ImportError:
        JAEGER_AVAILABLE = False
        
    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        OTLP_AVAILABLE = True
    except ImportError:
        OTLP_AVAILABLE = False
        
    try:
        from opentelemetry.semconv.resource import ResourceAttributes
        SEMCONV_AVAILABLE = True
    except ImportError:
        SEMCONV_AVAILABLE = False
        
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FASTAPI_INSTRUMENTOR_AVAILABLE = True
    except ImportError:
        FASTAPI_INSTRUMENTOR_AVAILABLE = False
        
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    # Log as debug instead of warning - OpenTelemetry is optional
    logger.debug("OpenTelemetry not available - tracing will be disabled")

class TracingService:
    """
    OpenTelemetry distributed tracing service
    
    ✅ Automatic span creation
    ✅ Context propagation
    ✅ Custom attributes
    ✅ Error tracking
    ✅ Performance monitoring
    ✅ Multi-exporter support (Jaeger, OTLP, Console)
    """
    
    def __init__(
        self,
        service_name: str = "amas-backend",
        service_version: str = "1.0.0",
        environment: str = "production",
        jaeger_endpoint: str = None,
        otlp_endpoint: str = None
    ):
        if not OPENTELEMETRY_AVAILABLE:
            logger.debug("OpenTelemetry not available - TracingService will be a no-op")
            self.enabled = False
            return
        
        self.enabled = True
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        
        # Create resource
        resource_dict = {
            "service.name": service_name,
            "service.version": service_version,
            "deployment.environment": environment,
            "service.namespace": "amas",
        }
        
        if SEMCONV_AVAILABLE:
            resource_dict = {
                ResourceAttributes.SERVICE_NAME: service_name,
                ResourceAttributes.SERVICE_VERSION: service_version,
                ResourceAttributes.DEPLOYMENT_ENVIRONMENT: environment,
                "service.namespace": "amas",
            }
        
        self.resource = Resource.create(resource_dict)
        
        # Initialize tracer provider
        self.tracer_provider = TracerProvider(resource=self.resource)
        
        # Configure exporters
        self._configure_exporters(jaeger_endpoint, otlp_endpoint)
        
        # Set global tracer provider
        trace.set_tracer_provider(self.tracer_provider)
        
        # Get tracer
        self.tracer = trace.get_tracer(__name__)
        
        logger.info(f"TracingService initialized: {service_name} ({environment})")
    
    def _configure_exporters(
        self,
        jaeger_endpoint: Optional[str],
        otlp_endpoint: Optional[str]
    ):
        """Configure span exporters"""
        
        if not self.enabled:
            return
        
        # Console exporter (development)
        if os.getenv("TRACING_CONSOLE", "false").lower() == "true":
            console_exporter = ConsoleSpanExporter()
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(console_exporter)
            )
            logger.info("Console trace exporter enabled")
        
        # Jaeger exporter
        if JAEGER_AVAILABLE and (jaeger_endpoint or os.getenv("JAEGER_ENDPOINT")):
            endpoint = jaeger_endpoint or os.getenv("JAEGER_ENDPOINT", "jaeger:6831")
            
            try:
                if ":" in endpoint:
                    host, port = endpoint.split(":")
                    port = int(port)
                else:
                    host = endpoint
                    port = 6831
                
                jaeger_exporter = JaegerExporter(
                    agent_host_name=host,
                    agent_port=port,
                )
                
                self.tracer_provider.add_span_processor(
                    BatchSpanProcessor(jaeger_exporter)
                )
                logger.info(f"Jaeger trace exporter configured: {host}:{port}")
            except Exception as e:
                logger.warning(f"Failed to configure Jaeger exporter: {e}")
        
        # OTLP exporter (for Tempo, Grafana Cloud, etc.)
        if OTLP_AVAILABLE and (otlp_endpoint or os.getenv("OTLP_ENDPOINT")):
            endpoint = otlp_endpoint or os.getenv("OTLP_ENDPOINT")
            
            try:
                otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
                
                self.tracer_provider.add_span_processor(
                    BatchSpanProcessor(otlp_exporter)
                )
                logger.info(f"OTLP trace exporter configured: {endpoint}")
            except Exception as e:
                logger.warning(f"Failed to configure OTLP exporter: {e}")
    
    def instrument_app(self, app):
        """
        Instrument FastAPI application
        
        Automatically creates spans for all HTTP requests
        """
        
        if not self.enabled or not FASTAPI_INSTRUMENTOR_AVAILABLE:
            logger.debug("FastAPI instrumentation not available")
            return
        
        try:
            FastAPIInstrumentor.instrument_app(app)
            logger.info("FastAPI instrumentation enabled")
        except Exception as e:
            logger.warning(f"Failed to instrument FastAPI app: {e}")
    
    def instrument_libraries(self):
        """
        Instrument common libraries
        
        Automatically traces:
        - HTTP requests (requests, httpx)
        - Database queries (asyncpg)
        - Redis operations
        """
        
        if not self.enabled:
            return
        
        try:
            # HTTP clients
            try:
                from opentelemetry.instrumentation.requests import RequestsInstrumentor
                RequestsInstrumentor().instrument()
            except ImportError:
                pass
            
            try:
                from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
                HTTPXClientInstrumentor().instrument()
            except ImportError:
                pass
            
            # Database
            try:
                from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
                AsyncPGInstrumentor().instrument()
            except ImportError:
                pass
            
            # Redis
            try:
                from opentelemetry.instrumentation.redis import RedisInstrumentor
                RedisInstrumentor().instrument()
            except ImportError:
                pass
            
            logger.info("Library instrumentation enabled")
        except Exception as e:
            logger.warning(f"Failed to instrument libraries: {e}")
    
    def trace_function(
        self,
        span_name: str = None,
        attributes: Dict[str, Any] = None
    ):
        """
        Decorator to automatically trace function execution
        
        Usage:
            @tracing_service.trace_function(span_name="my_function")
            async def my_function():
                ...
        """
        
        if not self.enabled:
            # Return no-op decorator
            def noop_decorator(func):
                return func
            return noop_decorator
        
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Use function name if span_name not provided
                name = span_name or f"{func.__module__}.{func.__name__}"
                
                with self.tracer.start_as_current_span(name) as span:
                    # Add custom attributes
                    if attributes:
                        for key, value in attributes.items():
                            span.set_attribute(key, value)
                    
                    # Add function metadata
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    
                    try:
                        result = await func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    
                    except Exception as e:
                        # Record exception in span
                        span.set_status(
                            Status(StatusCode.ERROR, str(e))
                        )
                        span.record_exception(e)
                        raise
            
            def sync_wrapper(*args, **kwargs):
                name = span_name or f"{func.__module__}.{func.__name__}"
                
                with self.tracer.start_as_current_span(name) as span:
                    if attributes:
                        for key, value in attributes.items():
                            span.set_attribute(key, value)
                    
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    
                    try:
                        result = func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    
                    except Exception as e:
                        span.set_status(
                            Status(StatusCode.ERROR, str(e))
                        )
                        span.record_exception(e)
                        raise
            
            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        """
        Add event to current span
        
        Args:
            name: Event name
            attributes: Event attributes
        """
        
        if not self.enabled:
            return
        
        current_span = trace.get_current_span()
        if current_span:
            current_span.add_event(name, attributes=attributes or {})
    
    def set_attribute(self, key: str, value: Any):
        """
        Set attribute on current span
        
        Args:
            key: Attribute key
            value: Attribute value
        """
        
        if not self.enabled:
            return
        
        current_span = trace.get_current_span()
        if current_span:
            current_span.set_attribute(key, value)
    
    def record_exception(self, exception: Exception):
        """
        Record exception in current span
        
        Args:
            exception: Exception to record
        """
        
        if not self.enabled:
            return
        
        current_span = trace.get_current_span()
        if current_span:
            current_span.record_exception(exception)
            current_span.set_status(
                Status(StatusCode.ERROR, str(exception))
            )
    
    def start_span(self, name: str, attributes: Dict[str, Any] = None):
        """
        Start a new span
        
        Args:
            name: Span name
            attributes: Optional span attributes
        
        Returns:
            Span context manager
        """
        
        if not self.enabled:
            # Return a no-op context manager
            from contextlib import nullcontext
            return nullcontext()
        
        span = self.tracer.start_as_current_span(name)
        
        # Set attributes if provided
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        
        return span


# Global tracing service instance
_tracing_service: Optional[TracingService] = None

def init_tracing(
    service_name: str = "amas-backend",
    service_version: str = "1.0.0",
    environment: str = None,
    jaeger_endpoint: str = None,
    otlp_endpoint: str = None
) -> TracingService:
    """Initialize global tracing service"""
    
    global _tracing_service
    
    if _tracing_service is not None:
        logger.warning("Tracing already initialized")
        return _tracing_service
    
    # Get environment from env var if not provided
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "production")
    
    _tracing_service = TracingService(
        service_name=service_name,
        service_version=service_version,
        environment=environment,
        jaeger_endpoint=jaeger_endpoint,
        otlp_endpoint=otlp_endpoint
    )
    
    # Instrument common libraries
    _tracing_service.instrument_libraries()
    
    return _tracing_service

def get_tracing_service() -> Optional[TracingService]:
    """Get global tracing service"""
    
    if _tracing_service is None:
        logger.warning("Tracing not initialized - returning None")
        return None
    
    return _tracing_service

