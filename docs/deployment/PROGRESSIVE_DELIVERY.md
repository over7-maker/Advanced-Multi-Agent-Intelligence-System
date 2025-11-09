# 🚀 Progressive Delivery Pipeline - Comprehensive Guide

## Overview

The AMAS Progressive Delivery Pipeline provides safe, automated deployments with canary releases, automatic rollback, and zero-downtime delivery capabilities. This guide covers everything you need to know about deploying AMAS using the Progressive Delivery system.

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Deployment Strategies](#deployment-strategies)
7. [Monitoring & Observability](#monitoring--observability)
8. [Rollback Procedures](#rollback-procedures)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)
11. [Advanced Topics](#advanced-topics)

---

## Introduction

### What is Progressive Delivery?

Progressive Delivery is a deployment strategy that gradually releases new versions of your application to production, allowing you to validate changes with real traffic before fully deploying. AMAS uses Argo Rollouts to implement this strategy.

### Key Benefits

- **Risk Reduction**: Catch issues early with small traffic percentages
- **Zero Downtime**: Deploy without service interruption
- **Automatic Rollback**: Bad deployments are automatically rolled back
- **SLO-based Gates**: Deployments only proceed if service level objectives are met
- **Real-time Validation**: Monitor actual production metrics during deployment

### How It Works

1. New version is deployed alongside the current version
2. Traffic is gradually shifted to the new version (10% → 25% → 50% → 75% → 100%)
3. At each step, metrics are analyzed to ensure SLOs are met
4. If SLOs are violated, the deployment automatically rolls back
5. If all checks pass, traffic is fully shifted to the new version

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                       │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              Argo Rollouts Controller                 │ │
│  │  - Manages rollout lifecycle                          │ │
│  │  - Executes canary strategy                           │ │
│  │  - Triggers analysis runs                             │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  Stable Service  │         │  Canary Service  │         │
│  │  (Current)        │         │  (New Version)  │         │
│  └──────────────────┘         └──────────────────┘         │
│           │                           │                    │
│           └───────────┬───────────────┘                    │
│                       │                                     │
│              ┌────────▼────────┐                           │
│              │  NGINX Ingress  │                           │
│              │  Traffic Split  │                           │
│              └────────┬────────┘                           │
│                       │                                     │
│              ┌────────▼────────┐                           │
│              │    Prometheus   │                           │
│              │  Metrics Store  │                           │
│              └─────────────────┘                           │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         Analysis Templates (Prometheus Queries)      │ │
│  │  - Success Rate Validation                           │ │
│  │  - Latency P95 Validation                           │ │
│  │  - Error Budget Validation                          │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Traffic Flow

1. **Stable Version (100%)**: All traffic initially goes to the current stable version
2. **Canary Deployment**: New version is deployed, but receives 0% traffic initially
3. **Progressive Shift**: Traffic gradually shifts: 10% → 25% → 50% → 75% → 100%
4. **Analysis**: At 25%, 50%, and 75%, analysis runs validate SLOs
5. **Promotion or Rollback**: Based on analysis results, either promote to 100% or rollback

---

## Prerequisites

### Infrastructure Requirements

- **Kubernetes Cluster**: Version 1.20+ with sufficient resources
- **Argo Rollouts Controller**: Installed and running
- **NGINX Ingress Controller**: For traffic routing and splitting
- **Prometheus**: For metrics collection and analysis
- **kubectl**: Configured with cluster access
- **Argo Rollouts CLI**: For advanced operations (optional but recommended)

### Application Requirements

- **Health Endpoints**: `/health/ready` and `/health/live` endpoints
- **Metrics Export**: Prometheus-compatible metrics
- **Container Image**: Available in container registry
- **Service Labels**: Properly labeled Kubernetes services

### Access Requirements

- **Kubernetes Cluster Access**: `kubectl` configured
- **Container Registry Access**: Push/pull permissions
- **Prometheus Access**: Query access for analysis templates

---

## Installation

### Step 1: Install Argo Rollouts

```bash
# Create namespace
kubectl create namespace argo-rollouts

# Install Argo Rollouts controller
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

# Verify installation
kubectl get pods -n argo-rollouts
```

### Step 2: Install Argo Rollouts CLI (Optional)

```bash
# Linux
curl -LO https://github.com/argoproj/argo-rollouts/releases/latest/download/kubectl-argo-rollouts-linux-amd64
chmod +x kubectl-argo-rollouts-linux-amd64
sudo mv kubectl-argo-rollouts-linux-amd64 /usr/local/bin/kubectl-argo-rollouts

# macOS
brew install argoproj/tap/kubectl-argo-rollouts

# Verify installation
kubectl argo rollouts version
```

### Step 3: Apply Analysis Templates

```bash
# Apply analysis templates (required before rollout)
kubectl apply -f k8s/argo-rollouts/analysis-templates.yaml

# Verify templates
kubectl get analysistemplates -n amas-prod
```

### Step 4: Apply Rollout Configuration

```bash
# Apply rollout configuration
kubectl apply -f k8s/argo-rollouts/rollout.yaml

# Apply network policies (optional but recommended)
kubectl apply -f k8s/argo-rollouts/network-policy.yaml

# Verify rollout
kubectl get rollout amas-orchestrator -n amas-prod
```

---

## Configuration

### Rollout Configuration

The main rollout configuration is in `k8s/argo-rollouts/rollout.yaml`. Key settings:

```yaml
spec:
  replicas: 3
  strategy:
    canary:
      steps:
      - setWeight: 10
        pause: {duration: 1m}
      - setWeight: 25
        pause: {duration: 1m}
        analysis:
          templates:
          - templateName: success-rate
          - templateName: latency-p95
      - setWeight: 50
        pause: {duration: 2m}
        analysis:
          templates:
          - templateName: success-rate
          - templateName: latency-p95
          - templateName: error-budget
      - setWeight: 75
        pause: {duration: 2m}
        analysis:
          templates:
          - templateName: success-rate
          - templateName: latency-p95
          - templateName: error-budget
      - pause: {duration: 1m}
        analysis:
          templates:
          - templateName: health-check
      canaryService: amas-orchestrator-canary
      stableService: amas-orchestrator-stable
      trafficRouting:
        nginx:
          stableIngress: amas-orchestrator-stable
          annotationPrefix: nginx.ingress.kubernetes.io
```

### Analysis Templates

Analysis templates define the SLO thresholds and Prometheus queries. Located in `k8s/argo-rollouts/analysis-templates.yaml`:

- **success-rate**: Validates 95% success rate threshold
- **latency-p95**: Validates P95 latency ≤ 3.0 seconds
- **error-budget**: Validates ≥ 5% error budget remaining
- **health-check**: Validates pod health status

### SLO Thresholds

Default SLO thresholds (configurable in analysis templates):

- **Success Rate**: ≥ 95%
- **P95 Latency**: ≤ 3.0 seconds
- **Error Budget**: ≥ 5% remaining
- **Health Check Timeout**: 2 minutes

### Environment Variables

Configure via environment variables or ConfigMaps:

```bash
export NAMESPACE=amas-prod
export ROLLOUT_NAME=amas-orchestrator
export IMAGE_TAG=latest
export DOCKER_REGISTRY=ghcr.io/over7-maker
export IMAGE_NAME=amas-orchestrator
```

---

## Deployment Strategies

### Canary Deployment (Default)

Progressive traffic shifting with analysis at key points:

```bash
# Using the deployment script
./scripts/deployment/canary_deploy.sh

# Or manually
kubectl set image rollout/amas-orchestrator \
  orchestrator=ghcr.io/over7-maker/amas-orchestrator:v1.2.3 \
  -n amas-prod
```

**Timeline**:
- 10% Traffic: 1 minute pause
- 25% Traffic: 1 minute pause + 1 minute analysis
- 50% Traffic: 2 minute pause + 2 minute analysis
- 75% Traffic: 2 minute pause + 2 minute analysis
- Final Validation: 1 minute pause + 1 minute analysis
- 100% Traffic: Full deployment

**Total Time**: ~8-9 minutes

### Blue-Green Deployment

Instant traffic switching for emergency scenarios:

```bash
# Deploy to inactive environment
./scripts/deployment/blue_green_deploy.sh deploy

# Switch traffic
./scripts/deployment/blue_green_deploy.sh switch

# Rollback
./scripts/deployment/blue_green_deploy.sh rollback
```

### Manual Promotion

Promote canary manually if paused:

```bash
# Promote to next step
kubectl argo rollouts promote amas-orchestrator -n amas-prod

# Promote to 100% (skip remaining steps)
kubectl argo rollouts promote amas-orchestrator -n amas-prod --full
```

---

## Monitoring & Observability

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

# View analysis run metrics
kubectl describe analysisrun <analysis-run-name> -n amas-prod
```

### Prometheus Metrics

Key metrics to monitor:

**Success Rate**:
```promql
sum(rate(http_requests_total{status!~"5.."}[2m])) / sum(rate(http_requests_total[2m]))
```

**P95 Latency**:
```promql
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[2m])) by (le))
```

**Error Budget**:
```promql
(sum(rate(http_requests_total{status!~"5.."}[2m])) / sum(rate(http_requests_total[2m]))) - 0.99
```

### Grafana Dashboards

Create dashboards to visualize:
- Deployment progress
- Traffic split percentages
- Success rates over time
- Latency percentiles
- Error rates
- Rollback events

---

## Rollback Procedures

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

# Force rollback
kubectl rollout undo rollout/amas-orchestrator -n amas-prod --force
```

### Rollback Verification

After rollback, verify:
1. Traffic is fully shifted back to stable version
2. Canary pods are terminated
3. Service health is restored
4. Metrics return to normal

---

## Troubleshooting

### Rollout Stuck

**Symptoms**: Rollout paused at a step and not progressing

**Diagnosis**:
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

**Solutions**:
- Check analysis run failures
- Verify Prometheus connectivity
- Check pod health
- Review SLO thresholds
- Manually promote if needed

### Analysis Failures

**Symptoms**: Analysis runs failing, preventing promotion

**Diagnosis**:
```bash
# View analysis run details
kubectl get analysisrun <name> -n amas-prod -o yaml

# Check Prometheus connectivity
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://prometheus.monitoring.svc.cluster.local:9090/api/v1/query?query=up
```

**Solutions**:
- Verify Prometheus service discovery
- Check metric names match queries
- Review SLO thresholds
- Ensure sufficient data points
- Check network policies

### Traffic Split Issues

**Symptoms**: Traffic not splitting correctly between stable and canary

**Diagnosis**:
```bash
# Check ingress configuration
kubectl get ingress -n amas-prod

# Check service endpoints
kubectl get endpoints -n amas-prod

# View NGINX ingress logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
```

**Solutions**:
- Verify NGINX ingress controller is running
- Check ingress annotations
- Verify service selectors
- Review network policies

### Rollback Issues

**Symptoms**: Rollback not completing or taking too long

**Diagnosis**:
```bash
# Check rollout history
kubectl rollout history rollout/amas-orchestrator -n amas-prod

# Check revision details
kubectl rollout history rollout/amas-orchestrator --revision=2 -n amas-prod

# View rollout events
kubectl describe rollout amas-orchestrator -n amas-prod
```

**Solutions**:
- Force rollback if needed
- Check pod termination
- Verify service endpoints
- Review resource constraints

---

## Best Practices

### Deployment Practices

1. **Always apply analysis templates before rollout**
2. **Test canary deployment in staging first**
3. **Monitor first deployment closely**
4. **Set up alerts for rollback events**
5. **Use semantic versioning for images**
6. **Document custom SLO thresholds**
7. **Keep deployment scripts in version control**

### SLO Configuration

1. **Start conservative**: Use strict thresholds initially
2. **Monitor and adjust**: Refine thresholds based on actual metrics
3. **Document changes**: Keep track of threshold modifications
4. **Test thresholds**: Validate in staging before production

### Monitoring Practices

1. **Set up dashboards**: Visualize deployment progress
2. **Configure alerts**: Get notified of rollback events
3. **Review metrics**: Regularly analyze deployment metrics
4. **Track trends**: Monitor success rates over time

### Security Practices

1. **Use network policies**: Restrict pod communication
2. **Enable pod security**: Use security contexts
3. **Scan images**: Security scan before deployment
4. **Rotate secrets**: Regularly update credentials

---

## Advanced Topics

### Custom Analysis Templates

Create custom analysis templates for specific metrics:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: custom-metric
spec:
  metrics:
  - name: custom-metric
    interval: 30s
    successCondition: result[0] >= 0.95
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          sum(rate(custom_metric_total[2m]))
```

### Multi-Cluster Deployments

Deploy across multiple clusters:

1. Configure cluster contexts
2. Apply rollout to each cluster
3. Coordinate traffic splitting
4. Monitor across clusters

### Integration with CI/CD

Integrate with GitHub Actions:

```yaml
- name: Deploy with Progressive Delivery
  run: |
    kubectl set image rollout/amas-orchestrator \
      orchestrator=${{ env.IMAGE }}:${{ github.sha }} \
      -n amas-prod
```

### Custom Traffic Splitting

Configure custom traffic percentages:

```yaml
steps:
- setWeight: 5
- setWeight: 15
- setWeight: 30
- setWeight: 60
- setWeight: 100
```

---

## Additional Resources

- [Progressive Delivery Quick Start](../PROGRESSIVE_DELIVERY_QUICK_START.md)
- [Progressive Delivery Implementation](../PROGRESSIVE_DELIVERY_IMPLEMENTATION.md)
- [Progressive Delivery Success Criteria](../PROGRESSIVE_DELIVERY_SUCCESS_CRITERIA.md)
- [Argo Rollouts Documentation](https://argoproj.github.io/argo-rollouts/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)

---

## Support

For issues or questions:
- Check [Troubleshooting](#troubleshooting) section
- Review [Argo Rollouts documentation](https://argoproj.github.io/argo-rollouts/)
- Open an issue on GitHub
- Contact the AMAS team

---

**Last Updated**: 2025-01-XX