# AMAS Examples & Demos
## Advanced Multi-Agent AI System - Practical Examples

### Quick Start Examples

#### 1. Basic Agent Orchestration Demo

```python
# examples/basic_orchestration.py
import asyncio
from agents.orchestrator import AgentOrchestrator, Agent, AgentType, Task, TaskStatus

async def basic_demo():
    # Initialize orchestrator
    config = {
        'llm_service_url': 'http://localhost:11434',
        'vector_service_url': 'http://localhost:8001',
        'graph_service_url': 'bolt://localhost:7687'
    }
    
    orchestrator = AgentOrchestrator(config)
    
    # Register agents
    research_agent = Agent(
        name="Research Agent",
        type=AgentType.RESEARCH,
        capabilities=["web_search", "data_analysis"]
    )
    
    await orchestrator.register_agent(research_agent)
    
    # Submit task
    task = Task(
        id="demo-task-1",
        type="research",
        description="Research the latest AI developments and create a summary"
    )
    
    task_id = await orchestrator.submit_task(task)
    await orchestrator.assign_task_to_agent(task_id, research_agent.id)
    
    # Execute ReAct cycle
    react_steps = await orchestrator.execute_react_cycle(task_id)
    
    print(f"Task completed in {len(react_steps)} steps")
    return react_steps

if __name__ == "__main__":
    asyncio.run(basic_demo())
```

#### 2. Multi-Agent Research Pipeline

```python
# examples/research_pipeline.py
import asyncio
from agents.orchestrator import AgentOrchestrator, Agent, AgentType, Task

async def research_pipeline_demo():
    orchestrator = AgentOrchestrator({
        'llm_service_url': 'http://localhost:11434',
        'vector_service_url': 'http://localhost:8001'
    })
    
    # Register specialized agents
    agents = [
        Agent(name="Web Scraper", type=AgentType.RESEARCH, capabilities=["web_scraping"]),
        Agent(name="Data Analyst", type=AgentType.ANALYSIS, capabilities=["data_analysis"]),
        Agent(name="Report Writer", type=AgentType.RESEARCH, capabilities=["report_generation"])
    ]
    
    for agent in agents:
        await orchestrator.register_agent(agent)
    
    # Create research pipeline
    tasks = [
        Task(id="scrape-1", type="research", description="Scrape latest AI news"),
        Task(id="analyze-1", type="analysis", description="Analyze scraped data"),
        Task(id="report-1", type="research", description="Generate research report")
    ]
    
    # Execute pipeline
    for task in tasks:
        task_id = await orchestrator.submit_task(task)
        # Assign to appropriate agent based on task type
        # ... assignment logic
    
    return "Research pipeline completed"

if __name__ == "__main__":
    asyncio.run(research_pipeline_demo())
```

### Advanced Examples

#### 3. AI-Powered Code Generation

```python
# examples/code_generation.py
import asyncio
from agents.orchestrator import AgentOrchestrator, Agent, AgentType, Task

async def code_generation_demo():
    orchestrator = AgentOrchestrator({
        'llm_service_url': 'http://localhost:11434'
    })
    
    # Register code agent
    code_agent = Agent(
        name="Code Generator",
        type=AgentType.CODE,
        capabilities=["python", "javascript", "api_development"]
    )
    
    await orchestrator.register_agent(code_agent)
    
    # Submit coding task
    task = Task(
        id="code-task-1",
        type="code",
        description="Create a REST API endpoint for user authentication with JWT tokens"
    )
    
    task_id = await orchestrator.submit_task(task)
    await orchestrator.assign_task_to_agent(task_id, code_agent.id)
    
    # Execute with code-specific ReAct cycle
    react_steps = await orchestrator.execute_react_cycle(task_id, max_steps=15)
    
    # Extract generated code
    generated_code = None
    for step in react_steps:
        if step.action == "code" and "python" in step.observation:
            generated_code = step.observation
            break
    
    return generated_code

if __name__ == "__main__":
    code = asyncio.run(code_generation_demo())
    print("Generated Code:")
    print(code)
```

