# AMAS Observability API Documentation

Complete API reference for the AMAS Observability & SLO Framework endpoints.

## Base URL

All endpoints are relative to the AMAS API base URL (default: `http://localhost:8000`).

---

## Health Endpoint

### `GET /health`

Includes observability health status in the overall health check response.

**Response Example:**

```json
{
  "status": "healthy",
  "checks": {
    "observability": {
      "tracer": "active",
      "slo_manager": "active",
      "prometheus": "connected",
      "otlp_endpoint": "http://localhost:4317"
    }
  }
}
```

**Status Codes:**
- `200 OK`: System is healthy
- `503 Service Unavailable`: One or more components are unhealthy

---

## SLO Status Endpoint

### `GET /observability/slo/status`

Get current SLO status for all configured Service Level Objectives.

**Response Example:**

```json
{
  "slos": [
    {
      "slo_name": "agent_availability",
      "current_value": 99.7,
      "threshold": 99.5,
      "comparison": ">=",
      "status": "compliant",
      "error_budget_remaining_percent": 0.4,
      "error_budget_total_percent": 0.5,
      "last_evaluated": "2025-01-15T10:30:00Z"
    },
    {
      "slo_name": "agent_latency_p95",
      "current_value": 1.2,
      "threshold": 1.5,
      "comparison": "<=",
      "status": "compliant",
      "error_budget_remaining_percent": 8.5,
      "error_budget_total_percent": 10.0,
      "last_evaluated": "2025-01-15T10:30:00Z"
    }
  ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `slo_name` | string | Name of the SLO |
| `current_value` | number | Current metric value |
| `threshold` | number | SLO threshold value |
| `comparison` | string | Comparison operator (`>=`, `<=`, `==`) |
| `status` | string | Status: `compliant`, `violated`, `unknown` |
| `error_budget_remaining_percent` | number | Remaining error budget percentage |
| `error_budget_total_percent` | number | Total error budget percentage |
| `last_evaluated` | string | ISO 8601 timestamp of last evaluation |

**Status Codes:**
- `200 OK`: Successfully retrieved SLO statuses
- `500 Internal Server Error`: Error evaluating SLOs

---

## SLO Violations Endpoint

### `GET /observability/slo/violations`

Get current SLO violations, optionally filtered by severity.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `severity` | string | No | Filter by severity: `critical`, `high`, `warning` |

**Response Example:**

```json
{
  "violations": [
    {
      "slo_name": "agent_availability",
      "severity": "critical",
      "current_value": 98.5,
      "threshold": 99.5,
      "comparison": ">=",
      "error_budget_remaining_percent": 0.1,
      "violated_at": "2025-01-15T10:25:00Z",
      "duration_seconds": 300
    }
  ],
  "total_violations": 1,
  "critical_violations": 1,
  "high_violations": 0,
  "warning_violations": 0
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `slo_name` | string | Name of the violated SLO |
| `severity` | string | Severity level: `critical`, `high`, `warning` |
| `current_value` | number | Current metric value |
| `threshold` | number | SLO threshold |
| `comparison` | string | Comparison operator |
| `error_budget_remaining_percent` | number | Remaining error budget |
| `violated_at` | string | ISO 8601 timestamp when violation started |
| `duration_seconds` | number | Duration of violation in seconds |
| `total_violations` | number | Total number of violations |
| `critical_violations` | number | Number of critical violations |
| `high_violations` | number | Number of high severity violations |
| `warning_violations` | number | Number of warning violations |

**Status Codes:**
- `200 OK`: Successfully retrieved violations
- `500 Internal Server Error`: Error retrieving violations

**Example Requests:**

```bash
# Get all violations
curl http://localhost:8000/observability/slo/violations

# Get only critical violations
curl http://localhost:8000/observability/slo/violations?severity=critical

# Get high and critical violations (using Prometheus query)
curl "http://localhost:8000/observability/slo/violations?severity=high"
```

---

## Prometheus Metrics Endpoint

### `GET /metrics`

Exposes Prometheus-formatted metrics for scraping.

**Response Format:**

Prometheus text format (text/plain)

**Example Response:**

```
# HELP amas_agent_requests_total Total number of agent requests
# TYPE amas_agent_requests_total counter
amas_agent_requests_total{agent_id="research_agent",operation="analyze",status="success"} 1250
amas_agent_requests_total{agent_id="research_agent",operation="analyze",status="error"} 5

# HELP amas_agent_duration_seconds Agent operation duration in seconds
# TYPE amas_agent_duration_seconds histogram
amas_agent_duration_seconds_bucket{agent_id="research_agent",operation="analyze",le="0.5"} 800
amas_agent_duration_seconds_bucket{agent_id="research_agent",operation="analyze",le="1.0"} 1100
amas_agent_duration_seconds_bucket{agent_id="research_agent",operation="analyze",le="1.5"} 1240
amas_agent_duration_seconds_bucket{agent_id="research_agent",operation="analyze",le="+Inf"} 1255
amas_agent_duration_seconds_sum{agent_id="research_agent",operation="analyze"} 1250.5
amas_agent_duration_seconds_count{agent_id="research_agent",operation="analyze"} 1255

# HELP amas_slo_error_budget_remaining_percent Remaining error budget percentage
# TYPE amas_slo_error_budget_remaining_percent gauge
amas_slo_error_budget_remaining_percent{slo_name="agent_availability"} 0.4
amas_slo_error_budget_remaining_percent{slo_name="agent_latency_p95"} 8.5
```

**Key Metrics Exposed:**

| Metric Name | Type | Description |
|-------------|------|-------------|
| `amas_agent_requests_total` | Counter | Total requests by agent/operation/status |
| `amas_agent_errors_total` | Counter | Error counts by type |
| `amas_agent_duration_seconds` | Histogram | Response time distribution (P50, P95, P99) |
| `amas_active_agents_current` | Gauge | Currently active agents |
| `amas_queue_depth_current` | Gauge | Current queue depth |
| `amas_tokens_used_total` | Counter | Total token usage |
| `amas_cost_usd_total` | Counter | Total cost in USD |
| `amas_slo_compliance` | Gauge | SLO compliance status (0/1) |
| `amas_slo_error_budget_remaining_percent` | Gauge | Error budget remaining percentage |
| `amas_slo_error_budget_burn_rate` | Gauge | Error budget burn rate |
| `amas_slo_violations_total` | Counter | Total SLO violations |

**Status Codes:**
- `200 OK`: Metrics successfully retrieved

**Configuration:**

Configure Prometheus to scrape this endpoint:

```yaml
scrape_configs:
  - job_name: 'amas-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

---

## Error Responses

All endpoints may return the following error responses:

### `500 Internal Server Error`

```json
{
  "error": "Internal server error",
  "message": "Failed to evaluate SLOs: Connection refused",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### `503 Service Unavailable`

```json
{
  "error": "Service unavailable",
  "message": "Observability system not initialized",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

## Authentication

Currently, observability endpoints do not require authentication. For production deployments, consider:

1. **API Key Authentication**: Add API key validation middleware
2. **JWT Tokens**: Use existing JWT authentication
3. **Network Isolation**: Restrict access via firewall rules
4. **Rate Limiting**: Implement rate limiting for metrics endpoint

---

## Rate Limiting

The `/metrics` endpoint may be scraped frequently by Prometheus. Consider:

- **Scrape Interval**: Configure Prometheus to scrape every 15-30 seconds
- **Rate Limiting**: Implement rate limiting if needed
- **Caching**: Metrics are generated on-demand, no caching needed

---

## Examples

### Check SLO Status

```bash
# Get all SLO statuses
curl http://localhost:8000/observability/slo/status | jq

# Check specific SLO
curl http://localhost:8000/observability/slo/status | \
  jq '.slos[] | select(.slo_name == "agent_availability")'
```

### Monitor Violations

```bash
# Watch for violations (using watch command)
watch -n 5 'curl -s http://localhost:8000/observability/slo/violations | jq'

# Alert on critical violations
CRITICAL=$(curl -s http://localhost:8000/observability/slo/violations?severity=critical | \
  jq '.critical_violations')
if [ "$CRITICAL" -gt 0 ]; then
  echo "ALERT: $CRITICAL critical SLO violations detected!"
fi
```

### Scrape Metrics

```bash
# Manual metrics scrape
curl http://localhost:8000/metrics

# Save to file for analysis
curl http://localhost:8000/metrics > metrics.txt

# Query specific metric (requires Prometheus)
curl 'http://localhost:9090/api/v1/query?query=amas_agent_requests_total'
```

---

## Integration Examples

### Python Client

```python
import requests

BASE_URL = "http://localhost:8000"

def get_slo_status():
    """Get current SLO status"""
    response = requests.get(f"{BASE_URL}/observability/slo/status")
    response.raise_for_status()
    return response.json()

def get_violations(severity=None):
    """Get SLO violations"""
    params = {"severity": severity} if severity else {}
    response = requests.get(
        f"{BASE_URL}/observability/slo/violations",
        params=params
    )
    response.raise_for_status()
    return response.json()

# Usage
status = get_slo_status()
for slo in status["slos"]:
    print(f"{slo['slo_name']}: {slo['status']}")

violations = get_violations(severity="critical")
if violations["critical_violations"] > 0:
    print(f"ALERT: {violations['critical_violations']} critical violations!")
```

### Shell Script Monitoring

```bash
#!/bin/bash

API_URL="http://localhost:8000"
ALERT_THRESHOLD=0.1  # Alert if error budget < 10%

# Check SLO status
STATUS=$(curl -s "${API_URL}/observability/slo/status")

# Check for critical violations
CRITICAL=$(curl -s "${API_URL}/observability/slo/violations?severity=critical" | \
  jq -r '.critical_violations')

if [ "$CRITICAL" -gt 0 ]; then
  echo "CRITICAL: $CRITICAL SLO violations detected!"
  exit 1
fi

# Check error budgets
echo "$STATUS" | jq -r '.slos[] | 
  select(.error_budget_remaining_percent < '"$ALERT_THRESHOLD"') | 
  "WARNING: \(.slo_name) error budget at \(.error_budget_remaining_percent)%"'
```

---

## Related Documentation

- [Observability Framework Guide](../OBSERVABILITY_FRAMEWORK.md)
- [Observability Setup Guide](../OBSERVABILITY_SETUP_GUIDE.md)
- [Monitoring Guide](../MONITORING_GUIDE.md)
- [Prometheus Query Documentation](https://prometheus.io/docs/prometheus/latest/querying/basics/)
