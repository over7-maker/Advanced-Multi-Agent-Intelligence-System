# Contributing to AMAS

Thank you for your interest in contributing to the Advanced Multi-Agent Intelligence System (AMAS)! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.9+ (3.11 recommended)
- Git
- Docker and Docker Compose
- NVIDIA GPU with CUDA support (recommended)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/Advanced-Multi-Agent-Intelligence-System.git
   cd Advanced-Multi-Agent-Intelligence-System
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e .[dev]
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

5. **Start Development Services**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

6. **Run Tests**
   ```bash
   pytest
   ```

## 🔧 Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow our coding standards:
- Use type hints for all functions
- Add comprehensive docstrings
- Follow PEP 8 style guidelines
- Write tests for new functionality

### 3. Run Quality Checks

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/

# Run tests
pytest

# Security check
bandit -r src/
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new agent capability for sentiment analysis"
```

We use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test additions/modifications
- `chore:` - Maintenance tasks

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## 📝 Code Standards

### Python Code Style

We follow PEP 8 with some modifications:

```python
# Good example
from typing import Dict, List, Optional, Any
import asyncio
import logging

class ResearchAgent(IntelligenceAgent):
    """
    Research agent for autonomous information gathering and analysis.
    
    This agent specializes in:
    - Literature review and synthesis
    - Trend analysis and forecasting
    - Data correlation and insights
    """
    
    def __init__(
        self, 
        agent_id: str,
        config: AgentConfig,
        llm_service: LLMService
    ) -> None:
        """Initialize the research agent."""
        super().__init__(agent_id, config)
        self.llm_service = llm_service
        self.logger = logging.getLogger(f"amas.agents.{agent_id}")
    
    async def execute_task(self, task: Task) -> TaskResult:
        """
        Execute a research task.
        
        Args:
            task: The research task to execute
            
        Returns:
            TaskResult with research findings and analysis
            
        Raises:
            TaskExecutionError: If task cannot be completed
        """
        try:
            self.logger.info(f"Starting research task: {task.id}")
            
            # Implementation here
            result = await self._perform_research(task)
            
            return TaskResult(
                task_id=task.id,
                status="completed",
                result=result
            )
            
        except Exception as e:
            self.logger.error(f"Research task failed: {e}")
            raise TaskExecutionError(f"Research failed: {e}") from e
```

### Documentation Standards

#### Docstring Format

Use Google-style docstrings:

```python
def process_data(data: List[Dict[str, Any]], threshold: float = 0.5) -> ProcessedData:
    """
    Process raw data and extract meaningful insights.
    
    This function performs data cleaning, normalization, and feature extraction
    to prepare data for analysis by AI agents.
    
    Args:
        data: List of raw data dictionaries to process
        threshold: Minimum confidence threshold for data inclusion (default: 0.5)
        
    Returns:
        ProcessedData object containing cleaned and normalized data
        
    Raises:
        DataProcessingError: If data cannot be processed
        ValueError: If threshold is not between 0 and 1
        
    Example:
        >>> raw_data = [{"text": "Sample data", "score": 0.8}]
        >>> processed = process_data(raw_data, threshold=0.7)
        >>> print(processed.features)
        ['normalized_text', 'confidence_score']
    """
```

#### Code Comments

```python
# Good: Explain why, not what
# Use exponential backoff to handle rate limiting gracefully
retry_delay = min(2 ** attempt, 60)

# Bad: Explain what (obvious from code)
# Set retry delay to 2 to the power of attempt
retry_delay = 2 ** attempt
```

### Testing Requirements

#### Test Coverage

- **Minimum**: 90% code coverage
- **Critical paths**: 100% coverage for security and core functionality
- **New features**: All new code must include tests

#### Test Types

1. **Unit Tests** (`tests/unit/`)
   ```python
   import pytest
   from amas.agents.research import ResearchAgent
   
   @pytest.mark.asyncio
   async def test_research_agent_initialization():
       """Test research agent initialization"""
       agent = ResearchAgent("test_agent", config, llm_service)
       assert agent.agent_id == "test_agent"
       assert "literature_review" in agent.capabilities
   ```

2. **Integration Tests** (`tests/integration/`)
   ```python
   @pytest.mark.asyncio
   async def test_task_submission_workflow():
       """Test complete task submission and execution"""
       app = AMASApplication(test_config)
       await app.initialize()
       
       task_id = await app.submit_task({
           'type': 'research',
           'description': 'Test research task'
       })
       
       # Wait for completion
       result = await app.get_task_result(task_id)
       assert result['status'] == 'completed'
   ```

3. **End-to-End Tests** (`tests/e2e/`)
   ```python
   async def test_full_system_scenario():
       """Test complete user scenario from UI to result"""
       # Test web interface interaction
       # Test API responses
       # Verify data persistence
   ```

### Performance Guidelines

#### Async/Await Usage

```python
# Good: Proper async usage
async def process_multiple_tasks(tasks: List[Task]) -> List[TaskResult]:
    """Process multiple tasks concurrently"""
    return await asyncio.gather(*[
        process_single_task(task) for task in tasks
    ])

