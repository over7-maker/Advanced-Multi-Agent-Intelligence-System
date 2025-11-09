---
title: Performance Scaling Infrastructure Guide
version: 1.0.0
last_updated: 2025-11-09
description: Comprehensive guide for AMAS performance scaling infrastructure including KEDA autoscaling, load testing, semantic caching, and resilience patterns
summary: This guide covers intelligent autoscaling with KEDA, comprehensive load testing framework, semantic caching for 30%+ speed improvement, circuit breakers, rate limiting, and cost optimization. Includes deployment instructions, best practices, and troubleshooting.
author: AMAS Development Team
status: active
tags: [performance, autoscaling, keda, monitoring, scaling, infrastructure]
---

# Performance Scaling Infrastructure Guide

This guide covers the comprehensive performance scaling infrastructure for AMAS, including KEDA-based autoscaling, load testing, and performance monitoring.

## Table of Contents

<!-- TOC -->
- [Overview](#overview)
  - [Key Components](#key-components)
  - [Architecture Overview](#architecture-overview)
    - [KEDA + HPA + VPA Interaction Flow](#keda--hpa--vpa-interaction-flow)
- [KEDA Autoscaling](#keda-autoscaling)
  - [Architecture](#architecture)
    - [Scaling Triggers](#scaling-triggers)
    - [Architecture Flow](#architecture-flow)
  - [Configuration](#configuration)
    - [Orchestrator Scaling](#orchestrator-scaling)
    - [Security Considerations](#security-considerations)
  - [Deployment](#deployment)
- [Load Testing Framework](#load-testing-framework)
  - [Overview](#overview-1)
  - [Usage](#usage)
    - [Basic Load Test](#basic-load-test)
  - [Prometheus Metrics](#prometheus-metrics)
- [Best Practices](#best-practices)
  - [Autoscaling Configuration](#autoscaling-configuration)
- [Prerequisites](#prerequisites)
  - [Required Components](#required-components)
  - [Configuration Requirements](#configuration-requirements)
- [Troubleshooting](#troubleshooting)
  - [Scaling Issues](#scaling-issues)
  - [Performance Issues](#performance-issues)
  - [Cost Issues](#cost-issues)
  - [Pod Disruption Budgets](#pod-disruption-budgets)
  - [Cold Start Mitigation](#cold-start-mitigation)
  - [Custom Metrics Pipeline](#custom-metrics-pipeline)
  - [GitOps Best Practices](#gitops-best-practices)
- [Additional Resources](#additional-resources)
<!-- /TOC -->

> ⚠️ **Note**: This TOC is auto-generated. To update, run: `npx markdown-toc -i docs/PERFORMANCE_SCALING_GUIDE.md --bullets="-"`. A pre-commit hook is recommended to automate TOC generation.

## Overview

The AMAS performance scaling infrastructure provides intelligent, event-driven autoscaling and comprehensive performance optimization. Based on internal benchmarks, it reduces over-provisioning by up to 60% during low-traffic periods while maintaining <100ms P95 latency during traffic spikes (see [Performance Benchmarks](./performance_benchmarks.md) for detailed metrics).

### Key Components

- **KEDA-based Autoscaling**: Intelligent pod scaling based on multiple metrics (CPU, memory, queue depth, latency) with event-driven triggers
- **Load Testing Framework**: Comprehensive performance testing with realistic traffic patterns, SLO validation, and regression detection
- **Performance Monitoring**: Real-time metrics collection and analysis including request rates, latency distributions, and resource utilization
- **Horizontal Pod Autoscaling (HPA)**: Kubernetes-native autoscaling used in conjunction with KEDA for CPU/memory-based scaling. HPA is automatically disabled when KEDA is active on the same deployment to prevent conflicting scaling triggers. See [KEDA Autoscaling](#keda-autoscaling) for coordination details.
- **Vertical Pod Autoscaling (VPA)**: Automatic right-sizing of container resources based on historical usage patterns (recommendations only in "Off" mode when using HPA/KEDA)
- **Semantic Caching**: Redis-based caching enhanced with embedding similarity matching via external vector search modules (e.g., RedisVL) or integrated AI proxies. Requires dedicated inference resources for embedding computation. See [Performance Benchmarks](./performance_benchmarks.md) for detailed performance metrics and benchmark results.
  
  > **Performance Note**: Semantic similarity lookups should be performed asynchronously or via pre-indexed vectors to avoid blocking request threads. Use RedisVL with HNSW indexes for sub-second performance at scale. Monitor P99 latency of cache lookup operations and set SLOs (e.g., <50ms for cached results).

- **Circuit Breakers**: Fail-fast patterns to prevent cascade failures
- **Rate Limiting**: User-based rate limiting with sliding window algorithm to prevent abuse and ensure fair usage across tenants
- **Cost Tracking**: Automatic token usage and API cost tracking with optimization recommendations

### Architecture Overview

The scaling infrastructure uses a multi-layered approach:

1. **Primary Layer**: KEDA ScaledObjects monitor Prometheus metrics and scale pods based on HTTP RPS, queue depth, latency, and resource pressure
2. **Fallback Layer**: HPA provides CPU/memory-based scaling if KEDA fails
3. **Optimization Layer**: VPA provides recommendations for right-sizing (note: VPA and HPA/KEDA should not be used simultaneously on the same pods - see [Kubernetes documentation](https://kubernetes.io/docs/tasks/run-application/vertical-pod-autoscaler/#known-limitations)). VPA is configured in "Off" mode to provide recommendations only when HPA/KEDA is active.
4. **Protection Layer**: Pod Disruption Budgets ensure availability during scaling events

> **⚠️ WARNING**: VPA and HPA/KEDA should not be used simultaneously on the same pods. VPA in "Off" mode provides only recommendations, not automatic scaling. For production workloads, use either HPA/KEDA for horizontal scaling OR VPA for vertical scaling, but not both.

For detailed architecture diagrams and component interactions, see [PERFORMANCE_SCALING_INTEGRATION.md](./PERFORMANCE_SCALING_INTEGRATION.md).

#### KEDA + HPA + VPA Interaction Flow

```
┌─────────────────┐
│  Prometheus     │
│  Metrics        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌─────────────────┐
│  KEDA           │──────▶│  HPA Controller │
│  ScaledObject   │      │  (if KEDA fails)│
└────────┬────────┘      └────────┬────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐      ┌─────────────────┐
│  Kubernetes API │◀─────│  VPA Recommender │
│  (Pod Scaling)   │      │  (recommendations)│
└─────────────────┘      └─────────────────┘
```

**Note**: VPA provides recommendations only when in "Off" mode. Do not enable VPA "Auto" mode when using HPA/KEDA.

## KEDA Autoscaling

### Architecture

KEDA (Kubernetes Event-Driven Autoscaling) provides event-driven autoscaling for Kubernetes workloads. AMAS uses KEDA to scale based on multiple metrics simultaneously, with the final replica count being the maximum of all trigger calculations.

**HPA/KEDA Coordination**: KEDA creates and manages HPA objects internally. The HPA backup configuration in `k8s/scaling/keda-scaler.yaml` is only used if KEDA fails completely. In normal operation, KEDA's internal HPA handles scaling, preventing conflicts. Both should not be manually configured to target the same deployment simultaneously.

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
- **Secrets Management**: Store sensitive configuration (Redis URLs, API keys, monitoring credentials) in Kubernetes Secrets. Never hardcode credentials or expose secret names/keys in documentation.

> **🔒 SECURITY WARNING**: Always store monitoring credentials (Prometheus, Grafana, etc.) in Kubernetes Secrets. Use generic secret names and avoid documenting exact secret names or key names in public documentation. Reference secrets using environment variables or mounted volumes.

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
   - Use VPA recommendations (in "Off" mode) to right-size containers and reduce waste
   - Monitor cost per request using `cost_tracking_service`
   - Implement semantic caching to reduce redundant API calls:
     - Use asynchronous similarity computation or dedicated microservices
     - Leverage approximate nearest neighbor (ANN) indexing (e.g., HNSW in RedisVL) with precomputed vectors
     - Cache similarity query results with TTLs to avoid repeated computation
     - See [Performance Benchmarks](./performance_benchmarks.md) for detailed benchmark results and performance metrics
   - Use request deduplication for expensive operations
   - Review scaling thresholds regularly to optimize resource usage

> **⚠️ IMPORTANT**: When using VPA for cost optimization, set `updatePolicy` to "Off"` to receive recommendations only. Do not enable VPA "Auto" mode when using HPA/KEDA, as this can cause conflicts. See [Kubernetes VPA limitations](https://kubernetes.io/docs/tasks/run-application/vertical-pod-autoscaler/#known-limitations).

## Prerequisites

Before deploying the performance scaling infrastructure, ensure the following are installed and configured:

### Required Components

1. **Kubernetes Cluster**
   - Kubernetes 1.20 or higher
   - Metrics Server installed and running
   - Cluster with sufficient resources for scaling

2. **KEDA Operator**
   - KEDA 2.0+ installed in cluster
   - Verify installation: `kubectl get pods -n keda-system`
   - See [KEDA Installation Guide](https://keda.sh/docs/latest/deploy/)

3. **Prometheus**
   - Prometheus installed and scraping AMAS metrics
   - Accessible at configured endpoint (default: `http://prometheus.monitoring.svc.cluster.local:9090`)
   - Metrics exported by AMAS application

4. **Redis** (for caching and rate limiting)
   - Redis cluster accessible from pods
   - **Security Requirements** (enforced at runtime):
     - **TLS 1.3+ encryption** enabled for all connections (validated via startup probe)
     - **Authentication required** (AUTH with strong passwords or client certificate authentication)
     - **Network policies** restricting Redis access to application pods only
     - **Secrets management**: Use SealedSecrets or external secret stores (e.g., HashiCorp Vault) for Redis credentials
     - **Runtime validation**: Health check or init container verifies AUTH and TLS are enabled before application startup
     - **Admission controllers**: Consider using OPA/Gatekeeper policies to reject deployments without proper Redis security configuration
   - Connection URL configured in application via environment variables (never hardcode)
   - Optional but recommended for optimal performance

5. **VPA** (optional, for vertical scaling)
   - VPA recommender installed
   - Note: Do not use VPA "Auto" mode with HPA/KEDA

### Configuration Requirements

- Prometheus metrics endpoint accessible (with authentication if exposed externally)
- Redis connection URL (if using semantic caching or distributed rate limiting)
  - Use TLS-encrypted connections
  - Store connection credentials in Kubernetes Secrets
- Sufficient cluster resources for max replica count
- Network policies configured (see `k8s/scaling/keda-scaler.yaml`)
- Pod Disruption Budgets configured for critical components (see example below)

## Troubleshooting

### Scaling Issues

**Problem**: Pods not scaling up

**Diagnosis Steps:**
1. Check KEDA installation: `kubectl get pods -n keda-system`
2. Verify metrics are available: `kubectl get metrics -n amas-prod`
3. Check ScaledObject status: `kubectl describe scaledobject amas-orchestrator-scaler -n amas-prod`
4. Verify Prometheus connectivity: Check KEDA logs for connection errors
5. Check metric queries: Verify Prometheus queries return data

**Solutions:**
- Ensure Prometheus is accessible from KEDA pods
- Verify metric names match those exported by AMAS
- Check network policies allow KEDA to access Prometheus
- Review KEDA operator logs: `kubectl logs -n keda-system -l app=keda-operator`

**Problem**: Too aggressive scaling

**Symptoms:**
- Pods scaling up and down rapidly (thrashing)
- High number of scaling events in short time
- Unstable replica counts

**Solutions:**
- Increase cooldown period in KEDA ScaledObject
- Increase stabilization window (especially scale-down)
- Adjust threshold values to be less sensitive
- Review scaling policies to be more conservative

**Problem**: Pods not scaling down

**Diagnosis:**
- Check if metrics are below thresholds
- Verify cooldown period hasn't expired
- Review scale-down policies

**Solutions:**
- Reduce min replicas if appropriate
- Adjust scale-down policies to be more aggressive
- Check for stuck metrics or stale data

### Performance Issues

**Problem**: High latency despite scaling

**Diagnosis:**
- Check if pods are actually scaling
- Verify resource limits aren't too restrictive
- Review application performance metrics

**Solutions:**
- Increase resource limits per pod
- Review scaling thresholds (may be too high)
- Check for application bottlenecks
- Consider VPA recommendations for right-sizing

**Problem**: Cache hit rate too low

**Diagnosis:**
- Check semantic cache statistics
- Verify Redis connectivity
- Review cache TTL settings

**Solutions:**
- Increase cache TTL for stable data
- Adjust similarity threshold
- Verify Redis is properly configured
- Review cache eviction policies

### Cost Issues

**Problem**: High infrastructure costs

**Diagnosis:**
- Review cost tracking service statistics
- Check scaling events and replica counts
- Analyze cost per request

**Solutions:**
- Optimize scaling thresholds to reduce unnecessary scaling
- Use VPA recommendations to right-size containers
- Implement semantic caching to reduce API calls
- Review and adjust max replica limits
- Monitor and optimize based on cost tracking recommendations

### Pod Disruption Budgets

For stateful components and critical services, configure Pod Disruption Budgets to maintain availability during scaling events:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: amas-orchestrator-pdb
  namespace: amas-prod
spec:
  selector:
    matchLabels:
      app: amas-orchestrator
  minAvailable: 2  # Or use maxUnavailable: 25%
```

**Best Practices:**
- Set `minAvailable` to ensure at least N pods are always running
- For stateless services, use `maxUnavailable` percentage
- For stateful services, use `minAvailable` count
- Consider cluster node maintenance windows when setting values

### Cold Start Mitigation

When using scale-from-zero configurations (KEDA with `minReplicaCount: 0`):

- **Warm-up Strategy**: Use `idleReplicaCount` to maintain minimum pods
- **Pre-warming**: Implement health check endpoints that initialize dependencies
- **Connection Pooling**: Pre-initialize connection pools in startup code
- **Cache Warming**: Pre-populate frequently accessed cache entries
- **Monitoring**: Track cold start latency separately from warm request latency

### Custom Metrics Pipeline

For advanced scaling beyond CPU/memory, set up a custom metrics pipeline:

1. **Export Custom Metrics**: Expose application metrics via Prometheus format
2. **Prometheus Scraping**: Configure Prometheus to scrape custom metrics
3. **KEDA Integration**: Reference custom metrics in KEDA ScaledObject triggers
4. **Validation**: Verify metrics are available before enabling scaling

Example custom metric in KEDA:
```yaml
triggers:
- type: prometheus
  metadata:
    serverAddress: http://prometheus.monitoring.svc.cluster.local:9090
    metricName: custom_request_rate
    query: rate(amas_custom_metric_total[2m])
    threshold: '100'
```

### GitOps Best Practices

For production deployments, use GitOps principles:

- **Version Control**: Store all scaling configurations in Git
- **Automated Deployment**: Use CI/CD pipelines to apply configurations
- **Configuration Drift Prevention**: Use tools like ArgoCD or Flux to sync configurations
- **Review Process**: Require PR reviews for scaling configuration changes
- **Rollback Strategy**: Maintain previous configurations for quick rollback

**Avoid Manual Scaling:**
- Do not manually scale pods in production (`kubectl scale`)
- Use configuration changes in Git to trigger scaling adjustments
- Monitor scaling events through observability tools, not manual inspection

## Additional Resources

- [KEDA Documentation](https://keda.sh/docs/)
- [Kubernetes HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
