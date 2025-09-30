# AMAS Developer Guide

This guide covers the technical aspects of AMAS development, architecture, and advanced customization.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Agent Development](#agent-development)
4. [Service Integration](#service-integration)
5. [Testing](#testing)
6. [Performance Optimization](#performance-optimization)
7. [Security Implementation](#security-implementation)

## Architecture Overview

### System Architecture

AMAS follows a modular, microservices-inspired architecture with the following key components:

```
┌─────────────────────────────────────────────────────────────┐
│                    AMAS System Architecture                  │
├─────────────────────────────────────────────────────────────┤
│  Frontend Layer                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Web UI      │  │ Desktop App │  │ CLI Tools   │         │
│  │ (React)     │  │ (Electron)  │  │ (Click)     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  API Gateway Layer                                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │            FastAPI Backend (Load Balanced)              │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Core Intelligence Layer                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Agent Orchestrator                         │ │
│  │              (ReAct Engine)                             │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Service Layer                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ LLM Service │  │Vector Service│  │Graph Service│         │
│  │ (Ollama)    │  │ (FAISS)     │  │ (Neo4j)     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ PostgreSQL  │  │ Redis Cache │  │ File Storage│         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Modularity**: Each component is independently deployable and testable
2. **Scalability**: Horizontal scaling through containerization
3. **Security**: Zero-trust architecture with end-to-end encryption
4. **Observability**: Comprehensive logging, metrics, and tracing
5. **Reliability**: Fault tolerance and graceful degradation

## Core Components

### 1. Agent Orchestrator (`src/amas/core/orchestrator.py`)

The heart of AMAS, implementing the ReAct framework:

```python
class IntelligenceOrchestrator:
    """
    Core orchestrator implementing ReAct pattern:
    - Reasoning: LLM-based task analysis
    - Acting: Agent action execution
    - Observing: Result evaluation and next step determination
    """
    
    async def execute_react_cycle(self, task_id: str) -> List[ReActStep]:
        """Execute full ReAct cycle for a task"""
        steps = []
        while not self.is_task_complete(task_id):
            # Reasoning phase
            reasoning = await self.reason_about_task(task_id)
            
            # Acting phase
            action_result = await self.execute_action(reasoning.action)
            
            # Observing phase
            observation = await self.observe_result(action_result)
            
            steps.append(ReActStep(reasoning, action_result, observation))
            
        return steps
```

### 2. Service Manager (`src/amas/services/service_manager.py`)

Manages all external service connections:

```python
class ServiceManager:
    """Centralized service management"""
    
    async def initialize_all_services(self):
        """Initialize all required services"""
        await asyncio.gather(
            self.initialize_llm_service(),
            self.initialize_vector_service(),
            self.initialize_graph_service(),
            self.initialize_database_service(),
            self.initialize_cache_service()
        )
```

### 3. Configuration System (`src/amas/config/settings.py`)

Centralized configuration using Pydantic:

```python
class AMASConfig(BaseSettings):
    """Type-safe configuration with environment variable support"""
    
    app_name: str = Field(default="AMAS", env="AMAS_APP_NAME")
    environment: str = Field(default="development", env="AMAS_ENVIRONMENT")
    
    # Nested configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
```

## Agent Development

### Creating Custom Agents

1. **Inherit from Base Agent**

```python
from amas.agents.base import IntelligenceAgent

class CustomAgent(IntelligenceAgent):
    """Custom agent implementation"""
    
    def __init__(self, agent_id: str, **kwargs):
        super().__init__(agent_id, **kwargs)
        self.capabilities = ["custom_capability"]
    
    async def execute_task(self, task: Task) -> TaskResult:
        """Implement your custom logic here"""
        return TaskResult(
            task_id=task.id,
            status="completed",
            result={"message": "Custom task completed"}
        )
```

2. **Register Your Agent**

```python
# In your initialization code
custom_agent = CustomAgent("custom_001")
await orchestrator.register_agent(custom_agent)
```

### Agent Communication

Agents can communicate through the message system:

```python
# Send message to another agent
await self.send_message(
    recipient_id="other_agent_001",
    message_type="collaboration_request",
    data={"task_id": task.id, "request": "data_analysis"}
)

# Handle incoming messages
async def handle_message(self, message: AgentMessage):
    if message.type == "collaboration_request":
        # Process collaboration request
        return await self.process_collaboration(message.data)
```

### Agent Capabilities

Define agent capabilities for intelligent task routing:

```python
class ResearchAgent(IntelligenceAgent):
    capabilities = [
        "literature_review",
        "trend_analysis", 
        "data_synthesis",
        "report_generation"
    ]
    
    supported_task_types = [
        "research",
        "analysis",
        "reporting"
    ]
```

## Service Integration

### Adding New Services

1. **Create Service Class**

```python
from amas.services.base import BaseService

class CustomService(BaseService):
    """Custom external service integration"""
    
    async def initialize(self):
        """Service initialization"""
        pass
    
    async def health_check(self) -> bool:
        """Health check implementation"""
        return True
```

2. **Register in Service Manager**

```python
# In service_manager.py
async def initialize_custom_service(self):
    """Initialize custom service"""
    self.custom_service = CustomService(self.config.custom_service)
    await self.custom_service.initialize()
```

### External API Integration

For external APIs, implement the standard interface:

```python
class ExternalAPIService(BaseService):
    """Template for external API services"""
    
    def __init__(self, config):
        self.api_key = config.api_key
        self.base_url = config.base_url
        self.session = aiohttp.ClientSession()
    
    async def make_request(self, endpoint: str, data: Dict) -> Dict:
        """Standardized API request method"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with self.session.post(
            f"{self.base_url}/{endpoint}", 
            json=data, 
            headers=headers
        ) as response:
            return await response.json()
```

## Testing

### Test Structure

```
tests/
├── unit/                 # Unit tests for individual components
│   ├── test_agents.py    # Agent unit tests
│   ├── test_services.py  # Service unit tests
│   └── test_config.py    # Configuration tests
├── integration/          # Integration tests
│   ├── test_workflows.py # End-to-end workflow tests
│   └── test_api.py       # API integration tests
└── e2e/                  # End-to-end system tests
    └── test_scenarios.py # Complete scenario tests
```

### Writing Tests

#### Unit Tests
```python
import pytest
from amas.agents.research import ResearchAgent

@pytest.fixture
async def research_agent():
    agent = ResearchAgent("test_agent")
    await agent.initialize()
    return agent

async def test_research_task_execution(research_agent):
    """Test research task execution"""
    task = Task(
        id="test_task",
        type="research",
        description="Test research task"
    )
    
    result = await research_agent.execute_task(task)
    assert result.status == "completed"
    assert "research_data" in result.result
```

#### Integration Tests
```python
async def test_full_workflow():
    """Test complete agent workflow"""
    app = AMASApplication(test_config)
    await app.initialize()
    
    task_id = await app.submit_task({
        'type': 'research',
        'description': 'Test research workflow'
    })
    
    result = await app.get_task_result(task_id)
    assert result['status'] == 'completed'
    
    await app.shutdown()
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=amas --cov-report=html

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/e2e/           # E2E tests only

# Run specific test file
pytest tests/unit/test_agents.py

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
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

### Docker Deployment

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
COPY config/ ./config/

EXPOSE 8000
CMD ["uvicorn", "amas.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
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

---

For more information, see:
- [API Documentation](../api/README.md)
- [Security Guide](security.md)
- [Performance Guide](performance.md)