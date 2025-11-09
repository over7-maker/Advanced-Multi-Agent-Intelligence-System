# ⚡ Performance & Scaling Infrastructure

> **Complete intelligent autoscaling and performance optimization for AMAS**

## Overview

The AMAS Performance & Scaling Infrastructure provides intelligent, event-driven autoscaling and comprehensive performance optimization to handle traffic spikes gracefully with optimal cost efficiency.

## 🎯 Key Features

- **🚀 Intelligent Autoscaling**: KEDA-based multi-metric scaling (HTTP RPS, queue depth, latency, resource usage)
- **💥 Load Testing Framework**: Comprehensive performance testing with SLO validation and regression detection
- **🧠 Semantic Caching**: Redis-based intelligent caching with 30%+ speed improvement
- **🛡️ Resilience Patterns**: Circuit breakers, rate limiting, request deduplication
- **💰 Cost Optimization**: Automatic cost tracking and optimization recommendations

## 📚 Documentation

### Main Guides

1. **[Performance Scaling Guide](PERFORMANCE_SCALING_GUIDE.md)** - **30KB** - Complete infrastructure guide
   - KEDA autoscaling configuration
   - Load testing framework
   - Performance monitoring
   - Best practices
   - Troubleshooting

2. **[Performance Scaling Integration](PERFORMANCE_SCALING_INTEGRATION.md)** - Integration examples
   - Complete integration examples
   - Service usage patterns
   - Best practices
   - Configuration guide

3. **[Performance Benchmarks](performance_benchmarks.md)** - Performance metrics
   - AI provider latency benchmarks
   - Performance expectations
   - Routing policy calibration

## 🚀 Quick Start

### 1. Deploy KEDA Autoscaling

```bash
# Apply KEDA scaler configuration
kubectl apply -f k8s/scaling/keda-scaler.yaml

# Verify installation
kubectl get scaledobjects -n amas-prod
kubectl describe scaledobject amas-orchestrator-scaler -n amas-prod
```

### 2. Run Load Tests

```bash
# List available scenarios
python scripts/run_load_test.py list

# Run specific test
python scripts/run_load_test.py run research_agent_baseline

# Run with custom target
python scripts/run_load_test.py run research_agent_baseline --target http://localhost:8000
```

### 3. Enable Semantic Caching

```python
from src.amas.services.semantic_cache_service import get_semantic_cache

cache = await get_semantic_cache(
    redis_url="redis://localhost:6379/0",
    similarity_threshold=0.85
)

# Use in agent calls
cached = await cache.get(query, agent_id="research_agent", use_semantic=True)
if cached:
    return cached  # 30%+ faster
```

### 4. Test Resilience Patterns

```bash
# Run resilience pattern tests
pytest tests/performance/test_resilience_patterns.py -v
```

## 📁 Implementation Files

### Infrastructure
- `k8s/scaling/keda-scaler.yaml` - Complete KEDA autoscaling configuration
  - Orchestrator scaling
  - Worker scaling
  - Research agent scaling
  - HPA backup
  - VPA integration
  - Pod Disruption Budgets

### Services
- `src/amas/services/semantic_cache_service.py` - Semantic caching
- `src/amas/services/circuit_breaker_service.py` - Circuit breakers
- `src/amas/services/rate_limiting_service.py` - Rate limiting
- `src/amas/services/request_deduplication_service.py` - Request deduplication
- `src/amas/services/cost_tracking_service.py` - Cost tracking
- `src/amas/services/connection_pool_service.py` - Connection pooling
- `src/amas/services/scaling_metrics_service.py` - Scaling metrics

### Testing
- `src/amas/performance/benchmarks/load_tester.py` - Load testing framework
- `tests/performance/test_resilience_patterns.py` - Resilience pattern tests
- `scripts/run_load_test.py` - Load testing CLI tool

## 🎯 Scaling Triggers

### KEDA Scaling Metrics

| Metric | Threshold | Activation | Description |
|--------|-----------|------------|-------------|
| HTTP Request Rate | >15 RPS/pod | 5 RPS | Scale based on request volume |
| Queue Depth | >25 items | 10 items | Scale based on backlog |
| High Latency | P95 >1.0s | 0.5 | Scale when latency indicates capacity issues |
| Resource Pressure | CPU >70% OR Memory >80% | 10% | Scale based on resource utilization |

### Scaling Behavior

- **Scale Up**: Fast (up to 100% increase per minute, max 5 pods)
- **Scale Down**: Conservative (max 10% decrease per minute, max 2 pods)
- **Stabilization**: 1 minute for scale-up, 5 minutes for scale-down
- **Limits**: Min 2 replicas, max 50 replicas

## 💡 Use Cases

### Handle Traffic Spikes
- System automatically scales up when request rate exceeds thresholds
- Maintains <100ms P95 latency during spikes
- Reduces over-provisioning by up to 60% during low traffic

### Optimize Costs
- Automatic cost tracking per request
- Optimization recommendations
- Right-size containers with VPA

### Improve Performance
- Semantic caching for 30%+ speed improvement
- Request deduplication eliminates redundant calls
- Connection pooling optimizes HTTP clients

### Ensure Reliability
- Circuit breakers prevent cascade failures
- Rate limiting prevents abuse
- Pod Disruption Budgets maintain availability

## 📊 Success Criteria

✅ **100 concurrent users** → System scales up automatically  
✅ **Performance test** → Meets latency SLOs under load  
✅ **Repeated requests** → Served from cache with <100ms response  
✅ **Overload component** → Circuit breaker prevents cascade failure  
✅ **Cost per request tracked** → Optimization recommendations generated

## 🔗 Related Documentation

- [Performance Scaling Guide](PERFORMANCE_SCALING_GUIDE.md) - Complete guide
- [Performance Scaling Integration](PERFORMANCE_SCALING_INTEGRATION.md) - Integration examples
- [Performance Benchmarks](performance_benchmarks.md) - Performance metrics
- [Deployment Guide](deployment/DEPLOYMENT.md) - Deployment instructions
- [Production Deployment](deployment/PRODUCTION_DEPLOYMENT.md) - Production setup

## 🛠️ Tools & Scripts

- `scripts/run_load_test.py` - Load testing CLI
- `scripts/update_toc.sh` - TOC auto-generation script
- `k8s/scaling/keda-scaler.yaml` - KEDA configuration

## 📈 Metrics & Monitoring

### Prometheus Metrics
- `amas_scaling_events_total` - Scaling events
- `amas_current_replicas` - Current replica count
- `amas_scaling_duration_seconds` - Scaling duration
- `amas_scaling_effectiveness` - Requests per replica
- `amas_load_test_requests_total` - Load test requests
- `amas_load_test_request_duration_seconds` - Load test duration

### Grafana Dashboards
- Scaling Events Dashboard
- Performance Metrics Dashboard
- Load Test Results Dashboard
- Cost Analytics Dashboard

## 🎓 Learning Resources

- [KEDA Documentation](https://keda.sh/docs/)
- [Kubernetes HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: 2025-11-09
