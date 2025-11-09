# AMAS Deployment Guide

## Local Development
- Clone the repo, install with pip and npm in each major directory.
- Use `docker-compose up` for all core backend/frontend services.
- Dashboard default URL: [localhost:3000](http://localhost:3000)

## Production/Staging
- Complete configuration in `.env` and `k8s/` manifests
- Deploy with `kubectl apply -f k8s/foundation/` and `k8s/intelligence/`
- Set up cloud load balancer/DNS and SSL as needed
- Check all observability with provided Grafana/Prometheus dashboards

## Infrastructure
- Kubernetes-native, with complete horizontal scaling for all agent types
- OIDC/JWT auth for all APIs and GUI
- CI/CD and supply chain protection for deployments

## Monitoring and Recovery
- SLO-based OpenTelemetry tracing
- KEDA auto-scaling, ready for load spikes
- Alerts through Slack/email integration

## Reference Roadmap
Full step-by-step in [PRODUCTION_ROADMAP.md](docs/PRODUCTION_ROADMAP.md).
