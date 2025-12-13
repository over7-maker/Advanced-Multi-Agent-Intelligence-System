# AMAS Deployment Guide

## Purpose
This guide describes how to deploy AMAS (Advanced Multi-Agent Intelligence System) in production and development environments.

---

## Requirements
- Docker v20+
- Docker Compose v2+
- Python 3.11+
- Node.js v18+ (for GUI)
- PostgreSQL 14+, Redis 7+
- Kubernetes 1.23+ (optional, for cloud-native deployment)

---

## Local Development (Docker Compose)
1. Copy `.env.example` to `.env` and configure secrets
2. Run:
   ```bash
   docker-compose up --build
   ```
3. Access UI at `http://localhost:3000`

---

## Production Deployment (Kubernetes)
- Apply all manifests in `k8s/`:
  ```bash
  kubectl apply -f k8s/
  ```
- Ensure secrets/configs are properly mounted
- Set minimum pod scale for API, orchestrator, workers

---

## Environment Configuration
- All integration secrets and config must go in environment variables or sealed secrets
- Example: `POSTGRES_URL`, `REDIS_URL`, `GITHUB_API_KEY`, etc

---

## Health Monitoring
- Built-in `/health` and `/ready` endpoints on all core services
- Kubernetes liveness/readiness probes recommended
- Alerts/monitoring setup recommended via Prometheus/Grafana

---

### Useful Commands
- Rebuild images:
  ```bash
  docker-compose build
  ```
- Check logs:
  ```bash
  docker-compose logs -f
  ```
- Run tests:
  ```bash
  pytest
  ```


_Last updated: November 15, 2025_