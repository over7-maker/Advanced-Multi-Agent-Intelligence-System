"""
AMAS Observability Framework

Provides comprehensive observability with:
- Distributed tracing via OpenTelemetry
- SLO monitoring with error budget tracking
- Performance metrics and regression detection
- Automated alerting
"""

from .tracing.tracer import (
    AmasTracer,
    PerformanceMonitor,
    initialize_observability,
    get_tracer,
    get_performance_monitor,
    trace_agent_operation,
    trace_tool_call,
    get_observability_health
)

from .slo_manager import (
    SLOManager,
    SLODefinition,
    SLOStatus,
    initialize_slo_manager,
    get_slo_manager
)

__all__ = [
    # Tracer
    "AmasTracer",
    "PerformanceMonitor",
    "initialize_observability",
    "get_tracer",
    "get_performance_monitor",
    "trace_agent_operation",
    "trace_tool_call",
    "get_observability_health",
    # SLO Manager
    "SLOManager",
    "SLODefinition",
    "SLOStatus",
    "initialize_slo_manager",
    "get_slo_manager",
]
