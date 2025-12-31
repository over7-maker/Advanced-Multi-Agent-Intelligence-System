# AMAS - Complete Components Documentation

**Version**: 2.0.0  
**Last Updated**: January 25, 2025

---

## Table of Contents

1. [Agents (12 Specialized Agents)](#agents-12-specialized-agents)
2. [Services (Core Services)](#services-core-services)
3. [Integrations (6 Platform Integrations)](#integrations-6-platform-integrations)
4. [AI Providers (16 Providers)](#ai-providers-16-providers)
5. [Database Layer](#database-layer)
6. [API Layer](#api-layer)
7. [Frontend Components](#frontend-components)

---

## Agents (12 Specialized Agents)

All agents extend `BaseAgent` and use the AI router for execution.

### 1. SecurityExpertAgent
- **File**: `src/amas/agents/security_expert_agent.py`
- **Capabilities**:
  - Vulnerability assessment
  - Security auditing
  - Penetration testing
  - Threat analysis
  - OWASP Top 10 detection
  - SSL/TLS analysis
  - Security headers review
- **Task Types**: `security_scan`, `security_audit`, `vulnerability_assessment`, `penetration_testing`, `threat_analysis`
- **Integration**: Uses AI router with quality_first strategy

### 2. IntelligenceGatheringAgent
- **File**: `src/amas/agents/intelligence_gathering_agent.py`
- **Capabilities**:
  - OSINT collection
  - Web scraping
  - Domain analysis
  - Social media monitoring
  - Technology monitoring
  - Dark web monitoring
- **Task Types**: `intelligence_gathering`, `osint_investigation`, `osint_collection`, `social_media_monitoring`, `technology_monitoring`
- **Integration**: Uses AI router for intelligence synthesis

### 3. CodeAnalysisAgent
- **File**: `src/amas/agents/code_analysis_agent.py`
- **Capabilities**:
  - Code quality analysis
  - Security code review
  - Code refactoring suggestions
  - Best practices enforcement
- **Task Types**: `code_analysis`, `code_review`, `code_quality`, `security_code_review`
- **Integration**: Analyzes code repositories and provides recommendations

### 4. PerformanceAgent
- **File**: `src/amas/agents/performance_agent.py`
- **Capabilities**:
  - Performance analysis
  - Bottleneck identification
  - Optimization recommendations
  - Resource usage monitoring
- **Task Types**: `performance_analysis`, `performance_monitoring`, `performance_optimization`, `bottleneck_analysis`
- **Integration**: Monitors and optimizes system performance

### 5. DocumentationAgent
- **File**: `src/amas/agents/documentation_agent.py`
- **Capabilities**:
  - Documentation generation
  - API documentation
  - Code documentation
  - User guides
- **Task Types**: `documentation`, `documentation_generation`, `api_documentation`
- **Integration**: Generates comprehensive documentation

### 6. TestingAgent
- **File**: `src/amas/agents/testing_agent.py`
- **Capabilities**:
  - Test generation
  - Test coordination
  - QA automation
  - Test coverage analysis
- **Task Types**: `testing`, `testing_coordination`, `test_generation`, `qa`
- **Integration**: Automates testing workflows

### 7. DeploymentAgent
- **File**: `src/amas/agents/deployment_agent.py`
- **Capabilities**:
  - Deployment automation
  - CI/CD integration
  - DevOps workflows
  - Infrastructure as Code
- **Task Types**: `deployment`, `ci_cd`, `devops`
- **Integration**: Manages deployment processes

### 8. MonitoringAgent
- **File**: `src/amas/agents/monitoring_agent.py`
- **Capabilities**:
  - System monitoring
  - Observability setup
  - Metrics collection
  - Alerting configuration
- **Task Types**: `monitoring`, `observability`, `metrics_setup`
- **Integration**: Sets up comprehensive monitoring

### 9. DataAgent
- **File**: `src/amas/agents/data_agent.py`
- **Capabilities**:
  - Data analysis
  - Statistical analysis
  - Data processing
  - Data visualization
- **Task Types**: `data_analysis`, `statistical_analysis`, `data_processing`
- **Integration**: Processes and analyzes data

### 10. APIAgent
- **File**: `src/amas/agents/api_agent.py`
- **Capabilities**:
  - API design
  - API integration
  - REST API development
  - API testing
- **Task Types**: `api_design`, `api_integration`, `rest_api`
- **Integration**: Designs and integrates APIs

### 11. ResearchAgent
- **File**: `src/amas/agents/research_agent.py`
- **Capabilities**:
  - Research synthesis
  - Technology evaluation
  - Information gathering
  - Analysis and reporting
- **Task Types**: `research`, `technology_research`, `evaluation`
- **Integration**: Conducts research and provides insights

### 12. IntegrationAgent
- **File**: `src/amas/agents/integration_agent.py`
- **Capabilities**:
  - Platform integration
  - Connector development
  - Integration testing
  - Workflow automation
- **Task Types**: `integration`, `platform_integration`, `connector`
- **Integration**: Manages platform integrations

---

## Services (Core Services)

### AI/ML Services

1. **EnhancedAIRouter** (`src/amas/ai/enhanced_router_v2.py`)
   - 16 AI providers with automatic fallback
   - Circuit breaker pattern
   - Cost optimization
   - Performance tracking

2. **IntelligenceManager** (`src/amas/intelligence/intelligence_manager.py`)
   - ML-powered agent selection
   - Task outcome prediction
   - Learning engine integration

3. **PredictiveEngine** (`src/amas/intelligence/predictive_engine.py`)
   - Task success probability
   - Duration estimation
   - Quality score prediction

### Infrastructure Services

4. **DatabaseService** (`src/amas/services/database_service.py`)
   - PostgreSQL connection pooling
   - Query optimization
   - Transaction management

5. **VectorService** (`src/amas/services/vector_service.py`)
   - FAISS embeddings
   - Semantic search
   - Vector storage

6. **KnowledgeGraphService** (`src/amas/services/knowledge_graph_service.py`)
   - Neo4j integration
   - Relationship mapping
   - Graph analytics

### Caching Services

7. **TaskCacheService** (`src/amas/services/task_cache_service.py`)
   - Task result caching
   - Cache invalidation
   - TTL management

8. **AgentCacheService** (`src/amas/services/agent_cache_service.py`)
   - Agent performance caching
   - Cache optimization

9. **PredictionCacheService** (`src/amas/services/prediction_cache_service.py`)
   - ML prediction caching
   - Cache hit optimization

10. **SemanticCacheService** (`src/amas/services/semantic_cache_service.py`)
    - Semantic similarity caching
    - Duplicate request detection

### Monitoring Services

11. **PrometheusMetricsService** (`src/amas/services/prometheus_metrics_service.py`)
    - 50+ metrics collection
    - Performance tracking
    - Cost monitoring

12. **TracingService** (`src/amas/services/tracing_service.py`)
    - OpenTelemetry integration
    - Distributed tracing
    - Span management

13. **EnhancedLoggingService** (`src/amas/services/enhanced_logging_service.py`)
    - Structured logging
    - Security redaction
    - Correlation IDs

### Security Services

14. **SecurityService** (`src/amas/services/security_service.py`)
    - Authentication
    - Authorization
    - Encryption

15. **RateLimitingService** (`src/amas/services/rate_limiting_service.py`)
    - Sliding window algorithm
    - Redis-backed rate limiting
    - Per-user limits

### Other Services

16. **CircuitBreakerService** (`src/amas/services/circuit_breaker_service.py`)
    - Circuit breaker pattern
    - Failure detection
    - Automatic recovery

17. **CostTrackingService** (`src/amas/services/cost_tracking_service.py`)
    - AI provider cost tracking
    - Budget management
    - Cost optimization

---

## Integrations (6 Platform Integrations)

All integrations located in `src/amas/integration/`:

### 1. GitHub Connector
- **File**: `src/amas/integration/github_connector.py`
- **Capabilities**:
  - Repository management
  - PR/issue tracking
  - Webhook handling
  - Commit analysis
- **Integration**: OAuth2 authentication, GitHub API v4

### 2. Slack Connector
- **File**: `src/amas/integration/slack_connector.py`
- **Capabilities**:
  - Team communication
  - Notifications
  - Channel management
  - Message posting
- **Integration**: Slack Web API, OAuth2

### 3. N8N Connector
- **File**: `src/amas/integration/n8n_connector.py`
- **Capabilities**:
  - Workflow automation
  - Workflow execution
  - Webhook triggers
- **Integration**: N8N API, HTTP webhooks

### 4. Notion Connector
- **File**: `src/amas/integration/notion_connector.py`
- **Capabilities**:
  - Knowledge base integration
  - Page creation/updates
  - Database queries
- **Integration**: Notion API, OAuth2

### 5. Jira Connector
- **File**: `src/amas/integration/jira_connector.py`
- **Capabilities**:
  - Issue tracking
  - Project management
  - Workflow automation
- **Integration**: Jira REST API, OAuth2

### 6. Salesforce Connector
- **File**: `src/amas/integration/salesforce_connector.py`
- **Capabilities**:
  - CRM integration
  - Lead management
  - Opportunity tracking
- **Integration**: Salesforce REST API, OAuth2

---

## AI Providers (16 Providers)

### Tier 1 - Premium Speed & Quality
1. **Cerebras** - `qwen-3-235b-a22b-instruct-2507` (Ultra-fast)
2. **NVIDIA** - `deepseek-ai/deepseek-r1` (GPU-accelerated)
3. **Groq 2** - `llama-3.3-70b-versatile` (Fast inference)
4. **Groq AI** - `llama-3.3-70b-versatile` (Fast inference)

### Tier 2 - High Quality
5. **DeepSeek** - `deepseek/deepseek-chat-v3.1:free` (Free tier)
6. **Codestral** - `codestral-latest` (Code-specialized)
7. **GLM** - `z-ai/glm-4.5-air:free` (Free tier)
8. **Gemini 2** - `gemini-2.0-flash` (Multimodal)
9. **Grok** - `x-ai/grok-4-fast:free` (Free tier)

### Tier 3 - Enterprise
10. **Cohere** - `command-a-03-2025` (Enterprise features)

### Tier 4 - Reliable Fallbacks
11. **Kimi** - `moonshotai/kimi-k2:free` (Long context)
12. **Qwen** - `qwen/qwen3-coder:free` (Code-specialized)
13. **GPT-OSS** - `openai/gpt-oss-120b:free` (Large model)
14. **Chutes** - `zai-org/GLM-4.5-Air` (Final fallback)

### Local Fallback
15. **Ollama** - `phi3:3.8b` (Local, no API key required)

### Standard Providers
16. **OpenAI** - `gpt-4-turbo-preview` (Standard)
17. **Anthropic** - `claude-3-5-sonnet-20241022` (Standard)

---

## Database Layer

### PostgreSQL Tables

1. **users** - User accounts and authentication
2. **agents** - Agent registry and capabilities
3. **tasks** - Task storage with full results
4. **task_executions** - Detailed execution logs
5. **integrations** - Platform integration configurations
6. **ml_models** - ML model registry
7. **ml_training_data** - Training data for ML models
8. **api_keys** - API key management
9. **audit_logs** - Audit trail
10. **notifications** - Notification queue
11. **system_config** - System configuration

### Redis Cache

- Task cache (5 min TTL)
- Agent performance cache (5 min TTL)
- ML predictions cache (1 hour TTL)
- System metrics cache (1 min TTL)
- Session cache (24 hour TTL)

### Neo4j Graph

- Task dependencies
- Agent collaboration networks
- Task similarity analysis
- Agent-task affinity
- Execution paths

---

## API Layer

### FastAPI Application
- **File**: `src/api/main.py`, `src/amas/api/main.py`
- **Routes**:
  - `/api/v1/tasks` - Task management
  - `/api/v1/agents` - Agent management
  - `/api/v1/integrations` - Integration management
  - `/api/v1/analytics` - Analytics endpoints
  - `/api/v1/system` - System metrics
  - `/api/v1/predict` - ML predictions
  - `/api/v1/auth` - Authentication
  - `/ws` - WebSocket endpoint

### Authentication & Authorization
- JWT tokens
- OIDC support
- RBAC with OPA
- Rate limiting

---

## Frontend Components

### React Application
- **Location**: `frontend/src/`
- **Components**:
  - `Dashboard` - System overview
  - `TaskList` - Task listing
  - `CreateTask` - Task creation
  - `TaskExecutionView` - Task execution monitoring
  - `TaskResultsViewer` - Results display
  - `AgentList` - Agent management
  - `IntegrationList` - Integration management
  - `SystemHealth` - System monitoring

### Services
- `api.ts` - API client with Axios
- `websocket.ts` - WebSocket client with reconnection

---

## Component Dependencies

### Agent → Orchestrator
- Agents are initialized by orchestrator
- Orchestrator calls `agent.execute()` for task execution

### Agent → AI Router
- All agents use `self.ai_router.generate_with_fallback()`
- Never call AI providers directly

### Orchestrator → Intelligence Manager
- Orchestrator uses intelligence manager for agent selection
- ML predictions inform agent selection

### API → Orchestrator
- API routes call orchestrator for task execution
- Results are persisted to database

### API → Database
- All tasks persisted to PostgreSQL
- Results include `result`, `output`, `agent_results`

### API → WebSocket
- Real-time updates broadcast via WebSocket
- Events: `task_created`, `task_progress`, `task_completed`

---

## Integration Patterns

### How Components Integrate

1. **Task Creation**:
   - API → Intelligence Manager (prediction)
   - API → Orchestrator (agent selection)
   - API → Database (persistence)
   - API → WebSocket (broadcast)

2. **Task Execution**:
   - Orchestrator → Agent (execute)
   - Agent → AI Router (AI call)
   - AI Router → AI Provider (fallback chain)
   - Orchestrator → Database (result persistence)
   - Orchestrator → WebSocket (progress updates)

3. **Task Retrieval**:
   - API → Memory Cache (check first)
   - API → Redis Cache (check second)
   - API → Database (primary source)
   - API → Cache (update cache)

---

## Next Steps

For usage examples and best practices, see:
- [CAPABILITIES_COMPLETE.md](CAPABILITIES_COMPLETE.md) - System capabilities and usage

