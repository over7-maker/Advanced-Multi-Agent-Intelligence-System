from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_tracing(
    service_name: str = "amas", jaeger_host: str = "jaeger", jaeger_port: int = 6831
) -> None:
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    jaeger_exporter = JaegerExporter(
        agent_host_name=jaeger_host, agent_port=jaeger_port
    )
    span_processor = BatchSpanProcessor(jaeger_exporter)
    provider.add_span_processor(span_processor)


def instrument_fastapi(app) -> None:
    FastAPIInstrumentor.instrument_app(app)


def instrument_sqlalchemy() -> None:
    SQLAlchemyInstrumentor().instrument()


def instrument_redis() -> None:
    RedisInstrumentor().instrument()
