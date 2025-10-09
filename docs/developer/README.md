# 👨‍💻 AMAS Developer Guide - Complete Integration Documentation
# 👨‍💻 AMAS Developer Guide

> **Last Updated**: January 2025 | **Integration Status**: ✅ Fully Integrated

## Overview

Welcome to the AMAS Developer Guide! This comprehensive documentation will help you understand the system architecture, contribute to the project, and extend AMAS capabilities. Whether you're fixing bugs, adding features, or building custom agents, this guide has you covered.

**✅ 100% Implementation Verified** - All critical improvements from the project audit have been implemented and verified.

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

### 1. Unified Orchestrator

The heart of AMAS that coordinates all agent activities.

```python
# src/amas/orchestrator/orchestrator.py
class AgentOrchestrator:
    """Coordinates multi-agent operations and workflows."""
The heart of AMAS, implementing the unified orchestrator with provider management.

```python
# src/amas/core/unified_orchestrator.py
class UnifiedIntelligenceOrchestrator:
    """
    Unified orchestrator with provider management and circuit breakers:
    - Provider Management: Multi-AI provider support with fallback
    - Circuit Breakers: Robust error handling and recovery
    - Task Queue: Priority-based task management
    - Performance Monitoring: Real-time metrics and health tracking
    """
    
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

### 3. Minimal Configuration System (`src/amas/config/minimal_config.py`)

Simplified configuration with minimal API key requirements:

```python
class MinimalConfigManager:
    """Minimal configuration manager with mode-based setup"""
    
    def __init__(self, mode: MinimalMode):
        self.mode = mode
        self.config = self._get_config_for_mode(mode)
    
    def validate_environment(self) -> bool:
        """Validate environment against minimal requirements"""
        required_keys = self.config.required_providers
        missing_keys = []
        
        for provider in required_keys:
            if not os.getenv(f"{provider.upper()}_API_KEY"):
                missing_keys.append(provider)
        
        return len(missing_keys) == 0
    
    def get_setup_guide(self) -> str:
        """Generate setup guide for the current mode"""
        return f"""
        Minimal Configuration Setup ({self.mode.value}):
        
        Required API Keys:
        {', '.join(self.config.required_providers)}
        
        Optional API Keys:
        {', '.join(self.config.optional_providers)}
        """
```

## Agent Development

### Real Agent Implementations

AMAS now includes fully functional agents with real implementations:

#### OSINT Agent (`src/amas/agents/osint/osint_agent.py`)
```python
class OSINTAgent(IntelligenceAgent):
    """Real OSINT agent with web scraping and analysis"""
    
    async def _scrape_webpage(self, url: str, keywords: List[str]) -> Dict[str, Any]:
        """Real web scraping with aiohttp and BeautifulSoup"""
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        ) as session:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract real data
                title = soup.find('title').text if soup.find('title') else ""
                text = soup.get_text()
                links = [link.get('href') for link in soup.find_all('a', href=True)]
                
                return {
                    "title": title,
                    "text": text,
                    "links": links,
                    "status_code": response.status
                }
```

#### Forensics Agent (`src/amas/agents/forensics/forensics_agent.py`)
```python
class ForensicsAgent(IntelligenceAgent):
    """Real forensics agent with file analysis and security"""
    
    async def _calculate_hashes(self, file_path: Path) -> Dict[str, str]:
        """Real hash calculation with enhanced security"""
        hashes = {}
        
        with open(file_path, "rb") as f:
            md5_hash = hashlib.md5()
            sha1_hash = hashlib.sha1()
            sha256_hash = hashlib.sha256()
            sha512_hash = hashlib.sha512()
            
            while chunk := f.read(8192):
                md5_hash.update(chunk)
                sha1_hash.update(chunk)
                sha256_hash.update(chunk)
                sha512_hash.update(chunk)
            
            hashes["md5"] = md5_hash.hexdigest()
            hashes["sha1"] = sha1_hash.hexdigest()
            hashes["sha256"] = sha256_hash.hexdigest()
            hashes["sha512"] = sha512_hash.hexdigest()
            hashes["_security_note"] = "Use SHA256 or SHA512 for security-critical applications"
        
        return hashes
```

