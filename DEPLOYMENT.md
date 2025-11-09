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
1. Foundation Layer: `kubectl apply -f k8s/foundation/` (deploys Postgres, Redis, OPA, Prometheus)
2. Intelligence Layer: `kubectl apply -f k8s/intelligence/` (deploys agent orchestrator, specialists, frontend)
   - Ensure foundation pods are healthy before moving to intelligence layer.
3. Cloud Load Balancer Setup:
   - Use GKE/EKS/AKS; external DNS and TLS (see `docs/infra/load_balancer_setup.md`)
   - SSL: Use cert-manager for Let's Encrypt or upload managed certificate
   - Allow ingress from trusted IPs only

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
- Retention Policy: All logs and traces kept for at least 30 days and auto-rotated no later than 90 days.
- Alert tokens/URLs for Slack/email only set via k8s Secret or Vault
- All endpoints subject to OPA policy (deny by default)

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
   - Validate UI at http://loadbalancer-ip:3000
   - Check logs in Grafana and Prometheus for errors or unhealthy metrics
   - Confirm agent orchestrator queue is draining as expected
   - Run a test workflow from the UI and verify expected results with end-to-end traces

## Contact & Support
- Issues: [GitHub Issues](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues)
- Email: support@amas-team.org
- Full roadmap: [PRODUCTION_ROADMAP.md](docs/PRODUCTION_ROADMAP.md)

---
