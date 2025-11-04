# AMAS Observability & SLO Framework

## Overview

The AMAS Observability Framework provides comprehensive system visibility with distributed tracing, Service Level Objective (SLO) monitoring, error budget tracking, and automated alerting. This transforms AMAS from a "black box" into a fully observable system with proactive reliability monitoring.

## Features

✅ **OpenTelemetry Integration**: Distributed tracing and metrics for all agent operations  
✅ **SLO Monitoring**: Service Level Objectives with automatic error budget tracking  
✅ **Grafana Dashboards**: Real-time performance and reliability monitoring  
✅ **Automated Alerting**: Smart alerts when SLOs are violated or error budgets depleted  
✅ **Performance Regression Detection**: Automatic detection of performance degradations  

## Architecture

### Components

1. **AmasTracer** (`src/amas/observability/tracing/tracer.py`)
   - OpenTelemetry integration with OTLP export
   - Automatic instrumentation for FastAPI, HTTPX, and logging
   - Agent operation and tool call tracing
   - Metrics collection (request rates, latencies, errors, token usage, costs)

2. **SLOManager** (`src/amas/observability/slo_manager.py`)
   - Prometheus-based SLO evaluation
   - Error budget calculation and tracking
   - Multi-window burn rate detection
   - Performance baseline establishment

3. **SLOEvaluator** (`src/amas/observability/slo_evaluator.py`)
   - Background task for periodic SLO evaluation
   - Automatic violation detection and alerting

4. **Configuration Files**
   - `config/observability/slo_definitions.yaml`: SLO targets and alert rules
   - `config/observability/prometheus_alerts.yaml`: Prometheus alert rules
   - `config/observability/grafana_dashboards.json`: Grafana dashboard definitions

## SLO Targets

The following SLOs are pre-configured:

| SLO Name | Target | Error Budget | Description |
|----------|--------|--------------|-------------|
| `agent_availability` | ≥99.5% | 0.5% | Agent request success rate |
| `agent_latency_p95` | ≤1.5s | 10% | 95th percentile response time |
| `tool_call_success_rate` | ≥99.0% | 1% | Tool call success rate |
| `memory_usage` | ≤80% | 15% | Memory utilization |
| `cost_efficiency` | ≤$0.05/req | 20% | Cost per request |
| `queue_depth` | ≤50 | 25% | Processing queue depth |

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The observability framework requires:
- `opentelemetry-api==1.27.0`
- `opentelemetry-sdk==1.27.0`
- `opentelemetry-exporter-otlp-proto-grpc==1.27.0`
- `opentelemetry-instrumentation-fastapi==0.49b0`
- `opentelemetry-instrumentation-httpx==0.49b0`
- `prometheus-client==0.21.0`

### 2. Configure Environment Variables

```bash
export OTLP_ENDPOINT="http://localhost:4317"  # OpenTelemetry Collector endpoint
export PROMETHEUS_URL="http://localhost:9090"   # Prometheus query API
export ENVIRONMENT="production"                # Environment name
export SLO_CONFIG_PATH="config/observability/slo_definitions.yaml"  # Optional
```

### 3. Deploy Monitoring Stack

The observability framework integrates with:
- **OpenTelemetry Collector**: Centralized telemetry data collection
- **Prometheus**: Metrics storage and querying
- **Grafana**: Visualization and dashboards
- **Jaeger**: Distributed tracing analysis
- **Alert Manager**: Notification routing

#### Using Docker Compose

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./config/observability/prometheus_alerts.yaml:/etc/prometheus/alerts.yaml
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./config/observability/grafana_dashboards.json:/etc/grafana/provisioning/dashboards/dashboards.json
  
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # UI
      - "4317:4317"    # OTLP gRPC
  
  otel-collector:
    image: otel/opentelemetry-collector:latest
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317"  # OTLP gRPC receiver
```

### 4. Import Grafana Dashboards

1. Navigate to Grafana (http://localhost:3000)
2. Go to Dashboards → Import
3. Upload `config/observability/grafana_dashboards.json`
4. Configure Prometheus data source

## Usage

### Tracing Agent Operations

```python
from src.amas.observability import get_tracer

tracer = get_tracer()

async with tracer.trace_agent_execution(
    agent_id="my_agent",
    operation="process_request",
    user_id="user123"
):
    # Your agent code here
    result = await agent.process(request)
```

### Tracing Tool Calls

```python
async with tracer.trace_tool_call(
    agent_id="my_agent",
    tool_name="search_database",
    parameters={"query": "example"}
):
    result = await tool.execute(query)