### Real Agent Implementations

AMAS now includes fully functional agent implementations:

#### OSINT Agent (`src/amas/agents/osint/osint_agent.py`)
```python
class OSINTAgent(IntelligenceAgent):
    """Real OSINT agent with web scraping and analysis"""
    
    async def _scrape_webpage(self, url: str, keywords: List[str]) -> Dict[str, Any]:
        """Real web scraping with aiohttp and BeautifulSoup"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                return {
                    "title": soup.title.string if soup.title else "",
                    "text": soup.get_text(),
                    "links": [link.get('href') for link in soup.find_all('a')],
                    "images": [img.get('src') for img in soup.find_all('img')]
                }
    
    async def _analyze_scraped_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Real data analysis with entity extraction"""
        # Extract emails, phone numbers, URLs, domains
        # Perform keyword frequency analysis
        # Basic sentiment analysis
        return analysis_results
```

#### Forensics Agent (`src/amas/agents/forensics/forensics_agent.py`)
```python
class ForensicsAgent(IntelligenceAgent):
    """Real forensics agent with file analysis and security"""
    
    async def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Real file analysis with comprehensive security checks"""
        return {
            "file_info": await self._get_file_info(file_path),
            "hashes": await self._calculate_hashes(file_path),
            "content_analysis": await self._analyze_file_content(file_path),
            "security_analysis": await self._analyze_file_security(file_path)
        }
    
    async def _calculate_hashes(self, file_path: Path) -> Dict[str, str]:
        """Calculate MD5, SHA1, SHA256, and SHA512 hashes"""
        # Real hash calculation with security notes
        return {
            "md5": md5_hash.hexdigest(),      # Legacy compatibility
            "sha1": sha1_hash.hexdigest(),    # Legacy compatibility
            "sha256": sha256_hash.hexdigest(), # Primary security hash
            "sha512": sha512_hash.hexdigest(), # Additional security hash
            "_security_note": "Use SHA256 or SHA512 for security-critical applications"
        }
```

### Creating Custom Agents

1. **Inherit from Base Agent**

```python
from amas.agents.base import IntelligenceAgent

class CustomAgent(IntelligenceAgent):
    """Custom agent implementation"""
    
    def __init__(self, agent_id: str, **kwargs):
        super().__init__(agent_id, **kwargs)
        self.capabilities = ["custom_capability"]
    
    def __init__(self, service_manager: ServiceManager):
        self.service_manager = service_manager
        self.agents = {}
        self.task_queue = TaskQueue()
        self.event_bus = EventBus()
        self.provider_manager = ProviderManager()
        self.ml_engine = MLDecisionEngine()
        
    async def submit_task(self, agent_type: str, description: str, priority: int = 2) -> str:
        """Submit a task to the unified orchestrator."""
        task = IntelligenceTask(
            agent_type=agent_type,
            description=description,
            priority=priority,
            status=TaskStatus.PENDING
        )
        
        # Add to priority queue
        await self.task_queue.put(task)
        return task.task_id
        
    async def execute_task(self, task: Task) -> TaskResult:
        """Execute a task using appropriate agents with ML optimization."""
        # Task allocation using ML decision engine
        agents = await self.ml_engine.allocate_agents(task)
        
        # Select optimal AI provider
        provider = await self.provider_manager.get_optimal_provider(task)
        
        # Create workflow with optimizations
        workflow = self.create_workflow(task, agents, provider)
        
        # Execute workflow with monitoring
        results = await workflow.execute()
        
        # Learn from execution
        await self.ml_engine.record_execution(task, results)
        
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

#### New Test Infrastructure
```bash
# Run comprehensive test suite
python scripts/run_tests.py --all --verbose

