# AMAS Project Structure

This document outlines the clean, professional structure of the Advanced Multi-Agent Intelligence System (AMAS) project - now transformed into a next-generation enterprise AI platform.

## 🚀 **Latest Architecture Highlights (v1.1.0)**

- **🤖 Universal AI Manager**: 16 AI providers with intelligent fallback
- **🧠 ML-Powered Decision Engine**: Intelligent task allocation using machine learning
- **🛡️ Enterprise Security**: 8 compliance frameworks (GDPR, SOC2, HIPAA, PCI-DSS, ISO27001, NIST, CCA, FERPA)
- **📊 Predictive Analytics**: ML models for forecasting and anomaly detection
- **⚡ Reinforcement Learning**: Self-improving system optimization
- **🗣️ Natural Language Interface**: Command agents in plain English
- **🎨 Rich Visual Interface**: Beautiful console with progress bars and real-time monitoring
- **🧪 Comprehensive Testing**: 7 test suites with 80%+ code coverage

## 📁 Root Directory

```
/workspace/
├── README.md                    # Main project documentation
├── LICENSE                      # MIT License
├── CHANGELOG.md                 # Version history
├── pyproject.toml              # Modern Python project configuration
├── requirements.txt            # Production dependencies
├── requirements-test.txt       # Test dependencies
├── setup.py                    # Package setup script
├── Makefile                    # Development commands
├── .env.example               # Environment configuration template
├── .gitignore                 # Git ignore rules
├── .pre-commit-config.yaml    # Pre-commit hooks
├── pytest.ini                # Pytest configuration
└── main.py                    # Application entry point
```

## 📁 Source Code (`src/`)

```
src/amas/
├── __init__.py
├── main.py                    # Main application entry point
├── cli.py                     # Command-line interface
├── config/                    # Configuration management
│   ├── __init__.py
│   ├── settings.py           # Application settings
│   ├── ai_config.py          # AI service configuration
│   └── amas_config.yaml      # YAML configuration
├── core/                      # Core system components
│   ├── __init__.py
│   ├── orchestrator.py       # Main orchestrator
│   ├── enhanced_orchestrator.py
│   ├── unified_orchestrator.py
│   ├── integration_manager.py
│   ├── api_clients.py
│   ├── api_integration.py
│   └── quick_start.py
├── agents/                    # AI Agent implementations
│   ├── __init__.py
│   ├── orchestrator.py
│   ├── orchestrator_enhanced.py
│   ├── unified_ai_router.py
│   ├── base/                 # Base agent classes
│   │   ├── __init__.py
│   │   ├── intelligence_agent.py
│   │   ├── react_agent.py
│   │   └── agent_communication.py
│   ├── data_analysis/        # Data analysis agent
│   ├── forensics/            # Digital forensics agent
│   ├── investigation/        # Investigation agent
│   ├── metadata/             # Metadata analysis agent
│   ├── osint/                # OSINT collection agent
│   ├── reporting/            # Report generation agent
│   ├── reverse_engineering/  # Reverse engineering agent
│   └── technology_monitor/   # Technology monitoring agent
├── api/                      # FastAPI web interface
│   ├── __init__.py
│   └── main.py              # API server
├── services/                 # Core services
│   ├── __init__.py
│   ├── service_manager.py   # Service orchestration
│   ├── database_service.py  # Database operations
│   ├── llm_service.py       # Language model service
│   ├── vector_service.py    # Vector search service
│   ├── knowledge_graph_service.py
│   ├── security_service.py  # Security operations
│   ├── monitoring_service.py
│   ├── ai_service_manager.py
│   ├── universal_ai_manager.py  # 16-provider fallback system
│   ├── ml_decision_engine.py    # ML-powered task allocation
│   ├── reinforcement_learning.py # RL optimizer
│   ├── predictive_analytics.py  # ML forecasting
│   ├── compliance_service.py    # Enterprise compliance
│   └── ... (other services)
├── security/                 # Security components
│   ├── __init__.py
│   ├── authentication.py
│   ├── authorization.py
│   ├── encryption.py
│   ├── audit.py
│   └── secure_config.py
└── utils/                    # Utility functions
    ├── __init__.py
    └── security_utils.py
```

## 📁 Documentation (`docs/`)

```
docs/
├── README.md                 # Documentation index
├── architecture.md          # System architecture
├── api/                     # API documentation
│   ├── API_FALLBACK_SYSTEM.md
│   └── AI_API_MANAGER_SUMMARY.md
├── deployment/              # Deployment guides
│   ├── DEPLOYMENT.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   ├── PRODUCTION_DEPLOYMENT.md
│   └── PRODUCTION_READINESS_CHECKLIST.md
├── development/             # Development guides
│   ├── CONTRIBUTING.md
│   ├── PRE_COMMIT_INFO.md
│   ├── HOW_TO_CREATE_PULL_REQUESTS.md
│   └── CREATE_YOUR_PULL_REQUEST.md
├── security/                # Security documentation
│   ├── AUTHENTICATION_SETUP.md
│   └── SECURITY.md
└── user/                    # User guides
    ├── README.md
    ├── SETUP_GUIDE.md
    ├── WORKFLOW_VERIFICATION_GUIDE.md
    └── PULL_REQUEST_REVIEW_GUIDE.md
```

