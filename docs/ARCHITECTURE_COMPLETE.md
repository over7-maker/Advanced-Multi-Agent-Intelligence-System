# AMAS - Complete Architecture Documentation

**Version**: 2.0.0  
**Last Updated**: January 25, 2025  
**Status**: Production Ready

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Component Relationships](#component-relationships)
4. [Data Flow](#data-flow)
5. [Integration Patterns](#integration-patterns)
6. [API Endpoints](#api-endpoints)
7. [Database Schema](#database-schema)
8. [Deployment Architecture](#deployment-architecture)

---

## System Overview

AMAS (Advanced Multi-Agent Intelligence System) is a production-ready, enterprise-grade AI platform that provides:

- **12 Specialized AI Agents** with full orchestration
- **16 AI Provider Fallback Chain** for maximum reliability
- **ML-Powered Task Prediction** and intelligent agent selection
- **Real-Time WebSocket Updates** for live progress tracking
- **Complete Database Persistence** with PostgreSQL
- **Multi-Level Caching** with Redis
- **Graph Analytics** with Neo4j
- **6 Platform Integrations** (GitHub, Slack, N8N, Notion, Jira, Salesforce)

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer (React)                      │
│  - Dashboard, Tasks, Agents, Integrations, System Health    │
│  - Real-time WebSocket connections                           │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/WebSocket
┌───────────────────────▼─────────────────────────────────────┐
│              Nginx Reverse Proxy (Production)                │
│  - SSL/TLS Termination                                      │
│  - Rate Limiting                                             │
│  - Load Balancing                                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                  API Layer (FastAPI)                        │
│  - Authentication & Authorization (JWT, OIDC, RBAC)         │
│  - Request Validation                                        │
│  - Error Handling                                            │
│  - Rate Limiting                                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│        Orchestration Layer (Unified Intelligence)           │
│  - Task Lifecycle Management                                 │
│  - ML-Powered Agent Selection                                │
│  - Parallel/Sequential Execution                             │
│  - Result Aggregation                                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│              Intelligence Manager (ML)                      │
│  - Task Outcome Prediction                                   │
│  - Agent Selection Optimization                             │
│  - Learning Engine (Continuous Improvement)                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│            Agent System (12 Specialized Agents)              │
│  - Security Expert Agent                                     │
│  - Intelligence Gathering Agent                              │
│  - Code Analysis Agent                                       │
│  - Performance Agent                                         │
│  - Documentation Agent                                       │
│  - Testing Agent                                             │
│  - Deployment Agent                                          │
│  - Monitoring Agent                                          │
│  - Data Agent                                                │
│  - API Agent                                                 │
│  - Research Agent                                            │
│  - Integration Agent                                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│      AI Provider Router (16 Providers + Fallback)           │
│  - Tier 1: Cerebras, NVIDIA, Groq (Premium Speed)           │
│  - Tier 2: DeepSeek, Codestral, GLM, Gemini, Grok           │
│  - Tier 3: Cohere (Enterprise)                               │
│  - Tier 4: Kimi, Qwen, GPT-OSS, Chutes (Fallbacks)          │
│  - Local: Ollama (phi3:3.8b)                                │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│              Database Layer                                  │
│  - PostgreSQL (Primary Storage)                              │
│  - Redis (Multi-Level Caching)                               │
│  - Neo4j (Graph Analytics)                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Relationships

### Core Components

1. **Unified Intelligence Orchestrator** (`src/amas/core/unified_intelligence_orchestrator.py`)
   - Initializes all 12 agents
   - Coordinates task execution
   - Aggregates results
   - Manages agent lifecycle

2. **AI Provider Router** (`src/amas/ai/enhanced_router_v2.py`)
   - 16 AI providers with automatic fallback
   - Circuit breaker pattern
   - Cost optimization
   - Performance tracking

3. **Intelligence Manager** (`src/amas/intelligence/intelligence_manager.py`)
   - ML-powered agent selection
   - Task outcome prediction
   - Learning engine integration

4. **Predictive Engine** (`src/amas/intelligence/predictive_engine.py`)
   - Task success probability
   - Duration estimation
   - Quality score prediction
   - Cost estimation

### Agent System

All 12 agents extend `BaseAgent` and use the AI router:

1. **SecurityExpertAgent** - Security analysis, vulnerability assessment
2. **IntelligenceGatheringAgent** - OSINT, intelligence collection
3. **CodeAnalysisAgent** - Code quality, security review
4. **PerformanceAgent** - Performance analysis, optimization
5. **DocumentationAgent** - Documentation generation
6. **TestingAgent** - Test generation, QA
7. **DeploymentAgent** - Deployment automation, DevOps
8. **MonitoringAgent** - System monitoring, observability
9. **DataAgent** - Data analysis, processing
10. **APIAgent** - API design, integration
11. **ResearchAgent** - Research, information synthesis
12. **IntegrationAgent** - Platform integrations

### Integration Platform

6 Platform Integrations (`src/amas/integration/`):

1. **GitHub Connector** - Repository management, PR/issue tracking
2. **Slack Connector** - Team communication, notifications
3. **N8N Connector** - Workflow automation
4. **Notion Connector** - Knowledge base integration
5. **Jira Connector** - Project management, issue tracking
6. **Salesforce Connector** - CRM integration

---

## Data Flow

### Task Creation Flow

```
User Request (Frontend)
    ↓
POST /api/v1/tasks
    ↓
[FastAPI] → Authentication → Validation
    ↓
[Intelligence Manager] → ML Prediction
    ↓
[Orchestrator] → Agent Selection (ML-Powered)
    ↓
[Database] → Persist Task (INSERT)
    ↓
[Cache] → Update Cache (Redis + Memory)
    ↓
[WebSocket] → Broadcast "task_created"
    ↓
[Background Task] → Auto-Execute (if enabled)
    ↓
Response to Frontend
```

### Task Execution Flow

```
Background Task Trigger
    ↓
[Orchestrator] → Get Task from Database
    ↓
[Orchestrator] → Execute with Selected Agents
    ↓
[Agent] → Call AI Router
    ↓
[AI Router] → Try Providers (Fallback Chain)
    ↓
[AI Provider] → Generate Response
    ↓
[Agent] → Process Response → Return Result
    ↓
[Orchestrator] → Aggregate Results
    ↓
[Database] → Update Task (result, output, quality_score)
    ↓
[Cache] → Update Cache
    ↓
[WebSocket] → Broadcast "task_completed" with full results
    ↓
[Learning Engine] → Record Execution for ML Improvement
```

### Task Retrieval Flow

```
GET /api/v1/tasks/{task_id}
    ↓
[FastAPI] → Authentication
    ↓
[Memory Cache] → Check Recently Accessed (5 min TTL)
    ↓ (if not found)
[Redis Cache] → Check Cache
    ↓ (if not found)
[Database] → SELECT from tasks table
    ↓
[Parse JSON] → result, output, agent_results
    ↓
[Update Cache] → Store in Memory + Redis
    ↓
Response to Frontend (with full results)
```

---

## Integration Patterns

### Agent-Orchestrator Integration

- All agents extend `BaseAgent`
- Orchestrator calls `agent.execute(task_id, target, parameters)`
- Agents use `self.ai_router.generate_with_fallback()` for AI calls
- Results are standardized format with `success`, `output`, `quality_score`

### AI Router Integration

- Agents never call AI providers directly
- Always use `EnhancedAIRouter.generate_with_fallback()`
- Automatic fallback through 16 providers
- Circuit breakers prevent cascading failures

### Database Integration

- Primary storage: PostgreSQL
- All tasks persisted with full results
- JSON fields: `result`, `output`, `execution_metadata`
- Indexes on: `task_id`, `status`, `created_at`, `task_type`, `created_by`

### Cache Integration

- Multi-level caching: Memory → Redis → Database
- Memory cache: 5 min TTL for recently accessed tasks
- Redis cache: Longer TTL for frequently accessed data
- Cache invalidation on updates

### WebSocket Integration

- Real-time updates for all task events
- Events: `task_created`, `task_execution_started`, `task_progress`, `agent_started`, `agent_completed`, `task_completed`, `task_failed`
- Subscription model: Clients subscribe to specific tasks
- Heartbeat mechanism for connection health

---

## API Endpoints

### Task Management

- `POST /api/v1/tasks` - Create task (with ML prediction)
- `GET /api/v1/tasks` - List tasks (with filtering, pagination)
- `GET /api/v1/tasks/{task_id}` - Get task details (with full results)
- `POST /api/v1/tasks/{task_id}/execute` - Execute task
- `GET /api/v1/tasks/{task_id}/progress` - Get task progress

### Agent Management

- `GET /api/v1/agents` - List all agents
- `GET /api/v1/agents/{agent_id}` - Get agent details
- `POST /api/v1/agents` - Create custom agent
- `GET /api/v1/agents/ai-providers` - List AI providers

### Integrations

- `GET /api/v1/integrations` - List integrations
- `POST /api/v1/integrations` - Create integration
- `POST /api/v1/integrations/{integration_id}/trigger` - Trigger integration
- `POST /api/v1/integrations/webhooks/{platform}` - Webhook endpoint

### Analytics

- `GET /api/v1/analytics/tasks` - Task analytics
- `GET /api/v1/analytics/agents` - Agent performance analytics

### System

- `GET /api/v1/system/metrics` - System metrics (Prometheus)
- `GET /api/v1/health` - Health check
- `GET /api/v1/ready` - Readiness check

### Predictions

- `POST /api/v1/predict/task` - Predict task outcome
- `GET /api/v1/predict/resources` - Predict resource requirements

---

## Database Schema

### Tasks Table

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    task_type VARCHAR(100) NOT NULL,
    target TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    parameters JSONB,
    assigned_agents JSONB DEFAULT '[]',
    result JSONB,                    -- Full execution result
    output JSONB,                     -- Agent results structure
    summary TEXT,                     -- Task summary
    quality_score NUMERIC(5,4),       -- Quality score (0.0-1.0)
    duration_seconds NUMERIC(10,2),   -- Execution duration
    success_rate NUMERIC(5,4),        -- Success rate (0.0-1.0)
    execution_metadata JSONB,         -- ML prediction data
    error_details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    created_by VARCHAR(255)
);

-- Indexes
CREATE INDEX ix_tasks_task_id ON tasks(task_id);
CREATE INDEX ix_tasks_status ON tasks(status);
CREATE INDEX ix_tasks_created_at ON tasks(created_at);
CREATE INDEX ix_tasks_quality_score ON tasks(quality_score);
CREATE INDEX ix_tasks_status_created_at ON tasks(status, created_at);
CREATE INDEX ix_tasks_task_type_status ON tasks(task_type, status);
CREATE INDEX ix_tasks_created_by_created_at ON tasks(created_by, created_at);
```

### Other Tables

- `users` - User accounts and authentication
- `agents` - Agent registry and capabilities
- `task_executions` - Detailed execution logs
- `integrations` - Platform integration configurations
- `ml_models` - ML model registry
- `ml_training_data` - Training data for ML models
- `api_keys` - API key management
- `audit_logs` - Audit trail
- `notifications` - Notification queue
- `system_config` - System configuration

---

## Deployment Architecture

### Production Stack (Docker Compose)

- **Application**: `amas-backend`, `nginx`
- **Database**: `postgres`, `redis`, `neo4j`
- **Monitoring**: `prometheus`, `grafana`, `jaeger`, `alertmanager`, `loki`, `promtail`
- **Exporters**: `node-exporter`, `cadvisor`, `postgres-exporter`, `redis-exporter`

### Kubernetes Deployment

- **Deployment**: 3+ replicas with HPA (3-10 replicas)
- **Service**: LoadBalancer/ClusterIP
- **Ingress**: Nginx ingress with SSL
- **ConfigMap**: Configuration management
- **Secret**: Sensitive data (API keys, passwords)
- **PVC**: Persistent volumes for databases

---

## Performance Targets

| Metric | Target | Critical |
|--------|--------|----------|
| API Response Time (p95) | < 200ms | < 500ms |
| Database Query Time (p95) | < 50ms | < 200ms |
| Task Execution Time | < 30s | < 60s |
| Frontend Load Time | < 2s | < 4s |
| WebSocket Latency | < 100ms | < 300ms |
| Cache Hit Rate | > 80% | > 60% |
| Error Rate | < 0.1% | < 1% |
| Uptime | > 99.9% | > 99.5% |

---

## Security Architecture

- **Authentication**: JWT tokens, OIDC support
- **Authorization**: RBAC with OPA policy engine
- **Encryption**: TLS/SSL for all communications
- **Secrets Management**: Environment variables, Kubernetes Secrets
- **Audit Logging**: Complete audit trail for all operations
- **Data Classification**: PII detection and redaction

---

## Monitoring & Observability

- **Prometheus Metrics**: 50+ metrics for tasks, agents, AI providers, system
- **Grafana Dashboards**: 7 dashboards for comprehensive monitoring
- **OpenTelemetry Tracing**: Distributed tracing for request flows
- **Structured Logging**: JSON logs with correlation IDs
- **Alert Rules**: 15+ alerts for critical issues

---

## Next Steps

For detailed component documentation, see:
- [COMPONENTS_COMPLETE.md](COMPONENTS_COMPLETE.md) - All components and capabilities
- [CAPABILITIES_COMPLETE.md](CAPABILITIES_COMPLETE.md) - System capabilities and usage

