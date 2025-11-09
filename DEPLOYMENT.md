# AMAS Deployment Guide

## Table of Contents
- [System Requirements](#system-requirements)
- [Local Development (Step-by-Step)](#local-development-step-by-step)
- [Environment Variables](#environment-variables)
- [Production/Staging Deployment](#productionstaging-deployment)
- [Kubernetes & Scaling](#kubernetes--scaling)
- [CI/CD & Security](#cicd--security)
- [Monitoring, Alerts, and Troubleshooting](#monitoring-alerts-and-troubleshooting)
- [Backup & Recovery](#backup--recovery)
- [Contact & Support](#contact--support)

---

## System Requirements
- Docker v20+, Docker Compose
- Kubernetes 1.28+ (tested); requires KEDA and OPA controllers installed
- Node.js 18+, Python 3.11+
- Grafana/Prometheus stack for observability

## Local Development (Step-by-Step)
1. Clone repo: `git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git`
2. Backend setup:
   - `cd backend`
   - `pip install -r requirements.txt`
   - `cp .env.example .env` and fill in values
3. Frontend setup:
   - `cd frontend`
   - `npm install`
4. Start services:
   - `docker-compose up -d`
   - Default UI: http://localhost:3000/
5. Check logs:
   - `docker-compose logs agent-orchestrator`
   - `docker-compose ps` to verify healthy containers

## Environment Variables
- All runtime secrets must be set via `.env` (never committed).
- Sample variables: `OIDC_CLIENT_ID, OIDC_CLIENT_SECRET, DATABASE_URL, AGENT_API_TOKEN`
- For Kubernetes: use `kubectl create secret` to load all production secrets.

## Production/Staging Deployment
1. Confirm all k8s manifests in `k8s/foundation/` are applied:
   - `kubectl apply -f k8s/foundation/`
2. Once core infra is healthy, deploy agents/intelligence layer:
   - `kubectl apply -f k8s/intelligence/`
3. Configure cloud load balancer (e.g. GKE, EKS):
   - Set external DNS, enable SSL/TLS (see `docs/infra/load_balancer_setup.md`)
   - Security: Only allow inbound from trusted networks.
4. Configure SSL via cert-manager or Let's Encrypt as per hosting cloud provider.
   - Ensure SSL/TLS secrets rotate at least every 60 days.

## Kubernetes & Scaling
- Minimum resource requests/limits in each deployment YAML (see foundation/k8s/).
- KEDA: Scale agent deployments on CPU > 75% usage or work queue metrics.
- Example: `spec.replicas: 3-30`, horizontally scaling per concurrency demands.
- Tune `agents.active_tasks` metric for optimal cost/performance.

## CI/CD & Security
- All images built via GitHub Actions, pushed to private registry.
- OIDC/JWT configured with token expiration ≤ 15min, refresh token support, secrets only in memory on instance.
- `opa-policy-server` enforces RBAC and action-level security on agent endpoints.
- Supply chain checks via Snyk/Dependabot.
   - No secret or credential in repo; use secrets manager.

## Monitoring, Alerts, and Troubleshooting
- Prometheus and Grafana preconfigured dashboards:
   - `agent-latency`, `task-throughput`, `error-rates` visible in `/infra/grafana_dashboards/`
- OpenTelemetry traces report to Grafana Cloud or your endpoint.
- Troubleshoot with `kubectl logs` and `kubectl describe pod`.
- To configure Slack/email alerts, see `docs/infra/alerting_setup.md`—keep alert tokens/URLs in secrets only.

## Backup & Recovery
- Database backups: nightly via cronjob, push to encrypted cloud bucket.
- Agent state and logs: snapshot volume every 6 hours.
- Restore using procedure in `/docs/infra/restore_guide.md`.

## Contact & Support
- Issues: [GitHub Issues](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues)
- Email: [contact@amas-team.org](mailto:contact@amas-team.org)
- Full roadmap: [PRODUCTION_ROADMAP.md](docs/PRODUCTION_ROADMAP.md)

---
