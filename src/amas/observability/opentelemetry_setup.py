"""
OpenTelemetry Setup for AMAS
Provides structured telemetry (traces, metrics, logs) across services
"""

import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

logger = logging.getLogger(__name__)


def setup_opentelemetry(
    service_name: str = "amas",
    otlp_endpoint: Optional[str] = None,
    enable_console: bool = False,
) -> None:
    """Setup OpenTelemetry tracing and metrics"""

    # Create resource with service metadata
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": "3.0.0",
            "deployment.environment": "production",
        }
    )

    # Setup trace provider
    trace_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(trace_provider)

    # Add exporters
    if otlp_endpoint:
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
        trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        logger.info(f"OTLP exporter configured for {otlp_endpoint}")

    if enable_console:
        console_exporter = ConsoleSpanExporter()
        trace_provider.add_span_processor(BatchSpanProcessor(console_exporter))
        logger.info("Console exporter enabled")

    # Auto-instrument common libraries
    try:
        FastAPIInstrumentor().instrument()
        HTTPXClientInstrumentor().instrument()
        RedisInstrumentor().instrument()
        SQLAlchemyInstrumentor().instrument()
        logger.info("OpenTelemetry auto-instrumentation enabled")
    except Exception as e:
        logger.warning(f"Failed to enable some instrumentation: {e}")

    logger.info("OpenTelemetry setup complete")


def get_tracer(name: str):
    """Get tracer instance for custom spans"""
    return trace.get_tracer(name)


def propagate_trace_context(headers: dict) -> dict:
    """Propagate trace context in headers for distributed tracing"""
    from opentelemetry.propagate import inject

    context_headers = {}
    inject(context_headers)
    return {**headers, **context_headers}


# Context manager for custom spans
class TraceContext:
    """Context manager for creating custom trace spans"""

    def __init__(self, name: str, tracer_name: str = "amas"):
        self.name = name
        self.tracer = get_tracer(tracer_name)
        self.span = None

    def __enter__(self):
        self.span = self.tracer.start_span(self.name)
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            if exc_type:
                self.span.set_status(
                    trace.Status(
                        trace.StatusCode.ERROR, f"{exc_type.__name__}: {exc_val}"
                    )
                )
            self.span.end()


# Decorator for tracing functions
def traced(func):
    """Decorator to automatically trace function execution"""
    from functools import wraps

    tracer = get_tracer(func.__module__)

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        with tracer.start_as_current_span(func.__name__) as span:
            try:
                result = await func(*args, **kwargs)
                span.set_status(trace.Status(trace.StatusCode.OK))
                return result
            except Exception as e:
                span.set_status(
                    trace.Status(trace.StatusCode.ERROR, str(e))
                )
                span.record_exception(e)
                raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        with tracer.start_as_current_span(func.__name__) as span:
            try:
                result = func(*args, **kwargs)
                span.set_status(trace.Status(trace.StatusCode.OK))
                return result
            except Exception as e:
                span.set_status(
                    trace.Status(trace.StatusCode.ERROR, str(e))
                )
                span.record_exception(e)
                raise

    import asyncio

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
