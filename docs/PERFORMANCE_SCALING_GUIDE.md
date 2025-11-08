# Performance Scaling Infrastructure Guide

> **Version:** 1.0.0 | **Last Updated:** 2025-11-08

This guide covers the comprehensive performance scaling infrastructure for AMAS, including KEDA-based autoscaling, load testing, and performance monitoring.

## Table of Contents

- [Overview](#overview)
- [KEDA Autoscaling](#keda-autoscaling)
- [Load Testing Framework](#load-testing-framework)
- [Performance Monitoring](#performance-monitoring)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The AMAS performance scaling infrastructure provides intelligent, event-driven autoscaling and comprehensive performance optimization to handle traffic spikes gracefully with optimal cost efficiency.

### Key Components

- **KEDA-based Autoscaling**: Intelligent pod scaling based on multiple metrics (CPU, memory, queue depth, latency) with event-driven triggers
- **Load Testing Framework**: Comprehensive performance testing with realistic traffic patterns, SLO validation, and regression detection
- **Performance Monitoring**: Real-time metrics collection and analysis including request rates, latency distributions, and resource utilization
- **Horizontal Pod Autoscaling (HPA)**: Kubernetes-native autoscaling as fallback when KEDA is unavailable
- **Vertical Pod Autoscaling (VPA)**: Automatic right-sizing of container resources based on historical usage patterns
- **Semantic Caching**: Redis-based intelligent caching with embedding similarity matching for 30%+ speed improvement
- **Circuit Breakers**: Fail-fast patterns to prevent cascade failures
- **Rate Limiting**: User-based quotas with sliding window algorithm
- **Cost Tracking**: Automatic token usage and API cost tracking with optimization recommendations

### Architecture Overview

The scaling infrastructure uses a multi-layered approach:

1. **Primary Layer**: KEDA ScaledObjects monitor Prometheus metrics and scale pods based on HTTP RPS, queue depth, latency, and resource pressure
2. **Fallback Layer**: HPA provides CPU/memory-based scaling if KEDA fails
3. **Optimization Layer**: VPA automatically adjusts resource requests/limits based on actual usage
4. **Protection Layer**: Pod Disruption Budgets ensure availability during scaling events

For detailed architecture diagrams and component interactions, see [PERFORMANCE_SCALING_INTEGRATION.md](./PERFORMANCE_SCALING_INTEGRATION.md).

## KEDA Autoscaling

### Architecture

KEDA (Kubernetes Event-Driven Autoscaling) provides event-driven autoscaling for Kubernetes workloads. AMAS uses KEDA to scale based on multiple metrics simultaneously, with the final replica count being the maximum of all trigger calculations.

#### Scaling Triggers

AMAS uses four primary scaling triggers:

1. **HTTP Request Rate**: Monitors `rate(amas_agent_requests_total[2m])` and scales when >15 RPS per pod (activation at 5 RPS)
2. **Queue Depth**: Tracks `amas_queue_depth_current` and scales when >25 queued items (activation at 10 items)
3. **Latency**: Monitors P95 latency via `histogram_quantile(0.95, rate(amas_agent_duration_seconds_bucket[2m]))` and scales when >1.0 seconds
4. **Resource Utilization**: Tracks CPU and memory pressure, scaling when CPU >70% OR memory >80%

#### Architecture Flow

```
Prometheus Metrics → KEDA ScaledObject → HPA Controller → Kubernetes API → Pod Scaling
     ↓                      ↓                    ↓
  Query Metrics      Evaluate Triggers    Apply Scaling Policy
     ↓                      ↓                    ↓
  Update Values      Calculate Replicas   Scale Pods
```

### Configuration

The KEDA scaler configuration is located at `k8s/scaling/keda-scaler.yaml`. The configuration includes:

- **Scaling Metrics**: HTTP request rate, queue depth, latency, CPU, memory
- **Scaling Thresholds**: 
  - HTTP request rate > 15 RPS per pod (activation at 5 RPS)
  - Queue depth > 25 items (activation at 10 items)
  - P95 latency > 1.0 seconds (activation at 0.5)
  - CPU > 70% OR memory > 80% (activation at 10%)
- **Scaling Behavior**: Aggressive scaling up, conservative scaling down

#### Orchestrator Scaling

The orchestrator uses multi-metric scaling with the following configuration:

**Scaling Metrics:**
- HTTP request rate: Scale up when >15 RPS per pod, activation at 5 RPS
- Agent queue depth: Scale up when >25 queued items, activation at 10 items
- High latency: Scale up when P95 latency >1.0 seconds
- Resource pressure: Scale up when CPU >70% OR memory >80%

**Scaling Behavior:**
- **Min Replicas**: 2 (ensures high availability)
- **Max Replicas**: 50 (safety limit to prevent runaway scaling)
- **Polling Interval**: 15 seconds (responsive scaling)
- **Cooldown Period**: 180 seconds (3 minutes, prevents oscillation)

**Scale-Up Policy:**
- Stabilization window: 60 seconds
- Max increase: 100% per minute OR 5 pods per minute
- Selects maximum (aggressive scaling for fast response)

**Scale-Down Policy:**
- Stabilization window: 300 seconds (5 minutes)
- Max decrease: 10% per minute OR 2 pods per minute
- Selects minimum (conservative scaling to prevent thrashing)

#### Security Considerations

When configuring autoscaling, consider the following security best practices:

- **Resource Limits**: Set appropriate max replicas to prevent resource exhaustion attacks
- **Metric Validation**: Ensure Prometheus metrics are properly authenticated and validated
- **Network Policies**: Use NetworkPolicies to restrict pod-to-pod communication during scaling
- **RBAC**: Configure proper Role-Based Access Control for KEDA and HPA components
- **Secrets Management**: Store sensitive configuration (Redis URLs, API keys) in Kubernetes Secrets

The KEDA scaler configuration includes NetworkPolicy definitions (see `k8s/scaling/keda-scaler.yaml` lines 300-362) that restrict ingress and egress traffic appropriately.

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
   - CPU: 60-70% for most workloads (allows headroom for traffic spikes)
   - Memory: 70-80% for memory-intensive workloads (prevents OOM kills)
   - Queue Depth: Based on average processing time (e.g., if avg processing is 2s, queue depth of 25 = ~50s of work)
   - Latency: P95 threshold should be based on SLO requirements (typically 1-2 seconds)

2. **Configure Stabilization Windows**
   - Scale-up: 60 seconds (fast response to traffic spikes)
   - Scale-down: 300 seconds (prevent oscillation and unnecessary scaling)
   - These windows prevent rapid scaling changes that can cause instability

3. **Set Reasonable Limits**
   - Min replicas: Ensure availability (2+ for production, provides redundancy)
   - Max replicas: Prevent runaway scaling (50 is a safety limit, adjust based on cluster capacity)
   - Consider cluster resource limits when setting max replicas

4. **Monitor Scaling Effectiveness**
   - Track scaling events using `scaling_metrics_service`
   - Monitor requests per replica to ensure efficient resource usage
   - Review scaling decisions regularly to optimize thresholds

5. **Cost Optimization**
   - Use VPA to right-size containers and reduce waste
   - Monitor cost per request using `cost_tracking_service`
   - Implement semantic caching to reduce redundant API calls
   - Use request deduplication for expensive operations

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
