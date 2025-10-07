# AMAS Developer Guide

This guide covers the technical aspects of AMAS development, architecture, and advanced customization.

**✅ 100% Implementation Verified** - All critical improvements from the project audit have been implemented and verified.

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

### 1. Unified Orchestrator (`src/amas/core/unified_orchestrator.py`)

The heart of AMAS, implementing the unified orchestrator with provider management:

```python
class UnifiedIntelligenceOrchestrator:
    """
    Unified orchestrator with provider management and circuit breakers:
    - Provider Management: Multi-AI provider support with fallback
    - Circuit Breakers: Robust error handling and recovery
    - Task Queue: Priority-based task management
    - Performance Monitoring: Real-time metrics and health tracking
    """
    
    async def submit_task(self, agent_type: str, description: str, priority: int = 2) -> str:
        """Submit a task to the unified orchestrator"""
        task = IntelligenceTask(
            agent_type=agent_type,
            description=description,
            priority=priority,
            status=TaskStatus.PENDING
        )
        
        # Add to priority queue
        await self.task_queue.put(task)
        return task.task_id
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "available_agents": len(self.agents),
            "active_tasks": len(self.active_tasks),
            "provider_health": await self.provider_manager.get_health_status(),
            "performance_metrics": self.performance_metrics
        }
```

### 2. Provider Manager (`src/amas/core/unified_orchestrator.py`)

Manages AI providers with circuit breakers and fallback:

```python
class ProviderManager:
    """Provider management with circuit breakers and fallback"""
    
    def __init__(self):
        self.providers = {}
        self.circuit_breakers = {}
        self.provider_stats = {}
    
    async def get_available_provider(self) -> Optional[str]:
        """Get an available provider with circuit breaker logic"""
        for provider_id, breaker in self.circuit_breakers.items():
            if breaker.can_execute():
                return provider_id
        return None
    
    async def record_success(self, provider_id: str):
        """Record successful provider call"""
        self.provider_stats[provider_id]["success_count"] += 1
        self.circuit_breakers[provider_id].record_success()
    
    async def record_failure(self, provider_id: str):
        """Record failed provider call"""
        self.provider_stats[provider_id]["failure_count"] += 1
        self.circuit_breakers[provider_id].record_failure()
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
pytest --cov=src/amas --cov-report=html

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/e2e/           # E2E tests only

# Run specific test file
pytest tests/test_unified_orchestrator.py

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

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

---

For more information, see:
- [API Documentation](../api/README.md)
- [Security Guide](security.md)
- [Performance Guide](performance.md)