# Run specific test types
python scripts/run_tests.py --unit --verbose
python scripts/run_tests.py --integration --verbose
python scripts/run_tests.py --benchmark --verbose

# Run with coverage
python scripts/run_tests.py --coverage --verbose

# Run specific test file
python scripts/run_tests.py --test tests/test_unified_orchestrator.py
```

#### Traditional pytest commands
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
pytest --cov=src/amas --cov-report=html

# Run specific test category
pytest tests/unit/
pytest tests/integration/

# Run specific test file
pytest tests/test_unified_orchestrator.py

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

#### New Test Infrastructure
```bash
# Run comprehensive test suite
python scripts/run_tests.py --all --verbose

# Run specific test types
python scripts/run_tests.py --unit --verbose
python scripts/run_tests.py --integration --verbose
python scripts/run_tests.py --benchmark --verbose

# Run tests with coverage
python scripts/run_tests.py --all --coverage

# Run specific test file
python scripts/run_tests.py --test tests/test_unified_orchestrator.py
```

#### Real Functionality Tests
```bash
# Test real OSINT functionality
python -m pytest tests/test_unified_orchestrator.py::TestOSINTAgentRealImplementation -v

# Test real forensics functionality
python -m pytest tests/test_unified_orchestrator.py::TestForensicsAgentRealImplementation -v

# Test unified orchestrator
python -m pytest tests/test_unified_orchestrator.py::TestUnifiedIntelligenceOrchestrator -v
```

#### Performance Benchmarking
```bash
# Run comprehensive benchmarks
python scripts/benchmark_system.py --mode basic --output results.json

# Run specific benchmark types
python scripts/benchmark_system.py --mode basic --benchmark latency
python scripts/benchmark_system.py --mode basic --benchmark throughput
python scripts/benchmark_system.py --mode basic --benchmark failover
```

## Performance Optimization

### GPU Optimization

```python
# Optimize for GPU usage
config = {
    'gpu_enabled': True,
    'gpu_memory_fraction': 0.8,
    'mixed_precision': True,
    'batch_size': 32
}
```

### Memory Management

```python
# Memory-efficient processing
async def process_large_dataset(data):
    """Process data in chunks to manage memory"""
    chunk_size = 1000
    for chunk in chunks(data, chunk_size):
        result = await process_chunk(chunk)
        yield result
```

### Caching Strategy

```python
# Implement intelligent caching
@cached(ttl=3600)  # Cache for 1 hour
async def expensive_computation(params):
    """Cache expensive computations"""
    return await perform_computation(params)
```

## Security Implementation

### Authentication & Authorization

```python
# JWT-based authentication
from amas.security import SecurityService

security = SecurityService(config)
token = await security.authenticate_user(username, password)
permissions = await security.get_user_permissions(user_id)
```

### Data Encryption

```python
# Encrypt sensitive data
from amas.security.encryption import EncryptionService

encryption = EncryptionService(config.encryption_key)
encrypted_data = encryption.encrypt(sensitive_data)
decrypted_data = encryption.decrypt(encrypted_data)
```

### Audit Logging

```python
# Comprehensive audit logging
from amas.security.audit import AuditLogger

audit = AuditLogger()
await audit.log_action(
    user_id="user123",
    action="task_submission",
    resource="task_456",
    result="success",
    metadata={"task_type": "research"}
)
```

## Advanced Topics

### Custom ReAct Implementations

```python
class CustomReActAgent(ReactAgent):
    """Custom ReAct implementation"""
    
    async def reason(self, context: Dict) -> Reasoning:
        """Custom reasoning logic"""
        prompt = self.build_reasoning_prompt(context)
        response = await self.llm_service.generate(prompt)
        return self.parse_reasoning(response)
    
    async def act(self, reasoning: Reasoning) -> ActionResult:
        """Custom action execution"""
        action = reasoning.planned_action
        return await self.execute_action(action)
    
    async def observe(self, action_result: ActionResult) -> Observation:
        """Custom observation and learning"""
        return Observation(
            success=action_result.success,
            insights=self.extract_insights(action_result),
            next_steps=self.determine_next_steps(action_result)
        )
