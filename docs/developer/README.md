# 👨‍💻 AMAS Developer Guide

## Overview

Welcome to the AMAS Developer Guide! This comprehensive documentation will help you understand the system architecture, contribute to the project, and extend AMAS capabilities. Whether you're fixing bugs, adding features, or building custom agents, this guide has you covered.

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment](#development-environment)
3. [Architecture Overview](#architecture-overview)
4. [Core Components](#core-components)
5. [Agent Development](#agent-development)
6. [API Development](#api-development)
7. [Testing](#testing)
8. [Code Style Guide](#code-style-guide)
9. [Debugging](#debugging)
10. [Performance Optimization](#performance-optimization)
11. [Security Considerations](#security-considerations)
12. [Contributing](#contributing)

---

## 🚀 Getting Started

### Prerequisites

Before you begin development, ensure you have:

- **Python 3.11+** installed
- **Docker & Docker Compose** for containerized development
- **Git** for version control
- **VS Code** or **PyCharm** (recommended IDEs)
- **PostgreSQL 14+** for database
- **Redis 6+** for caching and queuing

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
pip install -r requirements-monitoring.txt

# Install pre-commit hooks
pre-commit install

# Copy environment configuration
cp .env.example .env
# Edit .env with your API keys and settings

# Run initial setup
python scripts/setup_dev_environment.py

# Start development services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Run tests to verify setup
pytest tests/
```

---

## 💻 Development Environment

### IDE Setup

#### VS Code
```json
// .vscode/settings.json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "editor.formatOnSave": true,
    "editor.rulers": [88],
    "[python]": {
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

#### PyCharm
1. Set Python interpreter to virtual environment
2. Enable Black formatter: Settings → Tools → Black
3. Configure pytest: Settings → Tools → Python Integrated Tools
4. Enable type checking: Settings → Editor → Inspections → Python

### Development Tools

```bash
# Code formatting
black src/ tests/

# Import sorting
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/

# Security scanning
bandit -r src/

# Run all checks
make lint
```

---

## 🏗️ Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AMAS Architecture                        │
├─────────────────────────────────────────────────────────────────┤
│                      Presentation Layer                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐        │
│  │   Web UI    │  │   CLI Tool   │  │   REST API     │        │
│  └─────────────┘  └──────────────┘  └────────────────┘        │
├─────────────────────────────────────────────────────────────────┤
│                      Application Layer                           │
│  ┌─────────────────────────────────────────────────────┐        │
│  │              Agent Orchestrator                      │        │
│  ├─────────────────────────────────────────────────────┤        │
│  │  Task Queue │ Workflow Engine │ Event Dispatcher    │        │
│  └─────────────────────────────────────────────────────┘        │
├─────────────────────────────────────────────────────────────────┤
│                        Agent Layer                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  OSINT   │  │ Security │  │ Analysis │  │ Forensics│       │
│  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
├─────────────────────────────────────────────────────────────────┤
│                      Service Layer                               │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐        │
│  │ AI Manager  │  │ ML Decision  │  │   Monitoring   │        │
│  │ (16 Providers)│ │    Engine    │  │    Service     │        │
│  └─────────────┘  └──────────────┘  └────────────────┘        │
├─────────────────────────────────────────────────────────────────┤
│                        Data Layer                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │PostgreSQL│  │  Redis   │  │  FAISS   │  │  Neo4j   │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Microservice Architecture**: Loosely coupled, independently deployable services
2. **Event-Driven**: Asynchronous communication via event bus
3. **Domain-Driven Design**: Clear boundaries between domains
4. **SOLID Principles**: Single responsibility, open/closed, etc.
5. **12-Factor App**: Environment-based configuration, stateless processes

---

## 🔧 Core Components

### 1. Agent Orchestrator

The heart of AMAS that coordinates all agent activities.

```python
# src/amas/orchestrator/orchestrator.py
class AgentOrchestrator:
    """Coordinates multi-agent operations and workflows."""
    
    def __init__(self, service_manager: ServiceManager):
        self.service_manager = service_manager
        self.agents = {}
        self.task_queue = TaskQueue()
        self.event_bus = EventBus()
        
    async def execute_task(self, task: Task) -> TaskResult:
        """Execute a task using appropriate agents."""
        # Task allocation using ML decision engine
        agents = await self.allocate_agents(task)
        
        # Create workflow
        workflow = self.create_workflow(task, agents)
        
        # Execute workflow
        results = await workflow.execute()
        
        return TaskResult(task_id=task.id, results=results)
```

### 2. Universal AI Manager

Manages 16 AI providers with intelligent fallback.

```python
# src/amas/ai/universal_ai_manager.py
class UniversalAIManager:
    """Manages multiple AI providers with fallback support."""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.selector = ProviderSelector()
        self.health_monitor = HealthMonitor()
        
    async def generate(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response with automatic fallback."""
        for attempt in range(self.max_retries):
            provider = self.selector.select_provider()
            
            try:
                response = await provider.generate(prompt, **kwargs)
                self.health_monitor.record_success(provider)
                return response
                
            except Exception as e:
                self.health_monitor.record_failure(provider, e)
                if attempt == self.max_retries - 1:
                    raise
                continue
```

### 3. ML Decision Engine

Intelligent task allocation using machine learning.

```python
# src/amas/ml/decision_engine.py
class MLDecisionEngine:
    """ML-powered decision making for task allocation."""
    
    def __init__(self):
        self.model = self._load_model()
        self.feature_extractor = FeatureExtractor()
        self.optimizer = MultiObjectiveOptimizer()
        
    def allocate_agents(self, task: Task) -> List[Agent]:
        """Allocate agents using ML predictions."""
        # Extract features
        features = self.feature_extractor.extract(task)
        
        # Predict requirements
        predictions = self.model.predict(features)
        
        # Optimize allocation
        allocation = self.optimizer.optimize(
            predictions,
            objectives=['performance', 'cost', 'reliability']
        )
        
        return allocation.agents
```

### 4. Service Manager

Manages all system services and their lifecycle.

```python
# src/amas/core/service_manager.py
class ServiceManager:
    """Manages system services lifecycle."""
    
    def __init__(self):
        self.services = {}
        self.health_checker = HealthChecker()
        
    async def start_services(self):
        """Start all registered services."""
        for name, service in self.services.items():
            try:
                await service.start()
                logger.info(f"Started service: {name}")
            except Exception as e:
                logger.error(f"Failed to start {name}: {e}")
                raise
                
    async def shutdown(self):
        """Gracefully shutdown all services."""
        for name, service in reversed(self.services.items()):
            await service.stop()
            logger.info(f"Stopped service: {name}")
```

---

## 🤖 Agent Development

### Creating a Custom Agent

#### 1. Define Agent Class
```python
# src/amas/agents/custom_agent.py
from src.amas.agents.base import BaseAgent, AgentCapability

class CustomAgent(BaseAgent):
    """Custom agent for specific functionality."""
    
    def __init__(self):
        super().__init__(
            agent_id="custom-agent",
            name="Custom Agent",
            description="Performs custom operations"
        )
        
    @property
    def capabilities(self) -> List[AgentCapability]:
        """Define agent capabilities."""
        return [
            AgentCapability(
                name="custom_analysis",
                description="Perform custom analysis",
                parameters={
                    "data": "Data to analyze",
                    "options": "Analysis options"
                }
            )
        ]
        
    async def custom_analysis(self, data: str, options: dict) -> dict:
        """Implement custom analysis logic."""
        # Your implementation here
        result = await self._analyze_data(data, options)
        return {
            "status": "success",
            "analysis": result
        }
```

#### 2. Register Agent
```python
# src/amas/agents/registry.py
from src.amas.agents.custom_agent import CustomAgent

AGENT_REGISTRY = {
    "osint": OSINTAgent,
    "security": SecurityAgent,
    "custom": CustomAgent,  # Add your agent
}
```

#### 3. Test Your Agent
```python
# tests/agents/test_custom_agent.py
import pytest
from src.amas.agents.custom_agent import CustomAgent

@pytest.mark.asyncio
async def test_custom_analysis():
    agent = CustomAgent()
    
    result = await agent.custom_analysis(
        data="test data",
        options={"mode": "detailed"}
    )
    
    assert result["status"] == "success"
    assert "analysis" in result
```

### Agent Best Practices

1. **Single Responsibility**: Each agent should focus on one domain
2. **Async Operations**: Use async/await for I/O operations
3. **Error Handling**: Implement comprehensive error handling
4. **Logging**: Use structured logging for debugging
5. **Testing**: Write unit and integration tests
6. **Documentation**: Document capabilities and parameters

---

## 🔌 API Development

### Adding New Endpoints

#### 1. Define Route
```python
# src/amas/api/routes/custom.py
from fastapi import APIRouter, Depends
from src.amas.api.auth import verify_api_key
from src.amas.api.models import CustomRequest, CustomResponse

router = APIRouter(prefix="/custom", tags=["custom"])

@router.post("/analyze", response_model=CustomResponse)
async def analyze(
    request: CustomRequest,
    api_key: str = Depends(verify_api_key)
):
    """Perform custom analysis."""
    # Implementation
    return CustomResponse(result=result)
```

#### 2. Register Route
```python
# src/amas/api/app.py
from src.amas.api.routes import custom

app.include_router(custom.router, prefix="/api/v1")
```

#### 3. Add Models
```python
# src/amas/api/models.py
from pydantic import BaseModel

class CustomRequest(BaseModel):
    """Custom analysis request."""
    data: str
    options: dict = {}
    
class CustomResponse(BaseModel):
    """Custom analysis response."""
    result: dict
    metadata: dict = {}
```

### API Best Practices

1. **RESTful Design**: Follow REST conventions
2. **Versioning**: Use URL versioning (/api/v1/)
3. **Documentation**: Use FastAPI's automatic docs
4. **Validation**: Use Pydantic for request/response validation
5. **Error Handling**: Return consistent error responses
6. **Rate Limiting**: Implement rate limiting for all endpoints

---

## 🧪 Testing

### Test Structure

```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── performance/       # Performance tests
├── security/         # Security tests
├── e2e/             # End-to-end tests
├── fixtures/        # Test fixtures
└── conftest.py      # Pytest configuration
```

### Writing Tests

#### Unit Test Example
```python
# tests/unit/test_decision_engine.py
import pytest
from src.amas.ml.decision_engine import MLDecisionEngine

class TestMLDecisionEngine:
    @pytest.fixture
    def engine(self):
        return MLDecisionEngine()
        
    def test_allocate_agents(self, engine):
        task = create_test_task()
        agents = engine.allocate_agents(task)
        
        assert len(agents) > 0
        assert all(isinstance(a, Agent) for a in agents)
```

#### Integration Test Example
```python
# tests/integration/test_orchestrator.py
@pytest.mark.asyncio
async def test_task_execution():
    orchestrator = await create_test_orchestrator()
    
    task = Task(
        task_type="security_scan",
        parameters={"target": "example.com"}
    )
    
    result = await orchestrator.execute_task(task)
    
    assert result.status == "completed"
    assert result.results is not None
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test category
pytest tests/unit/
pytest tests/integration/

# Run tests in parallel
pytest -n auto

# Run with verbose output
pytest -v

# Run specific test
pytest tests/unit/test_decision_engine.py::test_allocate_agents
```

### Test Coverage Goals

- **Unit Tests**: 80%+ coverage
- **Integration Tests**: Critical paths covered
- **Performance Tests**: Baseline metrics established
- **Security Tests**: OWASP Top 10 covered
- **E2E Tests**: User workflows covered

---

## 📝 Code Style Guide

### Python Style

We follow PEP 8 with some modifications:

```python
# Good example
class AgentOrchestrator:
    """Orchestrates multi-agent operations.
    
    This class coordinates the execution of tasks across
    multiple agents, handling task allocation, workflow
    creation, and result aggregation.
    
    Attributes:
        agents: Dictionary of registered agents
        task_queue: Queue for pending tasks
        event_bus: Event bus for inter-component communication
    """
    
    def __init__(self, service_manager: ServiceManager) -> None:
        """Initialize the orchestrator.
        
        Args:
            service_manager: Service manager instance
        """
        self.service_manager = service_manager
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: TaskQueue = TaskQueue()
        
    async def execute_task(
        self,
        task: Task,
        timeout: Optional[float] = None
    ) -> TaskResult:
        """Execute a task using appropriate agents.
        
        Args:
            task: Task to execute
            timeout: Optional timeout in seconds
            
        Returns:
            TaskResult containing execution results
            
        Raises:
            TaskExecutionError: If task execution fails
        """
        # Implementation
```

### Type Hints

Always use type hints:

```python
from typing import List, Dict, Optional, Union, Tuple

def process_data(
    data: List[Dict[str, Any]],
    options: Optional[Dict[str, Union[str, int]]] = None
) -> Tuple[bool, str]:
    """Process data with options."""
    # Implementation
    return True, "Success"
```

### Docstrings

Use Google-style docstrings:

```python
def calculate_metrics(data: List[float], window: int = 10) -> Dict[str, float]:
    """Calculate statistical metrics for data.
    
    Args:
        data: List of numerical values
        window: Rolling window size for calculations
        
    Returns:
        Dictionary containing calculated metrics:
            - mean: Average value
            - std: Standard deviation
            - min: Minimum value
            - max: Maximum value
            
    Raises:
        ValueError: If data is empty or window size is invalid
        
    Example:
        >>> calculate_metrics([1, 2, 3, 4, 5])
        {'mean': 3.0, 'std': 1.58, 'min': 1, 'max': 5}
    """
    if not data:
        raise ValueError("Data cannot be empty")
    # Implementation
```

---

## 🐛 Debugging

### Debug Configuration

```python
# .env for development
AMAS_DEBUG=true
AMAS_LOG_LEVEL=debug
AMAS_TRACE_ENABLED=true
```

### Using Debugger

#### VS Code
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug AMAS",
            "type": "python",
            "request": "launch",
            "module": "src.amas.main",
            "env": {
                "AMAS_DEBUG": "true"
            }
        }
    ]
}
```

#### PyCharm
1. Run → Edit Configurations
2. Add Python configuration
3. Module: `src.amas.main`
4. Environment variables: `AMAS_DEBUG=true`

### Logging

```python
import structlog

logger = structlog.get_logger(__name__)

# Basic logging
logger.info("Processing task", task_id=task.id)

# With context
logger.bind(user_id=user.id).info("User action", action="create_task")

# Error logging
try:
    result = await process_task(task)
except Exception as e:
    logger.error("Task failed", task_id=task.id, error=str(e), exc_info=True)
```

### Performance Profiling

```python
# Using cProfile
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
result = expensive_operation()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 functions
```

---

## ⚡ Performance Optimization

### Optimization Guidelines

1. **Profile First**: Always profile before optimizing
2. **Async I/O**: Use async for all I/O operations
3. **Caching**: Implement caching where appropriate
4. **Connection Pooling**: Use connection pools for databases
5. **Batch Processing**: Process items in batches
6. **Lazy Loading**: Load resources only when needed

### Example Optimizations

```python
# Connection pooling
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
    pool_recycle=3600
)

# Caching
from functools import lru_cache

@lru_cache(maxsize=1000)
def expensive_calculation(param: str) -> float:
    # Expensive operation
    return result

# Batch processing
async def process_batch(items: List[Item], batch_size: int = 100):
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        await process_items(batch)
```

---

## 🔒 Security Considerations

### Security Best Practices

1. **Input Validation**: Always validate and sanitize inputs
2. **Authentication**: Use strong authentication mechanisms
3. **Authorization**: Implement role-based access control
4. **Encryption**: Encrypt sensitive data at rest and in transit
5. **Secrets Management**: Never hardcode secrets
6. **Dependency Scanning**: Regularly scan dependencies

### Security Implementation

```python
# Input validation
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    email: str
    age: int
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v
        
    @validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Invalid age')
        return v

# Authentication
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if not is_valid_api_key(api_key):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

---

## 🤝 Contributing

### Development Workflow

1. **Fork & Clone**
   ```bash
   git clone https://github.com/your-username/amas.git
   cd amas
   ```

2. **Create Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Write code following style guide
   - Add tests for new functionality
   - Update documentation

4. **Run Tests**
   ```bash
   make test
   make lint
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

6. **Push & Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new agent capability
fix: resolve memory leak in orchestrator
docs: update API documentation
test: add integration tests for ML engine
refactor: simplify decision engine logic
perf: optimize task allocation algorithm
chore: update dependencies
```

### Code Review Process

1. **Automated Checks**: CI/CD runs tests and linting
2. **Peer Review**: At least one approval required
3. **Security Review**: For security-related changes
4. **Performance Review**: For performance-critical paths

---

## 📚 Additional Resources

### Internal Documentation
- [Architecture Details](architecture.md)
- [Security Hardening](hardening.md)
- [API Reference](../api/README.md)
- [Deployment Guide](../deployment/DEPLOYMENT.md)

### External Resources
- [Python Best Practices](https://docs.python-guide.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AsyncIO Guide](https://docs.python.org/3/library/asyncio.html)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Tools & Libraries
- [Black](https://black.readthedocs.io/) - Code formatter
- [MyPy](https://mypy.readthedocs.io/) - Type checker
- [Pytest](https://docs.pytest.org/) - Testing framework
- [Structlog](https://www.structlog.org/) - Structured logging

---

**Last Updated**: January 2025  
**Version**: 1.1.0  
**Maintainers**: AMAS Development Team