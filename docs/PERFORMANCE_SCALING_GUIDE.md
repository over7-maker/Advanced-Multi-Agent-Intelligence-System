# Performance Scaling Infrastructure Guide

> **Version:** 1.0.0 | **Last Updated:** 2025-01-XX

This guide covers the comprehensive performance scaling infrastructure for AMAS, including KEDA-based autoscaling, load testing, and performance monitoring.

## Table of Contents

1. [Overview](#overview)
2. [KEDA Autoscaling](#keda-autoscaling)
3. [Load Testing Framework](#load-testing-framework)
4. [Performance Monitoring](#performance-monitoring)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Overview

The AMAS performance scaling infrastructure provides:

- **KEDA-based Autoscaling**: Intelligent pod scaling based on multiple metrics (CPU, memory, queue depth, latency)
- **Load Testing Framework**: Comprehensive load testing with SLO validation
- **Performance Monitoring**: Real-time metrics collection and analysis
- **Horizontal Pod Autoscaling (HPA)**: Kubernetes-native autoscaling as fallback
- **Vertical Pod Autoscaling (VPA)**: Automatic resource right-sizing

## KEDA Autoscaling

### Architecture

KEDA (Kubernetes Event-Driven Autoscaling) provides event-driven autoscaling for Kubernetes workloads. AMAS uses KEDA to scale based on:

1. **HTTP Request Rate**: Scale based on requests per second
2. **Queue Depth**: Scale based on agent job queue depth
3. **Latency**: Scale when p95 latency exceeds thresholds
4. **Resource Utilization**: Scale based on CPU/memory pressure

### Configuration

The KEDA scaler configuration is located at `k8s/scaling/keda-scaler.yaml`.

#### Orchestrator Scaling

```yaml
# Primary metrics for orchestrator scaling
- HTTP request rate > 15 RPS
- Agent queue depth > 25 items
- P95 latency > 1.0 seconds
- CPU > 70% or Memory > 80%
```

**Scaling Behavior:**
- **Min Replicas**: 2 (always available)
- **Max Replicas**: 50 (safety limit)
- **Polling Interval**: 15 seconds
- **Cooldown Period**: 180 seconds (3 minutes)

**Scale-Up Policy:**
- Stabilization: 60 seconds
- Max increase: 100% per minute OR 5 pods per minute
- Selects maximum (aggressive scaling)

**Scale-Down Policy:**
- Stabilization: 300 seconds (5 minutes)
- Max decrease: 10% per minute OR 2 pods per minute
- Selects minimum (conservative scaling)

#### Worker Scaling

Workers scale based on:
- Redis queue depth > 8 jobs
- Redis stream pending events > 5
- Average CPU utilization > 65%

**Configuration:**
- Min Replicas: 1
- Max Replicas: 20
- Polling Interval: 10 seconds
- Cooldown Period: 120 seconds

#### Research Agent Scaling

Research agents scale based on:
- Research request queue depth > 5
- Token usage rate > 1000 tokens/second

**Configuration:**
- Min Replicas: 1
- Max Replicas: 10
- Polling Interval: 20 seconds
- Cooldown Period: 300 seconds (longer for research tasks)

### Deployment

```bash
# Apply KEDA scaler configuration
kubectl apply -f k8s/scaling/keda-scaler.yaml

# Verify KEDA installation
kubectl get scaledobjects -n amas-prod

# Check scaling status
kubectl describe scaledobject amas-orchestrator-scaler -n amas-prod
```

### Monitoring KEDA Scaling

```bash
# Watch pod scaling in real-time
watch kubectl get pods -n amas-prod -l app=amas-orchestrator

# Check KEDA metrics
kubectl get metrics -n amas-prod

# View scaling events
kubectl get events -n amas-prod --sort-by='.lastTimestamp' | grep -i scale
```

## Load Testing Framework

### Overview

The load testing framework (`src/amas/performance/benchmarks/load_tester.py`) provides:

- **Realistic Traffic Patterns**: Constant, linear ramp, step function, spike tests
- **SLO Validation**: Automatic validation against success rate and latency thresholds
- **Performance Regression Detection**: Compare against historical baselines
- **Comprehensive Reporting**: JSON, CSV, and human-readable summaries
- **Prometheus Integration**: Real-time metrics during load tests

### Usage

#### Basic Load Test

```python
from src.amas.performance.benchmarks.load_tester import (
    AmasLoadTester,
    LoadTestConfig,
    LoadPattern
)

# Create load tester
tester = AmasLoadTester()

# Configure test
config = LoadTestConfig(
    name="research_agent_baseline",
    description="Baseline load test for research agent",
    target_url="http://localhost:8000/api/v1/agents/research/execute",
    method="POST",
    headers={"Content-Type": "application/json"},
    payload_template={
        "query": "Research latest AI developments",
        "research_scope": "broad"
    },
    concurrent_users=10,
    duration_seconds=120,
    ramp_up_seconds=30,
    think_time_seconds=2.0,
    load_pattern=LoadPattern.CONSTANT,
    success_rate_threshold=99.0,
    latency_p95_threshold_ms=1500.0
)

# Run test
report = await tester.run_load_test(config)

# Save report
tester.save_report(report, output_dir="reports/performance")

# Check SLO compliance
print(f"SLO Availability: {'PASS' if report.slo_availability_passed else 'FAIL'}")
print(f"SLO P95 Latency: {'PASS' if report.slo_latency_p95_passed else 'FAIL'}")
```

#### Spike Test

```python
config = LoadTestConfig(
    name="synthesis_agent_spike",
    target_url="http://localhost:8000/api/v1/agents/synthesis/execute",
    concurrent_users=12,
    duration_seconds=300,
    load_pattern=LoadPattern.SPIKE_TEST,
    spike_multiplier=4.0,  # 4x normal load during spikes
    spike_duration_seconds=45
)

report = await tester.run_load_test(config)
```

#### Pre-configured Scenarios

```python
from src.amas.performance.benchmarks.load_tester import create_standard_test_scenarios

# Get standard test scenarios
scenarios = create_standard_test_scenarios()

# Run all scenarios
tester = AmasLoadTester()
for scenario in scenarios:
    report = await tester.run_load_test(scenario)
    tester.save_report(report)
```

### Load Patterns

1. **CONSTANT**: Steady load throughout test
2. **LINEAR_RAMP**: Gradually increase load
3. **STEP_FUNCTION**: Sudden load increases
4. **SPIKE_TEST**: Periodic traffic spikes
5. **STRESS_TEST**: Push system to limits

### Metrics Collected

- **Request Metrics**: Total, successful, failed requests
- **Performance**: P50, P95, P99 latency, average response time
- **Throughput**: Requests per second, MB/s
- **Error Analysis**: Errors by status code and type
- **SLO Compliance**: Availability and latency thresholds
- **Performance Regression**: Comparison with baselines

### Prometheus Metrics

The load tester exports Prometheus metrics:

- `amas_load_test_requests_total`: Total requests by test name, status, phase
- `amas_load_test_request_duration_seconds`: Request duration histogram
- `amas_load_test_active_users`: Current active concurrent users
- `amas_load_test_requests_per_second`: Current RPS

## Performance Monitoring

### Metrics Collection

AMAS collects performance metrics via:

1. **Prometheus**: System and application metrics
2. **Performance Monitor**: Python-based monitoring (`src/monitoring/performance_monitor.py`)
3. **Performance Service**: Service-level optimization (`src/amas/services/performance_service.py`)

### Key Metrics

#### System Metrics
- CPU usage percentage
- Memory usage (bytes and percentage)
- Disk I/O
- Network I/O
- Active connections

#### Application Metrics
- Request count and duration
- Cache hit/miss rates
- Database connection pool utilization
- Response time percentiles (P50, P95, P99)

#### Scaling Metrics
- Pod count and scaling events
- Queue depth
- Request rate per pod
- Resource utilization per pod

### Grafana Dashboards

Pre-configured Grafana dashboards are available:

- **AMAS Overview**: System-wide metrics
- **Performance Metrics**: Application performance
- **Scaling Dashboard**: Autoscaling events and metrics
- **Load Test Results**: Load test analysis

## Best Practices

### Autoscaling Configuration

1. **Set Appropriate Thresholds**
   - CPU: 60-70% for most workloads
   - Memory: 70-80% for memory-intensive workloads
   - Queue Depth: Based on average processing time

2. **Configure Stabilization Windows**
   - Scale-up: 60 seconds (fast response)
   - Scale-down: 300 seconds (prevent oscillation)

3. **Set Reasonable Limits**
   - Min replicas: Ensure availability (2+ for production)
   - Max replicas: Prevent runaway scaling

4. **Monitor Scaling Behavior**
   - Watch for scaling oscillations
   - Adjust cooldown periods if needed
   - Review scaling events regularly

### Load Testing

1. **Start with Baseline Tests**
   - Establish performance baselines
   - Run regularly to detect regressions

2. **Test Realistic Scenarios**
   - Use actual payload sizes
   - Simulate real user behavior
   - Include think times

3. **Validate SLOs**
   - Set appropriate thresholds
   - Monitor SLO compliance
   - Alert on violations

4. **Run Tests Regularly**
   - Before deployments
   - After significant changes
   - As part of CI/CD pipeline

### Performance Optimization

1. **Cache Strategically**
   - Cache frequently accessed data
   - Use appropriate TTLs
   - Monitor cache hit rates

2. **Optimize Database Queries**
   - Use connection pooling
   - Monitor query performance
   - Index appropriately

3. **Monitor Resource Usage**
   - Set up alerts for high usage
   - Right-size containers
   - Use VPA recommendations

## Troubleshooting

### Scaling Issues

**Problem**: Pods not scaling up
- Check KEDA installation: `kubectl get pods -n keda`
- Verify metrics are available: `kubectl get metrics -n amas-prod`
- Check ScaledObject status: `kubectl describe scaledobject -n amas-prod`
- Review Prometheus queries in KEDA config

**Problem**: Too aggressive scaling
- Increase cooldown period
- Increase stabilization window
- Adjust threshold values

**Problem**: Scaling oscillations
- Increase scale-down stabilization window
- Adjust scale-down policies
- Review metric polling intervals

### Load Testing Issues

**Problem**: Tests fail with connection errors
- Verify target URL is accessible
- Check network connectivity
- Review timeout settings

**Problem**: High error rates
- Check application logs
- Verify payload format
- Review response validation

**Problem**: Performance regressions
- Compare with historical baselines
- Review recent code changes
- Check resource constraints

### Performance Issues

**Problem**: High latency
- Check database query performance
- Review cache hit rates
- Monitor resource utilization
- Consider scaling up

**Problem**: High memory usage
- Review cache sizes
- Check for memory leaks
- Optimize data structures
- Consider scaling horizontally

## Additional Resources

- [KEDA Documentation](https://keda.sh/docs/)
- [Kubernetes HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Load Testing Best Practices](https://k6.io/docs/test-types/)

## Support

For issues or questions:
1. Check logs: `kubectl logs -n amas-prod -l app=amas-orchestrator`
2. Review metrics in Grafana
3. Check KEDA events: `kubectl get events -n amas-prod`
4. Open an issue on GitHub