```

### Using Decorators

```python
from src.amas.observability.tracing.tracer import trace_agent_operation

@trace_agent_operation("my_operation")
async def my_agent_function():
    # Function automatically traced
    pass
```

### Recording Metrics

```python
tracer = get_tracer()

# Record token usage
tracer.record_token_usage(
    agent_id="my_agent",
    tokens_used=1000,
    cost_usd=0.01,
    model_name="gpt-4"
)

# Record queue depth
tracer.record_queue_metrics("task_queue", depth=25)
```

### SLO Monitoring

```python
from src.amas.observability import get_slo_manager

slo_manager = get_slo_manager()

# Get SLO status
status = slo_manager.get_slo_status("agent_availability")
print(f"Error budget remaining: {status.error_budget_remaining_percent}%")

# Get violations
violations = slo_manager.get_violations()
for violation in violations:
    print(f"SLO {violation.slo_name} is {violation.status}")
```

### API Endpoints

The framework exposes the following API endpoints:

- `GET /health` - Includes observability health status
- `GET /observability/slo/status` - Get all SLO statuses
- `GET /observability/slo/violations?severity=critical` - Get SLO violations
- `GET /metrics` - Prometheus metrics endpoint

## Testing

Run the observability tests:

```bash
pytest tests/test_observability.py -v
```

## Alert Configuration

Alerts are configured in `config/observability/prometheus_alerts.yaml`:

- **Critical**: Error budget < 5% remaining
- **High**: Error budget < 15% remaining
- **Warning**: Error budget < 25% remaining

### Burn Rate Alerts

- **Fast Burn**: 2% of error budget consumed in 1 hour
- **Slow Burn**: 5% of error budget consumed in 6 hours

### Notification Channels

Configured in `slo_definitions.yaml`:
- Slack (critical, alerts, warnings)
- PagerDuty (critical alerts)
- Email (oncall, team)

## Performance Regression Detection

The framework automatically detects performance regressions:

```python
from src.amas.observability import get_performance_monitor

monitor = get_performance_monitor()

regression = await monitor.check_performance_regression(
    operation="agent_execution",
    duration_seconds=3.0,
    success=True
)

if regression:
    print(f"Regression detected: {regression['type']}")
```

## Metrics Exposed

### Request Metrics
- `amas_agent_requests_total`: Total requests by agent/operation/status
- `amas_agent_errors_total`: Error counts by type
- `amas_agent_duration_seconds`: Response time histogram (P50, P95, P99)

### Resource Metrics
- `amas_active_agents_current`: Currently active agents
- `amas_queue_depth_current`: Queue depth
- `amas_tokens_used_total`: Token usage
- `amas_cost_usd_total`: Cost tracking

### SLO Metrics
- `amas_slo_compliance`: SLO compliance status (0/1)
- `amas_slo_error_budget_remaining_percent`: Error budget remaining
- `amas_slo_error_budget_burn_rate`: Burn rate
- `amas_slo_violations_total`: Violation counter

## Troubleshooting

### Traces Not Appearing in Jaeger

1. Check OTLP endpoint: `echo $OTLP_ENDPOINT`
2. Verify OpenTelemetry Collector is running
3. Check collector logs for errors

### SLO Evaluations Failing

1. Verify Prometheus is accessible: `curl http://localhost:9090/api/v1/status/config`
2. Check SLO queries in Prometheus UI
3. Review SLO manager logs

### Metrics Not Updating

1. Verify metrics endpoint: `curl http://localhost:8000/metrics`
2. Check Prometheus scraping configuration
3. Ensure metrics are being recorded in code

## Next Steps

After deployment:

1. **Validate SLOs**: Ensure all SLO queries return expected data
2. **Test Alerting**: Trigger test violations to validate alert delivery
3. **Configure Notifications**: Set up Slack/PagerDuty webhook integrations
4. **Review Dashboards**: Customize Grafana dashboards for your needs
5. **Establish Baselines**: Let the system run to establish performance baselines

## Success Criteria

✅ Simulate agent failure → Alert fires within 2 minutes  
✅ Check dashboard → Shows real-time performance metrics  
✅ Trace a slow request → See exactly where time was spent  
✅ SLO violation → Error budget automatically decrements  
✅ All traces end-to-end → Complete request visibility  

## References

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Prometheus SLO Best Practices](https://sre.google/workbook/slo-document/)
- [Grafana Dashboard Documentation](https://grafana.com/docs/grafana/latest/dashboards/)
