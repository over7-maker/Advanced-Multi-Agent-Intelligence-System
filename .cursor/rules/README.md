# Cursor Project Rules

<!--
Version: 1.0.0
Author: Architecture Team
Effective: 2025-01-20
Status: Active
-->

> ⚠️ **Confidential**: This document contains proprietary architecture details. Do not distribute outside authorized personnel.

This directory contains Cursor project rules based on the AMAS Production Implementation Guide (PART_1, PART_2, PART_3, PART_4, PART_5, PART_6, PART_7, PART_8, PART_9, PART_10).

## Rules Overview

### Core Architecture Rules

#### 1. **amas-architecture-overview.mdc** (Always Apply)
- **Purpose**: Complete AMAS architecture reference, component relationships, data flow, and system structure
- **When**: Applied to all files in `src/**/*.py` and `frontend/src/**/*.tsx`
- **Key Rules**:
  - Follow documented architecture patterns
  - Prefer orchestrator for complex operations (allow bypass for high-throughput, low-complexity tasks)
  - Use AI router with fallback chain (16 providers available, use as needed)
  - Implement agents as required by use case (12 agents available)
  - Maintain performance targets (p95 < 200ms for API, < 30s for task execution)

#### 2. **integration-architecture.mdc** (Always Apply)
- **Purpose**: Enforces the complete integration architecture flow
- **When**: Applied to all files in `src/api/**/*.py` and `src/amas/**/*.py`
- **Key Rules**:
  - Prefer orchestrator for task execution (bypass only for latency-critical operations > 200ms)
  - Never use mock data in production code
  - Always use real integrations for external services
  - Log and alert when bypassing architectural layers

#### 3. **ai-orchestration-integration.mdc** (File-Specific)
- **Purpose**: Guides AI orchestration integration in task/workflow APIs
- **When**: Applied to `src/api/routes/tasks.py`, `src/api/routes/workflows.py`, orchestrator files
- **Key Rules**:
  - Use orchestrator for task execution
  - Include ML predictions for task creation
  - Use intelligent agent selection based on task type
  - Persist all tasks and results to database

#### 4. **ml-predictions-integration.mdc** (File-Specific)
- **Purpose**: Ensures ML predictions are used for all task creation
- **When**: Applied to predictive engine, prediction routes, and task routes
- **Key Rules**:
  - Predict task outcomes before execution
  - Include prediction data in task metadata
  - Record learning feedback after execution
  - Use predictions for agent selection and resource estimation

#### 5. **ai-provider-fallback.mdc** (File-Specific)
- **Purpose**: Enforces use of enhanced router with 16-provider fallback
- **When**: Applied to AI router, agent files, orchestrator
- **Key Rules**:
  - Never call AI providers directly - always use EnhancedAIRouter
  - Use router's automatic fallback chain (16 providers available)
  - Handle fallback gracefully with circuit breakers
  - Log provider attempts and failures for monitoring
  - Fallback to next provider if current provider fails (max 3 retries per tier)

#### 6. **websocket-realtime-updates.mdc** (File-Specific)
- **Purpose**: Ensures real-time updates via WebSocket
- **When**: Applied to WebSocket files and task/workflow routes
- **Key Rules**: Broadcast all task events, use proper event structure, handle subscriptions

#### 7. **agent-implementation.mdc** (File-Specific)
- **Purpose**: Guides proper agent implementation patterns
- **When**: Applied to all agent files in `src/amas/agents/**/*.py`
- **Key Rules**: Extend BaseAgent, implement required methods, use AI router

### Database & Persistence Rules

#### 8. **database-persistence.mdc** (File-Specific)
- **Purpose**: Production-grade database persistence with PostgreSQL, Redis, and Neo4j
- **When**: Applied to task/workflow routes, database files, and services
- **Key Rules**: Always use connection pool, persist tasks, use parameterized queries, cache appropriately

#### 9. **postgresql-connection-pooling.mdc** (File-Specific)
- **Purpose**: Production-grade async PostgreSQL connection pool management
- **When**: Applied to database connection files, API routes, and services
- **Key Rules**: Always use DatabaseConnectionPool, use transactions, implement health checks

#### 10. **redis-caching-strategy.mdc** (File-Specific)
- **Purpose**: Production-grade Redis caching with read-through, write-through, and stampede prevention
- **When**: Applied to Redis cache files, caching services, and API routes
- **Key Rules**: Use RedisCacheManager, implement read-through/write-through, use appropriate TTL

#### 11. **neo4j-graph-database.mdc** (File-Specific)
- **Purpose**: Neo4j graph database for task dependencies, agent relationships, and analytics
- **When**: Applied to Neo4j connection files, services, and orchestrator
- **Key Rules**: Use Neo4jConnectionManager, track relationships, use graph analytics

