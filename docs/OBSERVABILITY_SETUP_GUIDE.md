# 🚀 AMAS Observability Setup Guide

Complete step-by-step guide to set up the AMAS Observability & SLO Framework in your environment.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Monitoring Stack Deployment](#monitoring-stack-deployment)
5. [Grafana Dashboard Setup](#grafana-dashboard-setup)
6. [Verification](#verification)
7. [Production Considerations](#production-considerations)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Python**: 3.8+ (3.11+ recommended)
- **Docker & Docker Compose**: For monitoring stack deployment
- **Network Access**: To OpenTelemetry Collector, Prometheus, and Grafana endpoints
- **Disk Space**: ~2GB for monitoring stack containers

### Required Accounts (Optional)

- **Slack**: For alert notifications
- **PagerDuty**: For critical alert escalation
- **Email**: For team notifications

---

## Installation

### Step 1: Install Python Dependencies

```bash
# Install all dependencies including observability packages
pip install -r requirements.txt
```

Key observability packages installed:
- `opentelemetry-api==1.27.0`
- `opentelemetry-sdk==1.27.0`
- `opentelemetry-exporter-otlp-proto-grpc==1.27.0`
- `opentelemetry-instrumentation-fastapi==0.49b0`
- `opentelemetry-instrumentation-httpx==0.49b0`
- `opentelemetry-instrumentation-sqlalchemy==0.49b0` (optional)
- `opentelemetry-instrumentation-psycopg2==0.49b0` (optional)
- `prometheus-client==0.21.0`

### Step 2: Verify Installation

```bash
python -c "from src.amas.observability import get_tracer; print('Observability installed successfully')"
```

---

## Configuration

### Step 1: Environment Variables

Create or update your `.env` file with the following variables:

```bash
# OpenTelemetry Configuration
OTLP_ENDPOINT=http://localhost:4317  # OpenTelemetry Collector gRPC endpoint
ENVIRONMENT=development              # Environment name (development/staging/production)

# Prometheus Configuration
PROMETHEUS_URL=http://localhost:9090  # Prometheus query API endpoint

# SLO Configuration (Optional)
SLO_CONFIG_PATH=config/observability/slo_definitions.yaml
```

### Step 2: Production Environment Variables

For production deployments:

```bash
# Production OTLP endpoint (example with authentication)
OTLP_ENDPOINT=https://otel-collector.your-domain.com:4317

# Production Prometheus
PROMETHEUS_URL=https://prometheus.your-domain.com:9090

# Production environment
ENVIRONMENT=production
```

### Step 3: Verify Configuration Files

Ensure these configuration files exist:

```bash
# Check SLO definitions
ls -la config/observability/slo_definitions.yaml

# Check Prometheus alerts
ls -la config/observability/prometheus_alerts.yaml

# Check Grafana dashboards
ls -la config/observability/grafana_dashboards.json
```

---

## Monitoring Stack Deployment

### Option 1: Docker Compose (Recommended for Development)

Create `docker-compose.observability.yml`:

```yaml
version: '3.8'

services:
  # OpenTelemetry Collector
  otel-collector:
    image: otel/opentelemetry-collector:latest
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./config/observability/otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317"  # OTLP gRPC receiver
      - "4318:4318"  # OTLP HTTP receiver
    networks:
      - observability

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./config/observability/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./config/observability/prometheus_alerts.yaml:/etc/prometheus/alerts.yaml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    networks:
      - observability

  # Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=
      - GF_SERVER_ROOT_URL=http://localhost:3000
    volumes:
      - grafana-data:/var/lib/grafana
      - ./config/observability/grafana/provisioning:/etc/grafana/provisioning
    networks:
      - observability
    depends_on:
      - prometheus

  # Jaeger (for distributed tracing)
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # UI
      - "4317:4317"    # OTLP gRPC (if not using separate collector)
      - "4318:4318"    # OTLP HTTP
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    networks:
      - observability

volumes:
  prometheus-data:
  grafana-data:

networks:
  observability:
    driver: bridge
```

### Step 2: Create Prometheus Configuration

Create `config/observability/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'amas'
    environment: 'development'

rule_files:
  - "/etc/prometheus/alerts.yaml"

scrape_configs:
  - job_name: 'amas-api'
    static_configs:
      - targets: ['host.docker.internal:8000']  # Adjust to your AMAS API host
        labels:
          service: 'amas-orchestrator'
          environment: 'development'

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

### Step 3: Create OpenTelemetry Collector Configuration

Create `config/observability/otel-collector-config.yaml`:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024
  memory_limiter:
    limit_mib: 512

exporters:
  # Export to Jaeger
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true
  
  # Export to Prometheus
  prometheus:
    endpoint: "0.0.0.0:8889"
  
  # Optional: Export to logging for debugging
  logging:
    loglevel: info

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [jaeger, logging]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheus, logging]
```

### Step 4: Start Monitoring Stack

```bash
# Start all services
docker-compose -f docker-compose.observability.yml up -d

# Check service status
docker-compose -f docker-compose.observability.yml ps

# View logs
docker-compose -f docker-compose.observability.yml logs -f
```

### Step 5: Verify Services

```bash
# Check OpenTelemetry Collector
curl http://localhost:4318/metrics

# Check Prometheus
curl http://localhost:9090/api/v1/status/config

# Check Grafana
curl http://localhost:3000/api/health

# Check Jaeger
curl http://localhost:16686/api/services
```

---

## Grafana Dashboard Setup

### Step 1: Configure Prometheus Data Source

1. Navigate to Grafana: http://localhost:3000
2. Login with `admin` / `admin` (change password on first login)
3. Go to **Configuration** → **Data Sources** → **Add data source**
4. Select **Prometheus**
5. Set URL: `http://prometheus:9090` (or `http://localhost:9090` if running locally)
6. Click **Save & Test**

### Step 2: Import Dashboards

#### Option A: Via Grafana UI

1. Go to **Dashboards** → **Import**
2. Click **Upload JSON file**
3. Select `config/observability/grafana_dashboards.json`
4. Select Prometheus data source
5. Click **Import**

#### Option B: Via Provisioning (Recommended)

Create `config/observability/grafana/provisioning/dashboards/dashboards.yml`:

```yaml
apiVersion: 1

providers:
  - name: 'AMAS Observability'
    orgId: 1
    folder: 'AMAS'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
      foldersFromFilesStructure: true
```

Create `config/observability/grafana/provisioning/datasources/prometheus.yml`:

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
```

Restart Grafana:

```bash
docker-compose -f docker-compose.observability.yml restart grafana
```

### Step 3: Verify Dashboards

You should see three dashboards:

1. **Agent Performance Dashboard** (`uid: amas-agent-performance`)
   - Request rates, latencies, error rates
   - Agent-specific metrics

2. **SLO Monitoring Dashboard** (`uid: amas-slo-monitoring`)
   - SLO compliance status
   - Error budget tracking
   - Violation history

3. **Resource Utilization Dashboard** (`uid: amas-resource-utilization`)
   - Memory, CPU usage
   - Queue depth
   - Token usage and costs

---

## Verification

### Step 1: Start AMAS Application

```bash
# Start AMAS with observability enabled
python -m src.amas.api.main

# Or using the startup script
./start-amas-interactive.sh
```

### Step 2: Generate Test Traffic

```bash
# Make some API requests
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/agents

# Check metrics endpoint
curl http://localhost:8000/metrics
```

### Step 3: Verify Traces in Jaeger

1. Open Jaeger UI: http://localhost:16686
2. Select service: `amas-orchestrator`
3. Click **Find Traces**
4. You should see traces from your requests

### Step 4: Verify Metrics in Prometheus

1. Open Prometheus: http://localhost:9090
2. Go to **Graph**
3. Try queries:
   - `amas_agent_requests_total`
   - `rate(amas_agent_requests_total[5m])`
   - `histogram_quantile(0.95, rate(amas_agent_duration_seconds_bucket[5m]))`

### Step 5: Verify SLO Evaluation

```bash
# Check SLO status via API
curl http://localhost:8000/observability/slo/status

# Check for violations
curl http://localhost:8000/observability/slo/violations
```

### Step 6: Verify Dashboards

1. Open Grafana: http://localhost:3000
2. Navigate to **Dashboards** → **AMAS**
3. Open each dashboard and verify data is appearing

---

## Production Considerations

### Security

1. **Authentication**: Enable authentication for all monitoring services
2. **TLS**: Use TLS for all OTLP and Prometheus connections
3. **Network Isolation**: Place monitoring stack in isolated network
4. **Access Control**: Restrict Grafana dashboard access

### Performance

1. **Resource Limits**: Set appropriate CPU/memory limits for containers
2. **Retention**: Configure Prometheus retention based on disk space
3. **Sampling**: Consider trace sampling for high-traffic environments
4. **Scraping Interval**: Adjust Prometheus scrape interval based on needs

### High Availability

1. **Prometheus**: Run multiple Prometheus instances with federation
2. **Grafana**: Use Grafana HA setup or load balancer
3. **Jaeger**: Use Jaeger production deployment (not all-in-one)
4. **Backup**: Regular backups of Prometheus and Grafana data

### Scaling

1. **Horizontal Scaling**: Scale AMAS instances, metrics aggregate automatically
2. **Vertical Scaling**: Increase Prometheus storage for longer retention
3. **Federation**: Use Prometheus federation for multi-cluster setups

---

## Troubleshooting

### Traces Not Appearing

**Problem**: No traces visible in Jaeger

**Solutions**:
1. Check OTLP endpoint: `echo $OTLP_ENDPOINT`
2. Verify collector is running: `docker ps | grep otel-collector`
3. Check collector logs: `docker logs otel-collector`
4. Verify network connectivity between AMAS and collector

### Metrics Not Scraped

**Problem**: Prometheus not collecting metrics

**Solutions**:
1. Verify metrics endpoint: `curl http://localhost:8000/metrics`
2. Check Prometheus targets: http://localhost:9090/targets
3. Verify scrape configuration in `prometheus.yml`
4. Check Prometheus logs: `docker logs prometheus`

### SLO Evaluations Failing

**Problem**: SLO status shows errors

**Solutions**:
1. Verify Prometheus URL: `echo $PROMETHEUS_URL`
2. Test Prometheus query manually in Prometheus UI
3. Check SLO queries in `slo_definitions.yaml` are valid
4. Review SLO manager logs for specific errors

### Dashboards Not Loading

**Problem**: Grafana dashboards show "No data"

**Solutions**:
1. Verify Prometheus data source is configured correctly
2. Check dashboard queries use correct metric names
3. Verify time range in dashboard (try "Last 6 hours")
4. Check if metrics are actually being generated

### High Resource Usage

**Problem**: Monitoring stack consuming too much resources

**Solutions**:
1. Reduce Prometheus retention period
2. Enable trace sampling in OpenTelemetry
3. Reduce scrape frequency
4. Use recording rules in Prometheus to pre-aggregate metrics

---

## Next Steps

After successful setup:

1. **Configure Alerting**: Set up Slack/PagerDuty webhooks in `slo_definitions.yaml`
2. **Customize Dashboards**: Adjust Grafana dashboards for your specific needs
3. **Establish Baselines**: Let system run to establish performance baselines
4. **Review SLO Targets**: Adjust SLO thresholds based on actual performance
5. **Document Runbooks**: Create runbooks for common alert scenarios

---

## Additional Resources

- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/instrumentation/python/)
- [Prometheus Query Documentation](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/best-practices/)
- [SRE Error Budget Guide](https://sre.google/workbook/slo-document/)

---

## Support

For issues or questions:
- Check [OBSERVABILITY_FRAMEWORK.md](./OBSERVABILITY_FRAMEWORK.md) for detailed framework documentation
- Review [MONITORING_GUIDE.md](./MONITORING_GUIDE.md) for monitoring best practices
- Open an issue on GitHub with `[observability]` tag