#### 4. Autonomous Research Agent

```python
# examples/autonomous_research.py
import asyncio
from agents.orchestrator import AgentOrchestrator, Agent, AgentType, Task

async def autonomous_research_demo():
    orchestrator = AgentOrchestrator({
        'llm_service_url': 'http://localhost:11434',
        'vector_service_url': 'http://localhost:8001'
    })
    
    # Register autonomous research agent
    research_agent = Agent(
        name="Autonomous Researcher",
        type=AgentType.RESEARCH,
        capabilities=[
            "web_search", "data_analysis", "source_verification",
            "credibility_scoring", "knowledge_synthesis"
        ]
    )
    
    await orchestrator.register_agent(research_agent)
    
    # Submit complex research task
    task = Task(
        id="autonomous-research-1",
        type="research",
        description="""Conduct comprehensive research on quantum computing applications 
        in AI, including current developments, challenges, and future prospects. 
        Verify sources, score credibility, and synthesize findings into a detailed report."""
    )
    
    task_id = await orchestrator.submit_task(task)
    await orchestrator.assign_task_to_agent(task_id, research_agent.id)
    
    # Execute extended ReAct cycle for complex research
    react_steps = await orchestrator.execute_react_cycle(task_id, max_steps=25)
    
    # Analyze research process
    research_phases = {
        'initial_search': 0,
        'source_verification': 0,
        'data_analysis': 0,
        'synthesis': 0
    }
    
    for step in react_steps:
        if 'search' in step.action.lower():
            research_phases['initial_search'] += 1
        elif 'verify' in step.action.lower():
            research_phases['source_verification'] += 1
        elif 'analyze' in step.action.lower():
            research_phases['data_analysis'] += 1
        elif 'synthesize' in step.action.lower():
            research_phases['synthesis'] += 1
    
    return {
        'total_steps': len(react_steps),
        'research_phases': research_phases,
        'final_report': react_steps[-1].observation if react_steps else None
    }

if __name__ == "__main__":
    result = asyncio.run(autonomous_research_demo())
    print(f"Research completed in {result['total_steps']} steps")
    print(f"Research phases: {result['research_phases']}")
```

### Integration Examples

#### 5. Web Interface Integration

```javascript
// examples/web_integration.js
import { AMASService } from '../web/src/services/amasService';

class AMASWebDemo {
    constructor() {
        this.amasService = new AMASService();
    }
    
    async runDemo() {
        try {
            // Initialize connection
            await this.amasService.initialize();
            
            // Get system status
            const status = await this.amasService.getSystemStatus();
            console.log('System Status:', status);
            
            // Submit task via web interface
            const task = {
                type: 'research',
                description: 'Research the latest developments in AI agent systems',
                priority: 1
            };
            
            const taskId = await this.amasService.submitTask(task);
            console.log('Task submitted:', taskId);
            
            // Monitor task progress
            const progress = await this.amasService.getTaskProgress(taskId);
            console.log('Task progress:', progress);
            
            // Get task result
            const result = await this.amasService.getTaskResult(taskId);
            console.log('Task result:', result);
            
        } catch (error) {
            console.error('Demo failed:', error);
        }
    }
}

// Run demo
const demo = new AMASWebDemo();
demo.runDemo();
```

#### 6. CLI Integration