# Bad: Blocking in async function
async def bad_processing(tasks: List[Task]) -> List[TaskResult]:
    """Don't do this - blocks the event loop"""
    results = []
    for task in tasks:
        result = process_single_task_sync(task)  # Blocking!
        results.append(result)
    return results
```

#### Memory Management

```python
# Good: Memory-efficient processing
async def process_large_dataset(data_stream):
    """Process data in chunks to manage memory"""
    async for chunk in data_stream.chunks(size=1000):
        processed = await process_chunk(chunk)
        yield processed
        # Chunk is automatically garbage collected

# Bad: Loading everything into memory
async def bad_processing(data_stream):
    """Don't do this - memory intensive"""
    all_data = await data_stream.read_all()  # Could be GBs!
    return await process_all(all_data)
```

## 🏗️ Architecture Contributions

### Adding New Agents

1. **Create Agent Class**
   ```python
   # src/amas/agents/your_agent/your_agent.py
   from amas.agents.base import IntelligenceAgent
   
   class YourAgent(IntelligenceAgent):
       """Your specialized agent"""
       
       capabilities = ["your_capability"]
       supported_task_types = ["your_task_type"]
   ```

2. **Add Tests**
   ```python
   # tests/unit/test_your_agent.py
   ```

3. **Update Configuration**
   ```python
   # Register in orchestrator initialization
   ```

4. **Update Documentation**
   ```markdown
   # Add to docs/user/README.md and docs/developer/README.md
   ```

### Adding New Services

1. **Implement Service Interface**
   ```python
   from amas.services.base import BaseService
   
   class YourService(BaseService):
       """Your external service integration"""
   ```

2. **Add to Service Manager**
   ```python
   # Update src/amas/services/service_manager.py
   ```

3. **Add Configuration**
   ```python
   # Update src/amas/config/settings.py
   ```

## 📊 Performance Contributions

### Benchmarking

Before and after performance changes:

```bash
# Run performance benchmarks
python scripts/development/benchmark_system.py

# Profile specific components
python -m cProfile -o profile.stats scripts/profile_agents.py
```

### Memory Profiling

```bash
# Memory usage profiling
mprof run python main.py
mprof plot
```

### Load Testing

```bash
# API load testing
locust -f tests/load/test_api.py --host=http://localhost:8000
```

## 🔒 Security Contributions

### Security Review Process

1. **Threat Modeling**: Document security implications
2. **Code Review**: All security-related changes require 2+ reviews
3. **Testing**: Include security test cases
4. **Documentation**: Update security documentation

### Security Testing

```bash
# Security scanning
bandit -r src/
safety check
semgrep --config=auto src/

# Dependency checking
pip-audit
```

## 📚 Documentation Contributions

### Documentation Types

1. **User Documentation** (`docs/user/`)
   - Getting started guides
   - Feature explanations
   - Troubleshooting help

2. **Developer Documentation** (`docs/developer/`)
   - Architecture details
   - API specifications
   - Development guides

3. **API Documentation** (`docs/api/`)
   - Endpoint documentation
   - Example requests/responses
   - SDK documentation

### Documentation Style

- Use clear, concise language
- Include practical examples
- Provide context and rationale
- Keep content up-to-date
- Use proper markdown formatting

## 🐛 Bug Reports

### Bug Report Template

```markdown
**Bug Description**
A clear description of the bug.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.11.5]
- AMAS version: [e.g., 1.0.0]
- GPU: [e.g., RTX 4080 SUPER]

**Logs**
Relevant log output (please use code blocks).

**Additional Context**
Any other context about the problem.
```

## ✨ Feature Requests

### Feature Request Template

```markdown
**Feature Description**
A clear description of the desired feature.

**Use Case**
Describe the problem this feature would solve.

**Proposed Solution**
Your proposed implementation approach.

**Alternatives Considered**
Other approaches you've considered.

**Additional Context**
Screenshots, mockups, or other relevant information.
```

## 🔄 Pull Request Process

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Tests added for new functionality
- [ ] All tests pass locally
- [ ] Documentation updated
- [ ] Changelog updated (if applicable)
- [ ] Security implications considered
- [ ] Performance impact assessed

### PR Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix/feature causing existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Security
- [ ] Security implications reviewed
- [ ] No sensitive data exposed
- [ ] Authentication/authorization updated if needed

## Performance
- [ ] Performance impact assessed
- [ ] Benchmarks run (if applicable)
- [ ] Memory usage considerations

## Documentation
- [ ] Code comments added/updated
- [ ] User documentation updated
- [ ] API documentation updated
```

## 🏆 Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Project README
- Annual contributor awards

## 📞 Getting Help

- **Documentation**: Comprehensive guides in `docs/`
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Community discussions and Q&A
- **Discord**: Real-time community chat (link in README)

## 📄 License

By contributing to AMAS, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to the future of autonomous AI intelligence!** 🤖✨