#### 12. **database-migrations.mdc** (File-Specific)
- **Purpose**: Alembic migration patterns and schema evolution best practices
- **When**: Applied to Alembic migration files and database scripts
- **Key Rules**: Always write downgrade, test migrations, use proper schema patterns

#### 13. **caching-service-patterns.mdc** (File-Specific)
- **Purpose**: Domain-specific caching services (tasks, agents, predictions)
- **When**: Applied to caching service files and API routes
- **Key Rules**: Use cache services, implement read-through/write-through, invalidate appropriately

### Platform Integration Rules

#### 14. **platform-integrations.mdc** (File-Specific)
- **Purpose**: Integration Manager, connector patterns, webhook handling, and 100+ platform support
- **When**: Applied to integration manager, connector files, and integration API routes
- **Key Rules**: Always use IntegrationManager, validate credentials, validate webhook signatures, handle errors gracefully

#### 15. **integration-connectors.mdc** (File-Specific)
- **Purpose**: Connector implementation patterns, credential validation, and platform-specific operations
- **When**: Applied to connector implementation files
- **Key Rules**: Implement all required methods, validate credentials, validate webhook signatures, use circuit breakers

### Monitoring & Observability Rules

#### 16. **monitoring-observability.mdc** (File-Specific)
- **Purpose**: Complete monitoring and observability patterns (Prometheus, OpenTelemetry, logging)
- **When**: Applied to monitoring services, tracing services, and middleware
- **Key Rules**: Use PrometheusMetricsService, use TracingService, use structured logging, record metrics for all operations

#### 17. **prometheus-metrics.mdc** (File-Specific)
- **Purpose**: Prometheus metrics patterns, naming conventions, and recording best practices
- **When**: Applied to services and API routes that need metrics
- **Key Rules**: Use appropriate metric types, follow naming conventions, use labels correctly, record metrics for critical operations

#### 18. **opentelemetry-tracing.mdc** (File-Specific)
- **Purpose**: OpenTelemetry distributed tracing patterns and instrumentation
- **When**: Applied to orchestrator, agents, and API routes
- **Key Rules**: Create spans for operations, add context attributes, record exceptions, use child spans

#### 19. **structured-logging.mdc** (File-Specific)
- **Purpose**: Structured JSON logging patterns and log aggregation
- **When**: Applied to all Python files
- **Key Rules**: Use JSON logging, add context to logs, use appropriate log levels, don't log sensitive data

### Frontend Rules

#### 20. **frontend-api-service.mdc** (File-Specific)
- **Purpose**: Frontend API service with Axios, authentication, error handling, and all endpoint methods
- **When**: Applied to frontend API service files and components using API
- **Key Rules**: Use APIService singleton, handle authentication, use TypeScript interfaces, handle errors gracefully

#### 21. **frontend-websocket-service.mdc** (File-Specific)
- **Purpose**: Production-ready WebSocket client with reconnection, heartbeat, and event handling
- **When**: Applied to frontend WebSocket service files and components using WebSocket
- **Key Rules**: Implement reconnection with exponential backoff, use heartbeat, subscribe/unsubscribe properly, handle errors

#### 22. **react-component-patterns.mdc** (File-Specific)
- **Purpose**: React component patterns with TypeScript, hooks, Material-UI, and real-time updates
- **When**: Applied to all React component files
- **Key Rules**: Use TypeScript, functional components with hooks, Material-UI components, handle loading/error states, subscribe to WebSocket events

#### 23. **frontend-routing-authentication.mdc** (File-Specific)
- **Purpose**: React Router patterns, protected routes, and authentication flow
- **When**: Applied to App.tsx, routing files, and authentication components
- **Key Rules**: Protect routes with authentication, use React Router, handle login/logout, connect WebSocket after auth

### Production Deployment Rules

#### 24. **docker-production.mdc** (File-Specific)
- **Purpose**: Docker production configuration with multi-stage builds, security, and optimization
- **When**: Applied to Dockerfile and docker-compose files
- **Key Rules**: Use multi-stage builds, run as non-root, include health checks, optimize image size

#### 25. **kubernetes-deployment.mdc** (File-Specific)
- **Purpose**: Kubernetes deployment manifests, HPA, services, ingress, and best practices
- **When**: Applied to Kubernetes manifest files
- **Key Rules**: Set resource limits, use ConfigMaps/Secrets, configure HPA, enable TLS, add health checks

#### 26. **cicd-pipeline.mdc** (File-Specific)
- **Purpose**: CI/CD pipeline patterns with GitHub Actions, testing, building, and deployment
- **When**: Applied to GitHub Actions workflow files
- **Key Rules**: Run tests before build, use service containers, cache dependencies, deploy conditionally

