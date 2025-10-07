# 📁 AMAS Project Structure

> Complete overview of the Advanced Multi-Agent Intelligence System codebase organization

## 🏗️ High-Level Architecture

```
Advanced-Multi-Agent-Intelligence-System/
├── 🧠 src/amas/              # Core AMAS source code
├── 🧪 tests/                 # Comprehensive test suite
├── 🌐 web/                   # React web dashboard
├── 🐳 docker/                # Docker configurations
├── 📊 monitoring/            # Monitoring and observability
├── 📚 docs/                  # Documentation
├── 🔧 scripts/               # Utility scripts
├── 📦 config/                # Configuration files
├── 🎯 examples/              # Usage examples
└── 🏭 k8s/                  # Kubernetes manifests
```

## 📂 Detailed Structure

### 🧠 Core Source Code (`src/amas/`)

```
src/amas/
├── __init__.py                    # Package initialization with exports
├── __main__.py                    # Entry point for python -m amas
├── cli.py                         # Command-line interface
│
├── 🎯 core/                       # Core orchestration
│   ├── __init__.py
│   ├── unified_orchestrator_v2.py # Main orchestrator (v2)
│   ├── task_manager.py           # Task queue management
│   ├── message_bus.py            # Inter-component messaging
│   └── types.py                  # Core type definitions
│
├── 🤖 agents/                     # Specialized AI agents
│   ├── __init__.py
│   ├── base/
│   │   ├── intelligence_agent.py  # Base agent class
│   │   └── agent_protocol.py      # Agent communication protocol
│   ├── code_agent.py             # Code analysis agent
│   ├── data_agent.py             # Data analysis agent
│   ├── planning_agent.py         # Strategic planning agent
│   ├── security_expert.py        # Security analysis agent
│   ├── osint_agent.py            # Intelligence gathering
│   ├── forensics_agent.py        # Digital forensics
│   ├── reporting_agent.py        # Report generation
│   ├── ml_decision_agent.py      # ML-powered decisions
│   ├── rl_optimizer_agent.py     # Reinforcement learning
│   └── adaptive_personality.py   # Personality adaptation
│
├── 🧠 intelligence/               # Collective intelligence system
│   ├── __init__.py
│   ├── intelligence_manager.py    # Central intelligence coordinator
│   ├── collective_learning.py    # Shared learning mechanisms
│   ├── predictive_engine.py      # Predictive analytics
│   └── knowledge_graph.py        # Knowledge representation
│
├── 🔌 providers/                  # AI provider integrations
│   ├── __init__.py
│   ├── manager.py                # Provider management & fallback
│   ├── base_provider.py          # Abstract provider interface
│   ├── openai_provider.py        # OpenAI integration
│   ├── anthropic_provider.py     # Anthropic Claude
│   ├── google_provider.py        # Google AI/Gemini
│   ├── local_provider.py         # Local LLM support
│   └── ... (13 more providers)
│
├── 🛠️ services/                   # Infrastructure services
│   ├── __init__.py
│   ├── service_manager.py        # Service lifecycle management
│   ├── llm_service.py           # LLM coordination service
│   ├── vector_service.py        # Vector database operations
│   ├── database_service.py      # PostgreSQL operations
│   ├── cache_service.py         # Redis caching
│   ├── security_service.py      # Security operations
│   └── audit_service.py         # Audit logging
│
├── 🌐 api/                        # REST API layer
│   ├── __init__.py
│   ├── server.py                # FastAPI application
│   ├── routes/
│   │   ├── tasks.py             # Task endpoints
│   │   ├── agents.py            # Agent management
│   │   ├── workflows.py         # Workflow execution
│   │   ├── intelligence.py      # Intelligence insights
│   │   └── health.py            # Health checks
│   ├── middleware/
│   │   ├── auth.py              # Authentication
│   │   ├── rate_limit.py        # Rate limiting
│   │   └── logging.py           # Request logging
│   └── models/                   # Pydantic models
│       ├── requests.py          # Request schemas
│       └── responses.py         # Response schemas
│
├── 📊 monitoring/                 # Observability
│   ├── __init__.py
│   ├── performance_monitor.py    # Performance tracking
│   ├── metrics.py               # Prometheus metrics
│   ├── tracing.py               # Distributed tracing
│   └── alerting.py              # Alert management
│
├── 🔧 utils/                      # Utility functions
│   ├── __init__.py
│   ├── crypto.py                # Encryption utilities
│   ├── validators.py            # Input validation
│   ├── formatters.py            # Output formatting
│   └── async_helpers.py         # Async utilities
│
└── 📋 config/                     # Configuration
    ├── __init__.py
    ├── settings.py              # Application settings
    ├── constants.py             # System constants
    └── schemas.py               # Configuration schemas
```

