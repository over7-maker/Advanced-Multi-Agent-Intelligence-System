# 🤝 Contributing to AMAS

Thank you for your interest in contributing to the Advanced Multi-Agent Intelligence System (AMAS)! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How to Contribute](#how-to-contribute)
4. [Development Setup](#development-setup)
5. [Code Style Guidelines](#code-style-guidelines)
6. [Commit Guidelines](#commit-guidelines)
7. [Pull Request Process](#pull-request-process)
8. [Testing Guidelines](#testing-guidelines)
9. [Documentation](#documentation)
10. [Community](#community)

---

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We pledge to:

- Be respectful and considerate in all interactions
- Welcome contributors from all backgrounds and experience levels
- Focus on what is best for the community and project
- Show empathy towards other community members

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on collaboration and problem-solving
- Help others learn and grow

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or insults
- Trolling or disruptive behavior
- Publishing others' private information
- Any conduct that creates an unsafe environment

### Reporting Issues

If you experience or witness unacceptable behavior, please report it to:
- Email: conduct@amas.ai
- Discord: Contact moderators
- GitHub: Use the report feature

---

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

1. **Git** installed and configured
2. **Python 3.11+** installed
3. **Docker** and **Docker Compose** (optional but recommended)
4. A **GitHub account**
5. Basic knowledge of:
   - Python programming
   - Git version control
   - REST APIs
   - Async programming (helpful)

### First Steps

1. **Fork the Repository**
   ```bash
   # Navigate to https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System
   # Click "Fork" button
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Advanced-Multi-Agent-Intelligence-System.git
   cd Advanced-Multi-Agent-Intelligence-System
   ```

3. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
   ```

4. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   
   # Install pre-commit hooks
   pre-commit install
   ```

---

## 🎯 How to Contribute

### Types of Contributions

#### 1. Bug Reports
Found a bug? Help us fix it!

- Check if the bug is already reported in [Issues](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues)
- If not, create a new issue with:
  - Clear, descriptive title
  - Steps to reproduce
  - Expected vs actual behavior
  - System information
  - Error messages/logs

**Bug Report Template:**
```markdown
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.11.5]
- AMAS Version: [e.g., 1.1.0]

## Additional Context
Any other relevant information
```

#### 2. Feature Requests
Have an idea for a new feature?

- Check existing [feature requests](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues?q=is%3Aissue+label%3Aenhancement)
- Create a new issue with:
  - Use case description
  - Proposed solution
  - Alternative approaches
  - Potential impact

**Feature Request Template:**
```markdown
## Feature Description
What feature would you like to see?

## Use Case
Why is this feature needed?

## Proposed Solution
How could this be implemented?

## Alternatives Considered
Other approaches you've thought about

## Additional Context
Mockups, examples, or references
```

#### 3. Code Contributions
Ready to write code?

**Good First Issues:**
- Look for issues labeled `good first issue`
- These are beginner-friendly tasks
- Great for getting familiar with the codebase

**Areas to Contribute:**
- New agent implementations
- AI provider integrations
- Performance optimizations
- Security enhancements
- Test coverage improvements
- Documentation updates

#### 4. Documentation
Documentation improvements are always welcome!

- Fix typos or clarify existing docs
- Add examples and tutorials
- Improve API documentation
- Create guides for common tasks
- Translate documentation

---

## 💻 Development Setup

### Full Development Environment

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install all dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
pip install -r requirements-monitoring.txt

# 4. Install development tools
pip install black isort mypy flake8 bandit pre-commit

# 5. Install pre-commit hooks
pre-commit install

# 6. Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 7. Start development services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 8. Run initial tests
pytest tests/
```

### IDE Configuration

#### VS Code
```json
// .vscode/settings.json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "editor.formatOnSave": true,
    "[python]": {
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

#### PyCharm
1. Set interpreter to virtual environment
2. Enable Black formatter
3. Configure pytest as test runner
4. Enable type checking

---

## 📝 Code Style Guidelines

### Python Style Guide

We follow PEP 8 with Black formatting:

```python
# Good example
from typing import List, Optional, Dict
import logging

from src.amas.agents.base import BaseAgent
from src.amas.core.models import Task, TaskResult

logger = logging.getLogger(__name__)


class SecurityAgent(BaseAgent):
    """Security analysis agent implementation.
    
    This agent specializes in security scanning and
    vulnerability assessment of targets.
    
    Attributes:
        scanner: The security scanner instance
        analyzer: The vulnerability analyzer
    """
    
    def __init__(self, config: Optional[Dict] = None) -> None:
        """Initialize the security agent.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(agent_id="security-agent", name="Security Agent")
        self.config = config or {}
        self._initialize_components()
    
    async def scan_target(
        self,
        target: str,
        scan_type: str = "basic",
        timeout: Optional[float] = None
    ) -> TaskResult:
        """Perform security scan on target.
        
        Args:
            target: The target to scan (URL or IP)
            scan_type: Type of scan to perform
            timeout: Optional timeout in seconds
            
        Returns:
            TaskResult containing scan findings
            
        Raises:
            ScanError: If scan fails
            ValidationError: If target is invalid
        """
        logger.info(f"Starting {scan_type} scan on {target}")
        
        # Validate target
        if not self._is_valid_target(target):
            raise ValidationError(f"Invalid target: {target}")
        
        # Perform scan
        try:
            results = await self._execute_scan(target, scan_type, timeout)
            return TaskResult(
                status="completed",
                data=results,
                metadata={"scan_type": scan_type}
            )
        except Exception as e:
            logger.error(f"Scan failed: {e}")
            raise ScanError(f"Failed to scan {target}: {e}")
```

### Code Style Rules

1. **Formatting**: Use Black with default settings
2. **Imports**: Use isort for import ordering
3. **Type Hints**: Always use type hints
4. **Docstrings**: Google-style docstrings
5. **Line Length**: 88 characters (Black default)
6. **Naming**:
   - Classes: `PascalCase`
   - Functions/Variables: `snake_case`
   - Constants: `UPPER_SNAKE_CASE`

### Linting

Run all linters before committing:

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/

# Security check
bandit -r src/

# Or run all at once
make lint
```

---

## 📋 Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding/updating tests
- **chore**: Maintenance tasks
- **ci**: CI/CD changes

### Examples

```bash
# Feature
feat(agents): add quantum encryption agent

Add new agent for quantum-resistant encryption with
support for post-quantum algorithms.

Closes #123

# Bug fix
fix(api): resolve memory leak in task queue

The task queue was not properly releasing references
to completed tasks, causing memory usage to grow.

# Documentation
docs(readme): update installation instructions

Add Docker installation method and clarify
Python version requirements.

# Performance
perf(orchestrator): optimize agent allocation

Implement caching for agent capability lookups,
reducing allocation time by 40%.
```

### Commit Best Practices

1. Keep commits atomic (one change per commit)
2. Write clear, descriptive messages
3. Reference issues when applicable
4. Use present tense ("add" not "added")
5. Keep subject line under 50 characters
6. Wrap body at 72 characters

---

## 🔄 Pull Request Process

### Before Creating a PR

1. **Update your fork**
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

2. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes**
   - Write code following style guide
   - Add/update tests
   - Update documentation

4. **Test thoroughly**
   ```bash
   # Run all tests
   pytest
   
   # Run specific tests
   pytest tests/test_your_feature.py
   
   # Check coverage
   pytest --cov=src --cov-report=html
   ```

5. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

### Creating the PR

1. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open PR on GitHub**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out PR template

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] Changelog updated

## Related Issues
Closes #issue_number

## Screenshots (if applicable)
Add screenshots for UI changes
```

### PR Review Process

1. **Automated Checks**
   - CI/CD runs tests
   - Code quality checks
   - Security scanning

2. **Code Review**
   - At least one maintainer review
   - Address feedback promptly
   - Update PR as needed

3. **Merge Requirements**
   - All checks passing
   - Approved by maintainer
   - No merge conflicts
   - Up to date with main

---

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── e2e/           # End-to-end tests
├── performance/   # Performance tests
├── security/      # Security tests
├── fixtures/      # Test data
└── conftest.py    # Pytest configuration
```

### Writing Tests

#### Unit Test Example
```python
import pytest
from src.amas.agents.security_agent import SecurityAgent

class TestSecurityAgent:
    @pytest.fixture
    def agent(self):
        """Create test agent instance."""
        return SecurityAgent()
    
    @pytest.mark.asyncio
    async def test_scan_valid_target(self, agent):
        """Test scanning a valid target."""
        result = await agent.scan_target("example.com")
        
        assert result.status == "completed"
        assert "vulnerabilities" in result.data
        assert result.data["security_score"] >= 0
    
    @pytest.mark.asyncio
    async def test_scan_invalid_target(self, agent):
        """Test scanning an invalid target."""
        with pytest.raises(ValidationError):
            await agent.scan_target("not-a-valid-target")
    
    @pytest.mark.parametrize("scan_type", ["basic", "deep", "stealth"])
    @pytest.mark.asyncio
    async def test_scan_types(self, agent, scan_type):
        """Test different scan types."""
        result = await agent.scan_target("example.com", scan_type=scan_type)
        assert result.metadata["scan_type"] == scan_type
```

#### Integration Test Example
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_orchestration():
    """Test multi-agent task execution."""
    orchestrator = await create_test_orchestrator()
    
    task = Task(
        task_type="security_analysis",
        parameters={
            "target": "example.com",
            "depth": "comprehensive"
        }
    )
    
    result = await orchestrator.execute_task(task)
    
    assert result.status == "completed"
    assert len(result.agent_results) > 1
    assert all(r.status == "success" for r in result.agent_results)
```

### Test Coverage

- Aim for 80%+ code coverage
- Critical paths must have 100% coverage
- Test edge cases and error conditions
- Include performance benchmarks

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_security_agent.py

# Run tests matching pattern
pytest -k "security"

# Run with verbose output
pytest -v

# Run in parallel
pytest -n auto
```

---

## 📚 Documentation

### Documentation Types

1. **Code Documentation**
   - Docstrings for all public APIs
   - Type hints for clarity
   - Inline comments for complex logic

2. **User Documentation**
   - Getting started guides
   - Feature tutorials
   - API reference
   - FAQ section

3. **Developer Documentation**
   - Architecture overview
   - Development setup
   - Contributing guidelines
   - Design decisions

### Documentation Style

#### Docstring Example
```python
def calculate_security_score(
    vulnerabilities: List[Vulnerability],
    weights: Optional[Dict[str, float]] = None
) -> float:
    """Calculate overall security score based on vulnerabilities.
    
    The score is calculated using a weighted average of vulnerability
    severities, with critical vulnerabilities having the highest impact.
    
    Args:
        vulnerabilities: List of discovered vulnerabilities
        weights: Optional custom weights for severity levels.
            Defaults to: {'critical': 10, 'high': 5, 'medium': 2, 'low': 1}
    
    Returns:
        Security score from 0 (worst) to 100 (best)
        
    Raises:
        ValueError: If weights don't sum to a positive value
        
    Example:
        >>> vulns = [Vulnerability(severity="high"), Vulnerability(severity="low")]
        >>> score = calculate_security_score(vulns)
        >>> print(f"Security score: {score}")
        Security score: 78.5
    """
    # Implementation
```

#### Markdown Documentation
```markdown
# Feature Name

## Overview
Brief description of the feature and its purpose.

## Installation
```bash
pip install amas-feature
```

## Quick Start
```python
from amas import Feature

# Initialize
feature = Feature()

# Use feature
result = feature.process(data)
```

## API Reference

### `Feature.process(data)`
Process data using the feature.

**Parameters:**
- `data` (dict): Input data to process

**Returns:**
- `Result`: Processing result

## Examples
[Provide 2-3 practical examples]

## Troubleshooting
[Common issues and solutions]
```

---

## 👥 Community

### Communication Channels

1. **GitHub Discussions**
   - General discussions
   - Feature ideas
   - Q&A

2. **Discord Server**
   - Real-time chat
   - Community support
   - Development discussions

3. **GitHub Issues**
   - Bug reports
   - Feature requests
   - Documentation issues

### Getting Help

- Check documentation first
- Search existing issues
- Ask in Discord #help channel
- Create detailed issue if needed

### Recognition

We appreciate all contributions! Contributors are:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in documentation

---

## 🎉 Thank You!

Thank you for contributing to AMAS! Your efforts help make this project better for everyone. Whether you're fixing a typo, adding a feature, or helping others, every contribution matters.

### Questions?

If you have questions about contributing:
1. Check this guide
2. Ask in Discord
3. Create a discussion on GitHub
4. Email: contribute@amas.ai

---

**Happy Contributing! 🚀🤖✨**

**Last Updated**: January 2025  
**Version**: 1.1.0