#### 27. **production-security.mdc** (File-Specific)
- **Purpose**: Production security including authentication, encryption, secrets management, and hardening
- **When**: Applied to security-related files, Nginx configs, and authentication code
- **Key Rules**: Use strong passwords, enable HTTPS, validate inputs, use parameterized queries, encrypt sensitive data

#### 28. **database-migrations-backup.mdc** (File-Specific)
- **Purpose**: Database migrations with Alembic, backup scripts, and disaster recovery procedures
- **When**: Applied to Alembic migration files and backup/restore scripts
- **Key Rules**: Always write downgrade, test migrations, backup before migration, verify backups, automate backups

### Production Deployment & Checklist Rules

#### 29. **production-deployment-checklist.mdc** (File-Specific)
- **Purpose**: Production deployment checklist, pre-deployment, deployment day, and post-deployment procedures
- **When**: Applied to deployment scripts, checklist documentation, and quick start guides
- **Key Rules**: Always backup before deployment, run pre-flight checks, verify health checks, test after deployment, have rollback plan

#### 30. **docker-compose-production.mdc** (File-Specific)
- **Purpose**: Complete Docker Compose production stack with all services, resource limits, health checks, and monitoring
- **When**: Applied to docker-compose.prod.yml and production compose files
- **Key Rules**: Use health checks, set resource limits, separate networks, use named volumes, configure dependencies properly

#### 31. **project-structure-consistency.mdc** (File-Specific)
- **Purpose**: Enforce correct file locations, naming conventions, and directory structure
- **When**: Applied to all files in the project
- **Key Rules**: Follow documented structure, use correct naming conventions, place files in correct directories, maintain separation of concerns

## How Rules Work

### Rule Types

1. **Always Apply** (`alwaysApply: true`):
   - Applied to every chat session
   - Example: `integration-architecture.mdc`

2. **Apply Intelligently** (`alwaysApply: false`, with `description`):
   - Applied when Cursor determines it's relevant
   - Based on file context and description

3. **Apply to Specific Files** (`globs` specified):
   - Applied when working with files matching the glob patterns
   - Example: `ai-orchestration-integration.mdc` applies to task/workflow routes

### Using Rules

- Rules are automatically applied based on context
- You can manually reference rules using `@rule-name` in chat
- Rules provide code examples and patterns to follow
- Rules help prevent common mistakes (mock data, bypassing orchestrator, etc.)

## Rule Format (MDC)

Each rule file uses the MDC (Markdown with Metadata) format:

```markdown
---
description: Brief description of what the rule helps with
globs:
  - "path/pattern/**/*.py"  # Files this applies to
alwaysApply: true/false     # Whether to always apply
---

# Rule Title

Rule content with code examples, patterns, and guidelines...
```

## Key Principles Enforced

1. **Complete Integration**: Prefer orchestrator for complex operations; allow bypass for latency-critical paths (> 200ms)
2. **Real Data**: Never return mock data in production - always use real orchestrator/agents
3. **ML Intelligence**: Use predictions for task creation when available; fallback gracefully if predictions fail
4. **Provider Fallback**: Use enhanced router with 16-provider fallback chain; circuit breakers prevent cascading failures
5. **Real-Time Updates**: Broadcast WebSocket events for all task/agent state changes
6. **Persistence**: Store all tasks and results in database with proper transaction handling
7. **Learning Loop**: Record execution results for ML improvement; use feedback to refine predictions

## Adding New Rules

To add a new rule:

1. Create a new `.mdc` file in `.cursor/rules/`
2. Add metadata header with description, globs, and alwaysApply
3. Write clear, actionable guidelines with code examples
4. Reference existing code patterns when possible

## References

- [Cursor Rules Documentation](https://cursor.com/docs/context/rules#project-rules)
- AMAS Production Implementation Guide:
  - PART_1.md: Core AI Orchestration Integration
  - PART_2.MD: ML Predictions Integration
  - PART_3.MD: AI Provider Fallback System
  - PART_4.MD: Database Full Integration (PostgreSQL, Redis, Neo4j)
  - PART_5.MD: Platform Integrations (N8N, Slack, GitHub, Salesforce, Notion, Jira)
  - PART_6.MD: Monitoring & Observability (Prometheus, Grafana, OpenTelemetry, Loki)
  - PART_7.MD: Frontend Complete Integration (React, TypeScript, Material-UI, WebSocket)
  - PART_8.MD: Production Deployment (Docker, Kubernetes, CI/CD, Security, Backup)
  - PART_9.MD: Production Docker Compose (Complete Stack, Monitoring, Exporters)
  - PART_10.MD: Production Checklist (Pre-deployment, Deployment Day, Post-deployment)
  - COMPREHENSIVE FINAL SUMMARY.md: Complete architecture overview, project structure, and system reference