### 🧪 Test Suite (`tests/`)

```
tests/
├── conftest.py                   # Pytest configuration & fixtures
├── pytest.ini                    # Pytest settings
│
├── unit/                         # Unit tests
│   ├── test_orchestrator.py
│   ├── test_agents.py
│   ├── test_services.py
│   ├── test_providers.py
│   └── test_utils.py
│
├── integration/                  # Integration tests
│   ├── test_integration.py      # Full system integration
│   ├── test_workflows.py        # Workflow testing
│   └── test_multi_agent.py      # Multi-agent coordination
│
├── api/                          # API tests
│   ├── test_api.py              # Endpoint testing
│   ├── test_auth.py             # Authentication tests
│   └── test_websockets.py       # WebSocket tests
│
├── load/                         # Performance tests
│   ├── amas_load_test.py        # Load testing
│   ├── stress_test.py           # Stress testing
│   └── benchmark.py             # Performance benchmarks
│
├── security/                     # Security tests
│   ├── test_security.py
│   └── test_vulnerabilities.py
│
└── fixtures/                     # Test data
    ├── mock_data.json
    └── test_cases.yaml
```

### 🌐 Web Dashboard (`web/`)

```
web/
├── package.json                  # Node.js dependencies
├── tsconfig.json                # TypeScript configuration
├── tailwind.config.js           # Tailwind CSS config
├── vite.config.ts               # Vite bundler config
│
├── public/                      # Static assets
│   ├── index.html
│   └── favicon.ico
│
├── src/
│   ├── index.tsx               # React entry point
│   ├── App.tsx                 # Main app component
│   ├── App.css                 # Global styles
│   │
│   ├── components/             # React components
│   │   ├── Dashboard.tsx       # Main dashboard
│   │   ├── TaskManager.tsx     # Task management UI
│   │   ├── AgentMonitor.tsx    # Agent monitoring
│   │   ├── IntelligenceView.tsx # Intelligence insights
│   │   ├── MetricsDisplay.tsx  # Performance metrics
│   │   └── common/             # Reusable components
│   │       ├── Card.tsx
│   │       ├── Chart.tsx
│   │       └── Table.tsx
│   │
│   ├── hooks/                  # Custom React hooks
│   │   ├── useWebSocket.ts     # WebSocket connection
│   │   ├── useAPI.ts           # API integration
│   │   └── useMetrics.ts       # Metrics updates
│   │
│   ├── services/               # Frontend services
│   │   ├── api.ts              # API client
│   │   ├── websocket.ts        # WebSocket client
│   │   └── auth.ts             # Authentication
│   │
│   └── types/                  # TypeScript types
│       ├── api.d.ts
│       └── components.d.ts
│
└── dist/                       # Build output
```

### 🐳 Docker Configuration (`docker/`)

```
docker/
├── Dockerfile                  # Main application image
├── Dockerfile.dev             # Development image
├── Dockerfile.prod            # Production optimized
├── docker-compose.yml         # Local development
├── docker-compose.prod.yml    # Production setup
├── docker-compose.test.yml    # Test environment
│
├── nginx/                     # Reverse proxy
│   └── nginx.conf
│
├── prometheus/                # Monitoring
│   ├── prometheus.yml
│   └── alerts.yml
│
└── grafana/                   # Dashboards
    ├── dashboards/
    └── provisioning/
```

### 📊 Monitoring (`monitoring/`)

```
monitoring/
├── prometheus/                # Prometheus configs
│   ├── prometheus.yml        # Main configuration
│   ├── alerts/               # Alert rules
│   │   ├── system.yml
│   │   ├── agents.yml
│   │   └── api.yml
│   └── targets/              # Service discovery
│
├── grafana/                  # Grafana dashboards
│   ├── dashboards/
│   │   ├── overview.json     # System overview
│   │   ├── agents.json       # Agent performance
│   │   ├── intelligence.json # Intelligence metrics
│   │   └── api.json          # API metrics
│   └── provisioning/
│
└── scripts/                  # Monitoring scripts
    ├── setup_monitoring.sh
    └── export_metrics.py
```

### 📚 Documentation (`docs/`)

