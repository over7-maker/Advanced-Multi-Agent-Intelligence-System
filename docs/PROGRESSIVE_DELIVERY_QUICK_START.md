# 🚀 Progressive Delivery Pipeline - Quick Start Guide

## Overview

This guide provides a quick start for using the Progressive Delivery Pipeline with Argo Rollouts, enabling safe, automated deployments with canary releases and automatic rollback.

## Prerequisites

1. **Kubernetes Cluster** with Argo Rollouts installed**
2. **NGINX Ingress Controller** for traffic routing
3. **Prometheus** for metrics-based analysis
4. **kubectl** and **Argo Rollouts CLI** configured

## Installation

### 1. Install Argo Rollouts

```bash
# Create namespace
kubectl create namespace argo-rollouts

# Install Argo Rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

# Install Argo Rollouts CLI (optional but recommended)
curl -LO https://github.com/argoproj/argo-rollouts/releases/latest/download/kubectl-argo-rollouts-linux-amd64
chmod +x kubectl-argo-rollouts-linux-amd64
sudo mv kubectl-argo-rollouts-linux-amd64 /usr/local/bin/kubectl-argo-rollouts
```

### 2. Apply Analysis Templates

```bash
# Apply analysis templates first (required before rollout)
kubectl apply -f k8s/argo-rollouts/analysis-templates.yaml
```

### 3. Apply Rollout Configuration

```bash
# Apply the rollout configuration
kubectl apply -f k8s/argo-rollouts/rollout.yaml

# Apply network policies (optional but recommended)
kubectl apply -f k8s/argo-rollouts/network-policy.yaml
```

## Usage

### Canary Deployment

#### Using the Script

```bash
# Set environment variables
export NAMESPACE=amas-prod
export ROLLOUT_NAME=amas-orchestrator
export IMAGE_TAG=v1.2.3
export DOCKER_REGISTRY=ghcr.io/over7-maker
export IMAGE_NAME=amas-orchestrator

# Run canary deployment
./scripts/deployment/canary_deploy.sh
```

#### Manual Deployment

```bash
# Update rollout image (triggers canary)
kubectl set image rollout/amas-orchestrator \
  orchestrator=ghcr.io/over7-maker/amas-orchestrator:v1.2.3 \
  -n amas-prod

# Monitor rollout progress
kubectl argo rollouts get rollout amas-orchestrator -n amas-prod

# Promote to next step (if paused)
kubectl argo rollouts promote amas-orchestrator -n amas-prod
```

### Blue-Green Deployment

```bash
# Deploy to inactive environment and switch traffic
./scripts/deployment/blue_green_deploy.sh deploy

# Just switch traffic (if both environments ready)
./scripts/deployment/blue_green_deploy.sh switch

# Rollback to previous environment
./scripts/deployment/blue_green_deploy.sh rollback
```

## Monitoring

### View Rollout Status

```bash
# Get rollout status
kubectl argo rollouts get rollout amas-orchestrator -n amas-prod

# Watch rollout in real-time
kubectl argo rollouts get rollout amas-orchestrator -n amas-prod --watch

# View rollout history
kubectl argo rollouts history amas-orchestrator -n amas-prod
```

### View Analysis Runs

```bash
# List analysis runs
kubectl get analysisruns -n amas-prod

# View analysis run details
kubectl get analysisrun <analysis-run-name> -n amas-prod -o yaml

# View analysis run logs
kubectl logs -n amas-prod -l app=amas-orchestrator
```

### Prometheus Metrics

Access Prometheus to view metrics:
- Success Rate: `sum(rate(http_requests_total{status!~"5.."}[2m])) / sum(rate(http_requests_total[2m]))`
- P95 Latency: `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[2m])) by (le))`
- Error Budget: `(sum(rate(http_requests_total{status!~"5.."}[2m])) / sum(rate(http_requests_total[2m]))) - 0.99`

## Rollback

### Automatic Rollback

Rollback is triggered automatically when:
- Success rate drops below 95%
- P95 latency exceeds 3.0 seconds
- Error budget remaining falls below 5%
- Health checks fail for >2 minutes

### Manual Rollback

```bash
# Rollback to previous revision
kubectl rollout undo rollout/amas-orchestrator -n amas-prod

# Rollback to specific revision
kubectl rollout undo rollout/amas-orchestrator --to-revision=2 -n amas-prod

# Abort current rollout
kubectl argo rollouts abort amas-orchestrator -n amas-prod
```

## Deployment Timeline

The optimized canary deployment follows this timeline:

1. **10% Traffic** → 1 minute pause
2. **25% Traffic** → 1 minute pause + 1 minute analysis
3. **50% Traffic** → 2 minute pause + 2 minute analysis
4. **75% Traffic** → 2 minute pause + 2 minute analysis
5. **Final Validation** → 1 minute pause + 1 minute analysis
6. **100% Traffic** → Full deployment

**Total Time: ~8-9 minutes** (meets <10 minute requirement)

## Troubleshooting

### Rollout Stuck

```bash
# Check rollout status
kubectl get rollout amas-orchestrator -n amas-prod

# Check analysis runs
kubectl get analysisruns -n amas-prod

# Check pod status
kubectl get pods -n amas-prod -l app=amas-orchestrator

# View rollout events
kubectl describe rollout amas-orchestrator -n amas-prod
```

### Analysis Failures

```bash
# View analysis run details
kubectl get analysisrun <name> -n amas-prod -o yaml

# Check Prometheus connectivity
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://prometheus.monitoring.svc.cluster.local:9090/api/v1/query?query=up
```

### Rollback Issues

```bash
# Force rollback
kubectl rollout undo rollout/amas-orchestrator -n amas-prod --force

# Check revision history
kubectl rollout history rollout/amas-orchestrator -n amas-prod
```

## Best Practices

1. **Always apply analysis templates before rollout**
2. **Monitor first deployment closely**
3. **Set up alerts for rollback events**
4. **Test rollback procedures regularly**
5. **Keep deployment scripts in version control**
6. **Use semantic versioning for images**
7. **Document custom SLO thresholds**

## Next Steps

- Read the [Implementation Guide](PROGRESSIVE_DELIVERY_IMPLEMENTATION.md)
- Review [Testing Guide](../PROGRESSIVE_DELIVERY_CHECKLIST.md)
- Configure CI/CD integration
- Set up monitoring dashboards
- Load test the deployment process