```

### Multi-Agent Coordination

```python
class CoordinatedWorkflow:
    """Multi-agent workflow coordination"""
    
    async def execute_parallel_tasks(self, tasks: List[Task]) -> List[TaskResult]:
        """Execute tasks in parallel across multiple agents"""
        agent_assignments = await self.assign_tasks_to_agents(tasks)
        
        # Execute tasks concurrently
        results = await asyncio.gather(*[
            agent.execute_task(task) 
            for agent, task in agent_assignments
        ])
        
        return results
    
    async def execute_sequential_workflow(self, workflow: Workflow) -> WorkflowResult:
        """Execute dependent tasks in sequence"""
        results = []
        context = {}
        
        for step in workflow.steps:
            # Use previous results as context
            step.context.update(context)
            result = await self.execute_step(step)
            results.append(result)
            context.update(result.output)
        
        return WorkflowResult(steps=results, final_output=context)
```

### Performance Monitoring

```python
from amas.monitoring import PerformanceMonitor

class MonitoredAgent(IntelligenceAgent):
    """Agent with performance monitoring"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitor = PerformanceMonitor(self.agent_id)
    
    async def execute_task(self, task: Task) -> TaskResult:
        """Monitored task execution"""
        with self.monitor.measure_execution():
            result = await super().execute_task(task)
            
        # Record metrics
        await self.monitor.record_task_completion(
            task_type=task.type,
            execution_time=self.monitor.last_execution_time,
            success=result.status == "completed"
        )
        
        return result
```

## API Development

### Creating New Endpoints

```python
from fastapi import APIRouter, Depends
from amas.api.auth import get_current_user
from amas.api.models import TaskRequest, TaskResponse

router = APIRouter(prefix="/api/v1/custom")

@router.post("/submit-custom-task", response_model=TaskResponse)
async def submit_custom_task(
    request: TaskRequest,
    current_user = Depends(get_current_user)
):
    """Submit a custom task"""
    # Validate permissions
    if not current_user.has_permission("submit_custom_tasks"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Process task
    task_id = await orchestrator.submit_task(
        task_type="custom",
        description=request.description,
        user_id=current_user.id
    )
    
    return TaskResponse(task_id=task_id, status="submitted")
```

### API Security

```python
from amas.api.middleware import SecurityMiddleware

# Add security middleware
app.add_middleware(SecurityMiddleware)

# Rate limiting
from amas.api.rate_limiting import RateLimiter
rate_limiter = RateLimiter(requests_per_minute=100)

@router.get("/protected-endpoint")
@rate_limiter.limit("10/minute")
async def protected_endpoint():
    """Rate-limited protected endpoint"""
    return {"message": "Protected data"}
```

## Database Schema

### Core Tables

```sql
-- agents table
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    capabilities JSONB,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id VARCHAR(255) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    parameters JSONB,
    priority INTEGER DEFAULT 2,
    status VARCHAR(20) DEFAULT 'pending',
    assigned_agent_id VARCHAR(255),
    result JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    FOREIGN KEY (assigned_agent_id) REFERENCES agents(agent_id)
);

-- audit_logs table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(255),
    result VARCHAR(20),
    metadata JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

## Configuration Management

### Environment-Based Configuration

```python
# config/settings.py
class AMASConfig(BaseSettings):
    """Environment-aware configuration"""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @validator('database_url')
    def validate_database_url(cls, v):
        """Validate database connection string"""
        if not v.startswith(('postgresql://', 'sqlite://')):
            raise ValueError('Invalid database URL')
        return v
```

### Configuration Profiles

```yaml
# config/profiles/development.yaml
app:
  debug: true
  log_level: DEBUG

database:
  host: localhost
  port: 5432

llm:
  model: llama3.1:8b  # Smaller model for development

# config/profiles/production.yaml
app:
  debug: false
  log_level: INFO

database:
  host: db.production.internal
  port: 5432

llm:
  model: llama3.1:70b  # Full model for production
```

## Deployment

### Development Environment

#### Docker Compose Development Setup
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  amas-dev:
    build: .
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - GLM_API_KEY=${GLM_API_KEY}
      - GROK_API_KEY=${GROK_API_KEY}
      - AMAS_CONFIG_MODE=${AMAS_CONFIG_MODE:-basic}
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src
      - ./tests:/app/tests
      - ./scripts:/app/scripts
    command: python scripts/validate_env.py --mode basic && uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000 --reload

  postgres-dev:
    image: postgres:15
    environment:
      - POSTGRES_DB=amas
      - POSTGRES_USER=amas
      - POSTGRES_PASSWORD=amas_password
    ports:
      - "5432:5432"

  redis-dev:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  neo4j-dev:
    image: neo4j:5
    environment:
      - NEO4J_AUTH=neo4j/amas_password
    ports:
      - "7474:7474"
      - "7687:7687"
```

#### Quick Start
```bash
# Start complete development environment
docker-compose -f docker-compose.dev.yml up -d

# Check services
docker-compose -f docker-compose.dev.yml ps

# View logs
docker-compose -f docker-compose.dev.yml logs -f amas-dev
```

### Production Deployment

```dockerfile
# Multi-stage production Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim as production

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY tests/ ./tests/

# Health check with validation
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python scripts/validate_env.py --mode basic --skip-db || exit 1

EXPOSE 8000
CMD ["uvicorn", "src.amas.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: amas-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: amas-api
  template:
    metadata:
      labels:
        app: amas-api
    spec:
      containers:
      - name: amas-api
        image: amas:latest
        ports:
        - containerPort: 8000
        env:
        - name: AMAS_ENVIRONMENT
          value: "production"
        resources:
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

## Best Practices

### Code Quality

1. **Type Hints**: Use comprehensive type annotations
2. **Docstrings**: Document all public APIs
3. **Error Handling**: Implement proper exception handling
4. **Testing**: Maintain 90%+ code coverage
5. **Security**: Follow security best practices

### Performance

1. **Async Operations**: Use async/await for I/O operations
2. **Connection Pooling**: Reuse database connections
3. **Caching**: Cache expensive computations
4. **Monitoring**: Track performance metrics
5. **Profiling**: Regular performance analysis

### Security

1. **Input Validation**: Validate all inputs
2. **Authentication**: Implement proper auth flows
3. **Authorization**: Use role-based access control
4. **Encryption**: Encrypt sensitive data
5. **Audit Logging**: Log all security events

## Contributing

### Development Setup

#### Quick Start with Docker
```bash
# Clone repository
git clone <repository-url>
cd Advanced-Multi-Agent-Intelligence-System

# Set minimal API keys
export DEEPSEEK_API_KEY="your_key"
export GLM_API_KEY="your_key"
export GROK_API_KEY="your_key"

# Start complete development environment
docker-compose -f docker-compose.dev.yml up -d

# Verify setup
python scripts/verify_implementation.py
```

#### Local Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Validate environment
python scripts/validate_env.py --mode basic --verbose

# Run tests
python scripts/run_tests.py --all --verbose

# Start development server
python -m uvicorn src.amas.api.main:app --reload
```

#### Traditional Setup
```bash
# Clone repository
git clone <repository-url>
cd Advanced-Multi-Agent-Intelligence-System

# Install development dependencies
pip install -e .[dev]

# Setup pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Pull Request Process

1. Create feature branch from `main`
2. Implement changes with tests
3. Ensure all tests pass
4. Update documentation
5. Submit pull request

### Code Review Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Security review completed
- [ ] Performance impact assessed

### Test Coverage Goals

- **Unit Tests**: 85%+ coverage
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