```
docs/
├── README.md                 # Documentation home
├── architecture.md           # System architecture
├── getting-started.md        # Quick start guide
│
├── api/                      # API documentation
│   ├── overview.md
│   ├── authentication.md
│   └── endpoints.md
│
├── development/              # Developer guides
│   ├── setup.md
│   ├── contributing.md
│   ├── agent-development.md
│   └── testing.md
│
├── deployment/               # Deployment guides
│   ├── docker.md
│   ├── kubernetes.md
│   ├── aws.md
│   └── scaling.md
│
├── user/                     # User documentation
│   ├── installation.md
│   ├── configuration.md
│   ├── usage.md
│   └── troubleshooting.md
│
└── security/                 # Security documentation
    ├── overview.md
    ├── compliance.md
    └── best-practices.md
```

### 🔧 Scripts (`scripts/`)

```
scripts/
├── setup/                    # Setup scripts
│   ├── setup_database.py     # Database initialization
│   ├── setup_redis.py        # Redis configuration
│   ├── setup_vectors.py      # Vector DB setup
│   └── setup_monitoring.sh   # Monitoring setup
│
├── maintenance/              # Maintenance scripts
│   ├── backup.sh            # Backup procedures
│   ├── cleanup.py           # Data cleanup
│   ├── migrate.py           # Database migrations
│   └── health_check.sh      # System health check
│
├── development/              # Dev tools
│   ├── generate_api_docs.py # API doc generation
│   ├── run_linters.sh       # Code quality checks
│   ├── update_deps.py       # Dependency updates
│   └── create_agent.py      # Agent scaffolding
│
└── deployment/               # Deployment scripts
    ├── deploy.sh            # Deployment automation
    ├── rollback.sh          # Rollback procedure
    └── validate_deploy.py   # Deployment validation
```

### 📦 Configuration (`config/`)

```
config/
├── .env.example             # Environment template
├── intelligence.json        # Intelligence settings
├── providers.yaml           # AI provider configs
├── agents.yaml              # Agent configurations
├── security.yaml            # Security settings
└── monitoring.yaml          # Monitoring configs
```

### 🎯 Examples (`examples/`)

```
examples/
├── basic_usage.py           # Basic AMAS usage
├── custom_agent.py          # Creating custom agents
├── workflow_example.py      # Complex workflows
├── api_client.py            # API client example
├── intelligence_demo.py     # Intelligence features
└── notebooks/               # Jupyter notebooks
    ├── getting_started.ipynb
    └── advanced_features.ipynb
```

## 🔑 Key Files

### Root Directory

```
/
├── README.md                # Project overview
├── README_HONEST.md         # Transparent status
├── DEPLOYMENT.md            # Deployment guide
├── TESTING.md               # Testing guide
├── CHANGELOG.md             # Version history
├── LICENSE                  # MIT License
├── requirements.txt         # Python dependencies
├── requirements-dev.txt     # Dev dependencies
├── requirements-test.txt    # Test dependencies
├── pyproject.toml          # Python project config
├── setup.py                # Package setup
├── Makefile                # Build automation
├── .gitignore              # Git exclusions
└── .env.example            # Environment template
```

## 🎨 Design Patterns

### Architectural Patterns

1. **Microservices**: Each agent is an independent service
2. **Event-Driven**: Async message passing between components
3. **Repository Pattern**: Data access abstraction
4. **Factory Pattern**: Agent and provider creation
5. **Strategy Pattern**: Swappable AI providers
6. **Observer Pattern**: Real-time monitoring

### Code Organization

- **Separation of Concerns**: Clear boundaries between layers
- **DRY Principle**: Shared utilities and base classes
- **SOLID Principles**: Extensible and maintainable design
- **Async-First**: Built for concurrent operations
- **Type Safety**: Comprehensive type hints
- **Testability**: Dependency injection and mocking

## 📈 Growth & Maintenance

### Adding New Components

1. **New Agent**: Create in `src/amas/agents/`, extend `IntelligenceAgent`
2. **New Provider**: Add to `src/amas/providers/`, implement `BaseProvider`
3. **New API Endpoint**: Add route in `src/amas/api/routes/`
4. **New Service**: Create in `src/amas/services/`, register in `ServiceManager`

### Conventions

- **Naming**: Use descriptive names, follow Python conventions
- **Documentation**: Docstrings for all public methods
- **Testing**: Write tests alongside new features
- **Typing**: Full type annotations required
- **Async**: Prefer async/await for I/O operations
- **Logging**: Structured logging with appropriate levels

---

*"A well-organized codebase is a joy to work with." - AMAS Team*