```python
# examples/cli_integration.py
import click
import asyncio
from agents.orchestrator import AgentOrchestrator

@click.group()
def cli():
    """AMAS CLI Demo"""
    pass

@cli.command()
@click.option('--task', required=True, help='Task description')
@click.option('--agent-type', default='research', help='Agent type')
async def submit_task(task, agent_type):
    """Submit a task to AMAS"""
    orchestrator = AgentOrchestrator({
        'llm_service_url': 'http://localhost:11434'
    })
    
    # Submit task
    task_id = await orchestrator.submit_task({
        'type': agent_type,
        'description': task
    })
    
    click.echo(f"Task submitted: {task_id}")

@cli.command()
@click.option('--task-id', required=True, help='Task ID')
async def get_result(task_id):
    """Get task result"""
    orchestrator = AgentOrchestrator({
        'llm_service_url': 'http://localhost:11434'
    })
    
    result = await orchestrator.get_task_result(task_id)
    click.echo(f"Result: {result}")

@cli.command()
async def system_status():
    """Get system status"""
    orchestrator = AgentOrchestrator({
        'llm_service_url': 'http://localhost:11434'
    })
    
    status = await orchestrator.get_system_status()
    click.echo(f"System Status: {status}")

if __name__ == '__main__':
    cli()
```

### Performance Examples

#### 7. Load Testing

```python
# examples/load_testing.py
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from agents.orchestrator import AgentOrchestrator, Agent, AgentType, Task

async def load_test_demo():
    orchestrator = AgentOrchestrator({
        'llm_service_url': 'http://localhost:11434'
    })
    
    # Register multiple agents
    agents = []
    for i in range(5):
        agent = Agent(
            name=f"Load Test Agent {i}",
            type=AgentType.RESEARCH,
            capabilities=["load_testing"]
        )
        await orchestrator.register_agent(agent)
        agents.append(agent)
    
    # Submit multiple tasks concurrently
    tasks = []
    for i in range(20):
        task = Task(
            id=f"load-test-{i}",
            type="research",
            description=f"Load test task {i}: Research AI performance optimization"
        )
        task_id = await orchestrator.submit_task(task)
        tasks.append(task_id)
    
    # Execute tasks concurrently
    start_time = time.time()
    
    async def execute_task(task_id):
        return await orchestrator.execute_react_cycle(task_id, max_steps=5)
    
    results = await asyncio.gather(*[execute_task(task_id) for task_id in tasks])
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"Load test completed:")
    print(f"Tasks: {len(tasks)}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per task: {total_time/len(tasks):.2f} seconds")
    print(f"Throughput: {len(tasks)/total_time:.2f} tasks/second")
    
    return results

if __name__ == "__main__":
    asyncio.run(load_test_demo())
```

### Security Examples

#### 8. Security Testing

```python
# examples/security_testing.py
import asyncio
from security.audit_logger import AuditLogger
from security.encryption_manager import EncryptionManager

async def security_test_demo():
    # Test encryption
    encryption_manager = EncryptionManager()
    
    test_data = "Sensitive AMAS data for testing"
    encrypted = encryption_manager.encrypt_data(test_data.encode(), "test_context")
    decrypted = encryption_manager.decrypt_data(encrypted)
    
    print(f"Original: {test_data}")
    print(f"Decrypted: {decrypted.decode()}")
    print(f"Encryption successful: {test_data == decrypted.decode()}")
    
    # Test audit logging
    audit_logger = AuditLogger()
    
    await audit_logger.log_security_event(
        event_type="authentication",
        user_id="test_user",
        resource="login",
        action="login_attempt",
        result="success",
        metadata={"ip_address": "127.0.0.1", "user_agent": "test"}
    )
    
    print("Security test completed successfully")

if __name__ == "__main__":
    asyncio.run(security_test_demo())
```

### Usage Instructions

1. **Prerequisites**: Ensure AMAS services are running
2. **Run Examples**: Execute examples with `python examples/[example_name].py`
3. **Monitor Results**: Check logs and system status
4. **Customize**: Modify examples for your specific use cases

### Example Outputs

Each example provides detailed output showing:
- Task execution steps
- Agent performance metrics
- System resource usage
- Security audit logs
- Error handling and recovery

These examples demonstrate the full capabilities of the AMAS system and provide a foundation for building custom AI agent workflows.
