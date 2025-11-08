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

### Deployment

```bash
# Apply KEDA scaler configuration
kubectl apply -f k8s/scaling/keda-scaler.yaml

# Verify KEDA installation
kubectl get scaledobjects -n amas-prod

# Check scaling status
kubectl describe scaledobject amas-orchestrator-scaler -n amas-prod
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

### Prometheus Metrics

The load tester exports Prometheus metrics:

- `amas_load_test_requests_total`: Total requests by test name, status, phase
- `amas_load_test_request_duration_seconds`: Request duration histogram
- `amas_load_test_active_users`: Current active concurrent users
- `amas_load_test_requests_per_second`: Current RPS

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

## Troubleshooting

### Scaling Issues

**Problem**: Pods not scaling up
- Check KEDA installation: `kubectl get pods -n keda`
- Verify metrics are available: `kubectl get metrics -n amas-prod`
- Check ScaledObject status: `kubectl describe scaledobject -n amas-prod`

**Problem**: Too aggressive scaling
- Increase cooldown period
- Increase stabilization window
- Adjust threshold values

## Additional Resources

- [KEDA Documentation](https://keda.sh/docs/)
- [Kubernetes HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
