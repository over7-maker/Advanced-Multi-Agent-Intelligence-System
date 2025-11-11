# AMAS Deployment Guide

## Table of Contents
- [System Requirements](#system-requirements)
- [Local Development (Step-by-Step)](#local-development-step-by-step)
- [Environment Variables](#environment-variables)
- [Production/Staging Deployment](#productionstaging-deployment)
- [Kubernetes & Scaling](#kubernetes--scaling)
- [CI/CD Pipeline Example](#cicd-pipeline-example)
- [Security Practices](#security-practices)
- [Monitoring, Alerts, and Troubleshooting](#monitoring-alerts-and-troubleshooting)
- [Backup & Recovery](#backup--recovery)
- [Documentation Versioning](#documentation-versioning)
- [Validation Steps](#validation-steps)
- [Contact & Support](#contact--support)

---

## System Requirements
- Docker v20+, Docker Compose
- Kubernetes 1.28+ (required); KEDA and OPA controllers must be present
- Node.js 18+, Python 3.11+
- Grafana/Prometheus stack for observability

## Local Development (Step-by-Step)
1. Clone repo: `git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git`
2. Backend setup:
   - `cd backend` → `pip install -r requirements.txt` → `cp .env.example .env` (edit)
3. Frontend setup:
   - `cd frontend` → `npm install`
4. Start all services:
   - `docker-compose up -d`
   - Default UI: http://localhost:3000/
   - Key services: agent-orchestrator, frontend, postgres, redis, n8n
5. Check logs:
   - `docker-compose logs agent-orchestrator`
   - `docker-compose ps` to verify all expected containers are running

## Environment Variables
- **Mandatory .env keys**:
   - `OIDC_CLIENT_ID`, `OIDC_CLIENT_SECRET`, `DATABASE_URL`, `AGENT_API_TOKEN`, `FRONTEND_SECRET`
- All secrets stored in `.env` must be encrypted at rest and never checked into version control.
- For Kubernetes, use `kubectl create secret` (see `k8s/foundation/` docs)

## Production/Staging Deployment

### Deployment Steps

#### 1. Foundation Layer
Deploy foundation services: `kubectl apply -f k8s/foundation/` (deploys Postgres, Redis, OPA, Prometheus)

#### 2. Intelligence Layer
Deploy intelligence components: `kubectl apply -f k8s/intelligence/` (deploys agent orchestrator, specialists, frontend)
- Ensure foundation pods are healthy before moving to intelligence layer.

#### 3. Orchestration System
Deploy the Hierarchical Agent Orchestration System

**Recommended**: Use deployment script for automated deployment:
```bash
./scripts/deploy-orchestration.sh
```

**Manual Alternative**: Step-by-step deployment:
- See [Orchestration Deployment Guide](docs/deployment/ORCHESTRATION_DEPLOYMENT.md) for detailed instructions
- **Prerequisites**: 
  - **Namespace Setup**: Create namespace using idempotent manifest:
    ```bash
    # Use namespace manifest for idempotent creation
    kubectl apply -f k8s/amas-namespace.yaml
    ```
    **Warning**: Use unique, environment-specific namespace names in multi-tenant clusters. Always pair namespace creation with RBAC policies limiting access to authorized users.
  - **Security Hardening**: For production, apply ResourceQuota and NetworkPolicy:
    ```bash
    # Apply resource quota to limit resource consumption in the amas namespace
    kubectl apply -f k8s/amas-namespace-quota.yaml -n amas
    # Verify quota applied
    kubectl get resourcequota -n amas
    
    # Enforce network isolation to restrict pod-to-pod communication
    kubectl apply -f k8s/amas-network-policy.yaml -n amas
    # Verify network policy applied
    kubectl get networkpolicy -n amas
    ```
  - **Best Practice**: Preview changes before applying:
    ```bash
    kubectl diff -f k8s/orchestration-configmap.yaml -n amas
    kubectl diff -f k8s/orchestration-deployment.yaml -n amas
    kubectl diff -f k8s/orchestration-hpa.yaml -n amas
    ```
- **Deploy configuration**: `kubectl apply -f k8s/orchestration-configmap.yaml -n amas`
- **Deploy service**: `kubectl apply -f k8s/orchestration-deployment.yaml -n amas`
- **Deploy autoscaling**: `kubectl apply -f k8s/orchestration-hpa.yaml -n amas`
- **Verify deployment**: 
  ```bash
  # Check pod readiness (wait for ready condition)
  kubectl wait --for=condition=ready pod -l component=orchestration -n amas --timeout=120s
  
  # Verify pods are running
  kubectl get pods -l component=orchestration -n amas
  
  # Verify resource requests/limits for HPA
  kubectl describe deployment amas-orchestration -n amas | grep -A5 Resources
  ```
  **Note**: Ensure the deployment defines CPU/memory requests for HPA to work effectively.
  
  **Performance Tip**: For better scaling, consider using custom metrics (e.g., agent task queue length via Prometheus) in orchestration-hpa.yaml. Example:
  ```yaml
  metrics:
  - type: Pods
    pods:
      metric:
        name: task_queue_length
      target:
        type: AverageValue
        averageValue: 100
  ```

- **Rollback** (if needed):
  ```bash
  kubectl rollout undo deployment/amas-orchestration -n amas
  ```

#### 4. Cloud Load Balancer Setup
- Use GKE/EKS/AKS; external DNS and TLS (see `docs/infra/load_balancer_setup.md`)
- SSL: Use cert-manager for Let's Encrypt or upload managed certificate
- **IP Whitelisting**: Restrict ingress to trusted CIDR ranges (e.g., corporate network or API gateways) using firewall rules or Ingress annotations:
  ```yaml
  annotations:
    nginx.ingress.kubernetes.io/whitelist-source-range: 192.168.1.0/24,203.0.113.0/24
  ```
  Or see `k8s/ingress-restrictions.yaml` for IP whitelisting example.
- **Best Practice**: Enable mTLS between orchestrator and agent pods using service mesh (e.g., Istio, Linkerd) in production environments for encrypted internal communication.

### Environment-Specific Deployment

**Best Practice**: Use Kustomize or Helm with overlays for environment-specific settings:
```bash
# Production
kustomize build environments/prod | kubectl apply -f -

# Staging
kustomize build environments/staging | kubectl apply -f -

# Development
kustomize build environments/dev | kubectl apply -f -
```

## Kubernetes & Scaling
- **Minimum:** CPUs/memory in each deployment YAML (see `k8s/foundation/`).
- **Autoscaling:** KEDA with thresholds (CPU > 75%, queue depth > 10); `spec.replicas: 3-30` typical.
- **Metrics:** Scale on `agents.active_tasks` or custom workload metric.

## CI/CD Pipeline Example
- All builds and releases triggered by GitHub Actions:
   - Lint → Type check → Test → Build Docker → Scan with Snyk → Push to registry → Deploy to k8s via ArgoCD
- All secrets for CI/CD stored in repository secrets, never in code
- Supply chain protection: Dependabot, Snyk (auto PR creation for critical CVEs)

## Security Practices
- Token rotation for OIDC/JWT (expires in 15min, refresh tokens enabled by default)
- All .env and k8s secrets encrypted at rest, loaded via secret manager/injected at pod runtime
- **Pod Security**: Orchestration pods run with:
  - `runAsNonRoot: true` and `runAsUser: 1001`
  - `allowPrivilegeEscalation: false`
  - Dropped capabilities (ALL)
  - Read-only root filesystem where possible
- **Secret Management**: All secrets referenced via Kubernetes Secret objects, never in ConfigMap
- **Internal Communication**: Enable mTLS via service mesh (Istio/Linkerd) for encrypted pod-to-pod communication
- Retention Policy: All logs and traces kept for at least 30 days and auto-rotated no later than 90 days.
- Alert tokens/URLs for Slack/email only set via k8s Secret or Vault
- All endpoints subject to OPA policy (deny by default)
- **RBAC**: Ensure namespace creation is paired with RBAC policies limiting access to authorized users

## Monitoring, Alerts, and Troubleshooting
- Prometheus + Grafana dashboards for `agent-latency`, `task-throughput`, `error-rates`
- OpenTelemetry traces to Grafana Cloud or custom endpoint
- Errors: Review `kubectl logs` and `kubectl describe pod` for live debugging
- For alert/notification config, see `docs/infra/alerting_setup.md`

## Backup & Recovery
- Nightly DB backups scheduled as Kubernetes batch jobs to encrypted storage
- Redis/Agent logs snapshotted every 6h; see `/docs/infra/restore_guide.md`

## Documentation Versioning
- Docs use project version tagging (`vX.Y.Z`)
- Major revisions and breaking infra changes noted in CHANGELOG.md

## Validation Steps
- After each deployment phase:
  - Run `kubectl get pods` and check readiness
  - **Validate UI**: Access via HTTPS at your configured domain (e.g., `https://your-domain.com`)
    - **Note**: For internal testing only, port 3000 may be exposed via NodePort or port-forwarding:
      ```bash
      kubectl port-forward svc/amas 3000:3000 -n amas
      ```
      **Security**: Never expose port 3000 publicly without TLS. Do not expose publicly.
  - Check logs in Grafana and Prometheus for errors or unhealthy metrics
  - Confirm agent orchestrator queue is draining as expected
  - **Orchestration System**: Validate orchestration deployment:
    - Check orchestration pods: `kubectl get pods -l component=orchestration -n amas`
    - Verify health: `kubectl exec -n amas deployment/amas-orchestration -- curl -s http://localhost:8000/health/orchestration`
      - **Note**: Health endpoints are for internal cluster validation only and should not be exposed externally without authentication
    - Check metrics: `kubectl port-forward svc/amas-orchestration 9090:9090 -n amas`
    - Test task decomposition: See [Orchestration Deployment Guide](docs/deployment/ORCHESTRATION_DEPLOYMENT.md#validation--testing)
  - **Performance Validation**:
    - Submit 50 test workflows and monitor queue latency in Prometheus
    - Verify HPA scales pods: `kubectl get hpa amas-orchestration-hpa -n amas`
    - Check average response time < 500ms under load
    - Monitor message queue depth: `kubectl exec -n amas deployment/amas-orchestration -- curl -s http://localhost:9090/metrics | grep orchestration_message_queue_depth`
  - **End-to-End Testing**:
    - **Prerequisite**: Ensure OpenTelemetry instrumentation is enabled and trace context headers (e.g., `traceparent`) are propagated across services
    - Run a test workflow from the UI and verify expected results with end-to-end traces
    - Verify trace correlation across orchestration components in Grafana or your tracing backend

## Contact & Support
- Issues: [GitHub Issues](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues)
- Email: support@amas-team.org
- Full roadmap: [PRODUCTION_ROADMAP.md](docs/PRODUCTION_ROADMAP.md)

---