## 📁 Scripts (`scripts/`)

```
scripts/
├── deploy.sh                # Main deployment script
├── setup.sh                 # Environment setup
├── health_check.py          # System health monitoring
├── generate_changelog.py    # Changelog generation
├── generate_release_notes.py
├── cli.py                   # CLI utilities
├── deployment/              # Deployment scripts
│   ├── setup_ai_complete.sh
│   ├── start_offline_docker.sh
│   ├── start_offline.sh
│   ├── start.sh
│   └── start.bat
├── development/             # Development tools
│   ├── check_secrets.py
│   ├── setup_complete.py
│   ├── setup_offline.py
│   ├── setup_venv.py
│   └── setup.py
├── maintenance/             # Maintenance scripts
│   ├── final_workflow_verification.py
│   ├── run_comprehensive_test.py
│   ├── run_workflow_tests.py
│   ├── run_workflow_verification.py
│   ├── update_9_api_support.py
│   └── verify_file_structure.py
└── testing/                 # Test utilities
    ├── test_ai_integration_complete.py
    ├── test_enhanced_responder.py
    ├── test_fallback_system.py
    ├── test_openrouter_direct.py
    ├── test_ultimate_fallback_system.py
    ├── test_unified_router.py
    ├── test_workflow_execution.py
    ├── test_workflows.py
    ├── validate_api_config.py
    ├── validate_complete_workflows.py
    ├── validate_upgrade.py
    ├── validate_workflows.py
    └── verify_security_fixes.py
```

## 📁 Examples (`examples/`)

```
examples/
├── api_manager_usage.py     # API manager usage example
├── basic_orchestration.py   # Basic system orchestration
├── code_generation.py       # Code generation example
├── minimal_example.py       # Minimal usage example
├── offline_example.py       # Offline operation example
└── research_pipeline.py     # Research pipeline example
```

## 📁 Tests (`tests/`)

```
tests/
├── conftest.py              # Pytest configuration
├── test_agents.py           # Agent tests
├── test_api.py              # API tests
├── test_core.py             # Core functionality tests
├── test_services.py         # Service tests
├── test_integration.py      # Integration tests
├── test_security_fixes.py   # Security tests
├── unit/                    # Unit tests
│   └── test_basic.py
├── integration/             # Integration tests
│   ├── test_fallback_system.py
│   ├── test_workflow_execution.py
│   ├── test_ultimate_fallback_system.py
│   ├── test_enhanced_responder.py
│   ├── test_system.py
│   ├── test_simple.py
│   ├── test_complete_system.py
│   ├── test_ai_system.py
│   ├── test_9_api_system.py
│   ├── test_ai_integration_complete.py
│   └── test_workflows.py
└── e2e/                     # End-to-end tests
    └── test_api_health.py
```

## 📁 Web Interface (`web/`)

```
web/
├── public/
│   └── index.html          # Main HTML template
├── src/
│   ├── App.js              # Main React application
│   ├── index.js            # Application entry point
│   └── index.css           # Global styles
├── package.json            # Node.js dependencies
├── build.sh                # Build script
└── README.md               # Web interface documentation
```

## 📁 Docker (`docker/`)

```
docker/
├── Dockerfile               # Main application image
├── Dockerfile.offline       # Offline deployment image
├── docker-compose.yml       # Production services
├── docker-compose.test.yml  # Test environment
├── docker-compose-offline.yml
├── nginx.conf               # Nginx configuration
└── ... (other Docker files)
```

## 📁 GitHub Actions (`.github/workflows/`)

```
.github/workflows/
└── ci.yml                   # CI/CD pipeline
```

## 🧹 Cleanup Summary

The following items were removed during cleanup:

### Temporary Files
- All `*.pyc` files and `__pycache__` directories
- Log files in `/logs` directory
- Temporary improvement reports and multi-agent results

### Development Artifacts
- Fix scripts (`fix_*.py`, `resolve_*.py`, `precision_*.py`, etc.)
- Test files in root directory
- Demo and standalone files
- Security fix scripts

### Redundant Documentation
- Duplicate and temporary documentation files
- Issue tracking files
- Sprint planning documents
- Project completion summaries

### Configuration Cleanup
- Standardized configuration files
- Updated `.gitignore` to prevent future clutter
- Created proper environment configuration template

## 🚀 Best Practices Implemented

1. **Clean Directory Structure**: Organized files into logical directories
2. **Professional Documentation**: Consolidated docs into proper structure
3. **Development Tools**: Added Makefile, pre-commit hooks, and CI/CD
4. **Configuration Management**: Standardized configuration files
5. **Testing Organization**: Proper test structure and organization
6. **Script Organization**: Categorized scripts by purpose
7. **Security**: Proper security configuration and documentation
8. **Docker**: Clean containerization setup
9. **Git Workflow**: Proper .gitignore and GitHub Actions

## 📋 Quick Start

```bash
# Setup development environment
make setup

# Run the application
make run

# Run tests
make test

# Run linting
make lint

# Format code
make format
```

This structure follows Python best practices and provides a clean, maintainable, and professional codebase for the AMAS project.