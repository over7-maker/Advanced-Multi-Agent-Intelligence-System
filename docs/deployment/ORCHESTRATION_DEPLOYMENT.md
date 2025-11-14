# 🎯 Orchestration System Deployment Guide

**Complete deployment guide for the Hierarchical Agent Orchestration System**

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Deployment Architecture](#deployment-architecture)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Docker Compose Deployment](#docker-compose-deployment)
- [Configuration](#configuration)
- [Health Checks](#health-checks)
- [Scaling Configuration](#scaling-configuration)
- [Monitoring & Observability](#monitoring--observability)
- [Security Configuration](#security-configuration)
- [Validation & Testing](#validation--testing)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Hierarchical Agent Orchestration System is the keystone component that enables autonomous multi-agent coordination. This guide provides comprehensive deployment instructions for production environments.

### Key Components

- **Task Decomposer**: AI-powered task breakdown (1,132 lines)
- **Agent Hierarchy Manager**: Multi-layer agent management (999 lines)
- **Agent Communication Bus**: Inter-agent messaging (1,084 lines)
- **Workflow Executor**: Multi-agent workflow execution (1,113 lines)
- **Supporting Components**: Configuration, utilities, health checks, REST API

### Performance Requirements

- **Task Decomposition**: <2 minutes for complex tasks
- **Agent Assignment**: <30 seconds for 10+ specialists
- **Communication Latency**: <100ms for inter-agent messages
- **Failure Recovery**: <30 seconds to replace failed agents
- **Scalability**: 100+ concurrent workflows, 500+ agents, 10,000+ messages/minute

---

## Prerequisites

### Infrastructure Requirements

- **Kubernetes**: 1.28+ with KEDA and OPA controllers
- **Database**: PostgreSQL 15+ (for workflow state persistence)
- **Cache**: Redis 7+ (for message bus and agent state)
- **Graph Database**: Neo4j 5+ (for knowledge graph and agent relationships)
- **Monitoring**: Prometheus + Grafana (for metrics and dashboards)
- **Tracing**: OpenTelemetry collector (for distributed tracing)

### Resource Requirements

**Per Orchestration Pod**:
- CPU: 1-4 cores (request: 1000m, limit: 4000m)
- Memory: 2-8 GB (request: 2Gi, limit: 8Gi)
- Storage: 20GB for data, 10GB for logs

**Cluster Minimum**:
- 3 orchestration pods (for high availability)
- Total: 6-24 CPU cores, 6-24 GB RAM

---

## Deployment Architecture

### 4-Layer Architecture

```
┌────────────── 🎯 EXECUTIVE LAYER ───────────────┐
│        Task Coordinator & Quality Supervisor         │
│ • Decompose complex tasks into specialist workflows│
│ • Monitor progress across all coordination layers  │
│ • Make final delivery decisions and approvals     │
└────────────────────────────────────────────────┘
                            ↓
┌────────────── 👥 MANAGEMENT LAYER ──────────────┐
│         Specialist Team Coordinators             │
│ Research Lead | Analysis Lead | Creative Lead | QA Lead│
│ Technical Lead | Integration Lead                 │
│ • Plan team strategies and coordinate execution   │
└────────────────────────────────────────────────┘
                            ↓
┌────────────── 🔬 SPECIALIST LAYER ───────────────┐
│              Domain Expert Agents               │
│ 20+ Specialists: Research, Analysis, Creative, QA │
│ • Execute domain-specific tasks with expertise   │
└────────────────────────────────────────────────┘
                            ↓
┌─────────────── ⚙️ EXECUTION LAYER ───────────────┐
│            Tool & Utility Agents               │
│ Tool Manager | API Gateway | Task Scheduler     │
│ • Execute low-level tool and system operations   │
└────────────────────────────────────────────────┘
```

### Deployment Components

1. **Orchestration Service**: Main orchestration engine (3+ replicas)
2. **Database**: PostgreSQL for workflow state
3. **Cache**: Redis for message bus and agent state
4. **Graph DB**: Neo4j for agent relationships
5. **Monitoring**: Prometheus + Grafana for observability

---

## Kubernetes Deployment

### Step 1: Create Namespace

```bash
kubectl create namespace amas
```

### Step 2: Deploy Foundation Services

Deploy foundation services first (PostgreSQL, Redis, Neo4j):

```bash
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/neo4j.yaml
```

Wait for foundation services to be ready:

```bash
kubectl wait --for=condition=ready pod -l app=postgres -n amas --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n amas --timeout=300s
kubectl wait --for=condition=ready pod -l app=neo4j -n amas --timeout=300s
```

### Step 3: Create Secrets

Create Kubernetes secrets for sensitive data:

```bash
kubectl create secret generic amas-secrets \
  --from-literal=POSTGRES_PASSWORD='your-secure-password' \
  --from-literal=REDIS_PASSWORD='your-secure-password' \
  --from-literal=NEO4J_PASSWORD='your-secure-password' \
  --from-literal=SECRET_KEY='your-secret-key' \
  -n amas
```

### Step 4: Deploy Configuration

Deploy orchestration configuration:

```bash
kubectl apply -f k8s/orchestration-configmap.yaml
```

### Step 5: Deploy Orchestration Service

Deploy the orchestration service:

```bash
kubectl apply -f k8s/orchestration-deployment.yaml
```

Verify deployment:

```bash
kubectl get pods -l component=orchestration -n amas
kubectl get svc amas-orchestration -n amas
```

### Step 6: Deploy Autoscaling

Deploy Horizontal Pod Autoscaler:

```bash
kubectl apply -f k8s/orchestration-hpa.yaml
```

Verify HPA:

```bash
kubectl get hpa amas-orchestration-hpa -n amas
```

### Step 7: Deploy Monitoring

Deploy ServiceMonitor for Prometheus:

```bash
kubectl apply -f k8s/servicemonitor.yaml
```

---

## Docker Compose Deployment

### Local Development

For local development, use `docker-compose.dev.yml`:

```bash
docker-compose -f docker-compose.dev.yml up -d
```

### Production-like Environment

For production-like testing:

```bash
docker-compose up -d
```

### Environment Variables

Create `.env` file with orchestration configuration:

```bash
# Orchestration Configuration
ORCHESTRATION_MAX_AGENTS_PER_POOL=5
ORCHESTRATION_MAX_TASKS_PER_AGENT=3
ORCHESTRATION_HEARTBEAT_INTERVAL=60
ORCHESTRATION_MAX_AGENT_SPAWN_RATE=10

# Task Decomposition
ORCHESTRATION_DECOMPOSITION_TIMEOUT=120.0
ORCHESTRATION_MAX_SUBTASKS=50

# Communication
ORCHESTRATION_MESSAGE_TIMEOUT=300.0
ORCHESTRATION_MESSAGE_RETRIES=3
ORCHESTRATION_MESSAGE_BACKLOG_WARNING=1000
ORCHESTRATION_MESSAGE_BACKLOG_CRITICAL=5000

# Workflow Execution
ORCHESTRATION_WORKFLOW_TIMEOUT=24.0
ORCHESTRATION_QUALITY_THRESHOLD=0.85
ORCHESTRATION_MAX_WORKFLOWS=100
ORCHESTRATION_MAX_TOTAL_AGENTS=500

# Performance
ORCHESTRATION_ENABLE_CACHE=true
ORCHESTRATION_ENABLE_METRICS=true

# Observability
ORCHESTRATION_LOG_LEVEL=INFO
ORCHESTRATION_ENABLE_TRACING=true

# Error Handling
ORCHESTRATION_ENABLE_CIRCUIT_BREAKER=true
ORCHESTRATION_RETRY_ATTEMPTS=3
```

---

## Configuration

### Environment Variables

See [Configuration Guide](../ORCHESTRATION_SYSTEM.md#configuration) for complete list of configuration options.

### Key Configuration Parameters

**Agent Management**:
- `ORCHESTRATION_MAX_AGENTS_PER_POOL`: Maximum agents per specialty pool (default: 5)
- `ORCHESTRATION_MAX_TASKS_PER_AGENT`: Maximum concurrent tasks per agent (default: 3)
- `ORCHESTRATION_MAX_AGENT_SPAWN_RATE`: Maximum agents spawned per second (default: 10)

**Message Bus**:
- `ORCHESTRATION_MESSAGE_BACKLOG_WARNING`: Warning threshold for message backlog (default: 1000)
- `ORCHESTRATION_MESSAGE_BACKLOG_CRITICAL`: Critical threshold for message backlog (default: 5000)

**Workflow Limits**:
- `ORCHESTRATION_MAX_WORKFLOWS`: Maximum concurrent workflows (default: 100)
- `ORCHESTRATION_MAX_TOTAL_AGENTS`: Maximum total agents (default: 500)

---

## Health Checks

### Kubernetes Health Checks

The orchestration service includes three health check endpoints:

1. **Liveness Probe**: `/health/orchestration`
   - Checks if the service is alive
   - Failure triggers pod restart

2. **Readiness Probe**: `/ready/orchestration`
   - Checks if the service is ready to accept traffic
   - Failure removes pod from service endpoints

3. **Startup Probe**: `/health/orchestration`
   - Checks if the service has started
   - Allows longer startup time for initialization

### Health Check Configuration

```yaml
livenessProbe:
  httpGet:
    path: /health/orchestration
    port: 8000
  initialDelaySeconds: 90
  periodSeconds: 30
  timeoutSeconds: 10
  failureThreshold: 5

readinessProbe:
  httpGet:
    path: /ready/orchestration
    port: 8000
  initialDelaySeconds: 45
  periodSeconds: 10
  timeoutSeconds: 10
  failureThreshold: 3
```

### Manual Health Check

```bash
# Check orchestration health
curl http://localhost:8000/health/orchestration

# Check readiness
curl http://localhost:8000/ready/orchestration
```

---

## Scaling Configuration

### Horizontal Pod Autoscaling

The orchestration service uses HPA with multiple metrics:

**Resource Metrics**:
- CPU: 70% utilization target
- Memory: 80% utilization target

**Custom Metrics**:
- Active workflows: 10 per pod
- Message queue depth: 1000 per pod
- Active agents: 50 per pod

**Scaling Behavior**:
- Scale Up: 50% increase or 3 pods per minute (max)
- Scale Down: 10% decrease or 1 pod per minute (min)
- Stabilization: 60s for scale up, 300s for scale down

### Manual Scaling

```bash
# Scale to specific replica count
kubectl scale deployment amas-orchestration --replicas=5 -n amas

# Check current scaling status
kubectl get hpa amas-orchestration-hpa -n amas
```

---

## Monitoring & Observability

### Metrics

The orchestration service exposes Prometheus metrics at `/metrics`:

**Key Metrics**:
- `orchestration_active_workflows`: Number of active workflows
- `orchestration_active_agents`: Number of active agents
- `orchestration_message_queue_depth`: Message queue depth
- `orchestration_task_decomposition_duration`: Task decomposition duration
- `orchestration_agent_assignment_duration`: Agent assignment duration
- `orchestration_message_latency`: Inter-agent message latency
- `orchestration_failure_recovery_duration`: Failure recovery duration

### Grafana Dashboards

Import orchestration dashboards:

```bash
kubectl apply -f k8s/grafana-dashboard.yaml
```

Dashboard includes:
- Workflow execution metrics
- Agent activity metrics
- Message bus metrics
- Performance benchmarks
- Error rates and recovery times

### Distributed Tracing

OpenTelemetry traces are automatically collected. View traces in Grafana Cloud or your tracing backend.

---

## Security Configuration

### Authentication & Authorization

- **Agent Authentication**: JWT/OIDC via security layer
- **Message Authentication**: All inter-agent messages authenticated
- **Role-Based Access Control**: Through agent hierarchy

### Network Security

- **Service Mesh**: Use Istio or Linkerd for mTLS between services
- **Network Policies**: Restrict pod-to-pod communication
- **Ingress**: Use TLS termination at ingress

### Secrets Management

- **Kubernetes Secrets**: Store sensitive data in Kubernetes secrets
- **External Secrets**: Use External Secrets Operator for cloud secret managers
- **Rotation**: Rotate secrets regularly (recommended: every 90 days)

---

## Validation & Testing

### Deployment Validation

1. **Check Pod Status**:
```bash
kubectl get pods -l component=orchestration -n amas
```

2. **Check Service Endpoints**:
```bash
kubectl get endpoints amas-orchestration -n amas
```

3. **Check Health**:
```bash
kubectl exec -it deployment/amas-orchestration -n amas -- \
  curl http://localhost:8000/health/orchestration
```

4. **Check Metrics**:
```bash
kubectl port-forward svc/amas-orchestration 9090:9090 -n amas
curl http://localhost:9090/metrics
```

### Functional Testing

1. **Test Task Decomposition**:
```python
from amas.orchestration import get_task_decomposer

decomposer = get_task_decomposer()
workflow = await decomposer.decompose_task(
    "Research AI market trends and create presentation"
)
assert workflow.complexity in ['MODERATE', 'COMPLEX']
```

2. **Test Workflow Execution**:
```python
from amas.orchestration import get_workflow_executor

executor = get_workflow_executor()
execution_id = await executor.execute_workflow(
    "Research competitor pricing and create report"
)
status = executor.get_execution_status(execution_id)
assert status['status'] in ['running', 'completed']
```

3. **Test Agent Communication**:
```python
from amas.orchestration import get_communication_bus, MessageType, Priority

bus = get_communication_bus()
message_id = await bus.send_message(
    sender_id="agent_1",
    recipient_id="agent_2",
    message_type=MessageType.SHARE_FINDINGS,
    payload={"data": "test"},
    priority=Priority.NORMAL
)
assert message_id is not None
```

### Performance Testing

Run load tests to validate performance benchmarks:

```bash
# Install k6
brew install k6  # macOS
# or
apt-get install k6  # Linux

# Run load test
k6 run scripts/load-test-orchestration.js
```

---

## Troubleshooting

### Common Issues

**Issue**: Orchestration pods not starting

**Solution**:
```bash
# Check pod logs
kubectl logs -l component=orchestration -n amas

# Check pod events
kubectl describe pod <pod-name> -n amas

# Check dependencies
kubectl get pods -n amas
```

**Issue**: High message queue depth

**Solution**:
```bash
# Check message backlog
kubectl exec -it deployment/amas-orchestration -n amas -- \
  python -c "from amas.orchestration import get_communication_bus; \
  bus = get_communication_bus(); \
  metrics = await bus.get_communication_metrics(); \
  print(metrics)"

# Scale up if needed
kubectl scale deployment amas-orchestration --replicas=5 -n amas
```

**Issue**: Agent assignment failures

**Solution**:
```bash
# Check agent pool status
kubectl exec -it deployment/amas-orchestration -n amas -- \
  python -c "from amas.orchestration import get_hierarchy_manager; \
  hierarchy = get_hierarchy_manager(); \
  status = hierarchy.get_hierarchy_status(); \
  print(status)"
```

### Debug Mode

Enable debug logging:

```bash
kubectl set env deployment/amas-orchestration \
  ORCHESTRATION_LOG_LEVEL=DEBUG -n amas
```

---

## Next Steps

After successful deployment:

1. **Monitor Metrics**: Set up Grafana dashboards and alerts
2. **Load Testing**: Run performance tests to validate benchmarks
3. **Integration Testing**: Test integration with other AMAS components
4. **Documentation**: Update team documentation with deployment details
5. **Training**: Train operations team on orchestration system

---

## Related Documentation

- [Orchestration System Guide](../ORCHESTRATION_SYSTEM.md)
- [Orchestration Quick Start](../ORCHESTRATION_QUICK_START.md)
- [Main Deployment Guide](../../DEPLOYMENT.md)
- [Security Guide](../../SECURITY.md)
- [Monitoring Guide](../MONITORING_GUIDE.md)

---

## Support

For deployment issues:
- GitHub Issues: [Create an issue](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues)
- Documentation: See [Orchestration System Guide](../ORCHESTRATION_SYSTEM.md)
- Email: support@amas-team.org
