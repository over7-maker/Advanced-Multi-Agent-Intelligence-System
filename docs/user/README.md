# AMAS User Guide

Welcome to the Advanced Multi-Agent Intelligence System (AMAS) user documentation. This guide will help you get started and make the most of AMAS's powerful AI capabilities.

## Table of Contents

1. [Getting Started](#getting-started)
2. [User Interfaces](#user-interfaces)
3. [Task Management](#task-management)
4. [Agent Types](#agent-types)
5. [Use Cases](#use-cases)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### First Time Setup

1. **System Requirements Check**
   ```bash
   amas health --check-all
   ```

2. **Configuration**
   - Copy `.env.example` to `.env`
   - Configure your preferences
   - Set up API keys if using external services

3. **Start AMAS**
   ```bash
   amas start
   ```

4. **Verify Installation**
   ```bash
   amas status
   ```

### Quick Test

Submit your first task to verify everything works:

```bash
amas submit-task research "What are the latest trends in AI?" --wait
```

## User Interfaces

### 1. Web Interface (Recommended for Beginners)

Access: `http://localhost:3000`

**Features:**
- Visual task management dashboard
- Real-time agent monitoring
- Interactive result visualization
- System health monitoring
- Configuration management

**Navigation:**
- **Dashboard**: System overview and quick stats
- **Tasks**: Submit, monitor, and manage tasks
- **Agents**: View agent status and capabilities
- **Results**: Browse and export task results
- **Settings**: System configuration

### 2. Command Line Interface (CLI)

Perfect for automation and advanced users.

**Basic Commands:**
```bash
# System management
amas start                     # Start the system
amas status                    # Show system status
amas health                    # Health checks

# Task management
amas submit-task <type> <description>  # Submit task
amas get-result <task-id>      # Get task results
amas list-tasks               # List all tasks

# Configuration
amas config-show              # Show configuration
amas config-set <key> <value> # Update configuration
```

### 3. Desktop Application

Cross-platform Electron app with native OS integration.

**Features:**
- Native notifications
- System tray integration
- Offline capabilities
- File drag-and-drop
- Local data management

## Task Management

### Task Types

AMAS supports various specialized task types:

| Task Type | Description | Use Cases |
|-----------|-------------|-----------|
| `research` | Autonomous research and analysis | Literature review, trend analysis |
| `osint` | Open-source intelligence gathering | Threat assessment, information collection |
| `forensics` | Digital forensics and investigation | Evidence analysis, incident response |
| `data_analysis` | Advanced data processing | Pattern recognition, statistical analysis |
| `reporting` | Automated report generation | Executive summaries, technical reports |

### Task Submission

#### Via CLI
```bash
# Basic task
amas submit-task research "Analyze cryptocurrency market trends"

# Task with parameters
amas submit-task osint "Investigate domain threats" --params '{"domains": ["example.com"]}'

# High priority task
amas submit-task forensics "Analyze malware sample" --priority 1 --wait
```

#### Via Python API
```python
import asyncio
from amas import AMASApplication

async def submit_research_task():
    app = AMASApplication()
    await app.initialize()
    
    task_id = await app.submit_task({
        'type': 'research',
        'description': 'Research quantum computing applications in cybersecurity',
        'priority': 2,
        'parameters': {
            'depth': 'comprehensive',
            'sources': ['academic', 'industry', 'news'],
            'timeframe': '2023-2024'
        }
    })
    
    print(f"Task submitted: {task_id}")
    await app.shutdown()

asyncio.run(submit_research_task())
```

### Task Monitoring

Track task progress in real-time:

```bash
# Check specific task
amas get-result <task-id>

# Monitor all active tasks
amas list-tasks --status active

# Get detailed task history
amas task-history <task-id>
```

## Agent Types

### Research Agent
**Capabilities:** Literature review, trend analysis, data synthesis
**Best For:** Academic research, market analysis, technology scouting

### OSINT Agent
**Capabilities:** Information gathering, source verification, threat assessment
**Best For:** Security analysis, competitive intelligence, risk assessment

### Forensics Agent
**Capabilities:** Digital evidence analysis, malware investigation, incident response
**Best For:** Cybersecurity, legal investigations, compliance audits

### Data Analysis Agent
**Capabilities:** Statistical analysis, pattern recognition, predictive modeling
**Best For:** Business intelligence, scientific analysis, performance optimization

### Reporting Agent
**Capabilities:** Automated report generation, data visualization, executive summaries
**Best For:** Business reporting, compliance documentation, executive briefings

## Use Cases

### 1. Autonomous Research Pipeline

**Scenario:** Comprehensive research on emerging AI technologies

```python
# Multi-stage research workflow
tasks = [
    {'type': 'research', 'description': 'Literature review on quantum AI'},
    {'type': 'osint', 'description': 'Industry analysis of quantum AI companies'},
    {'type': 'data_analysis', 'description': 'Trend analysis of quantum AI publications'},
    {'type': 'reporting', 'description': 'Generate comprehensive quantum AI report'}
]

for task in tasks:
    task_id = await app.submit_task(task)
    result = await app.get_task_result(task_id)
```

### 2. Security Threat Assessment

**Scenario:** Continuous monitoring and threat assessment

```bash
# Setup automated threat monitoring
amas submit-task osint "Monitor cybersecurity threats" --params '{
    "sources": ["threat_feeds", "social_media", "dark_web"],
    "keywords": ["zero-day", "ransomware", "apt"],
    "continuous": true
}'
```

### 3. Business Intelligence Dashboard

**Scenario:** Real-time business intelligence and analytics

```python
# Business intelligence pipeline
business_tasks = [
    {'type': 'data_analysis', 'description': 'Analyze sales performance Q4 2024'},
    {'type': 'research', 'description': 'Market trend analysis for 2025'},
    {'type': 'reporting', 'description': 'Generate executive dashboard'}
]
```

## Best Practices

### Task Design

1. **Be Specific**: Provide clear, detailed task descriptions
2. **Set Priorities**: Use priority levels effectively (1=urgent, 5=low)
3. **Use Parameters**: Leverage task parameters for customization
4. **Monitor Progress**: Check task status regularly

### System Management

1. **Regular Health Checks**: Monitor system health daily
2. **Log Monitoring**: Review logs for issues and insights
3. **Resource Management**: Monitor CPU, memory, and GPU usage
4. **Backup Strategy**: Regular data and configuration backups

### Security

1. **Regular Updates**: Keep AMAS and dependencies updated
2. **Access Control**: Use RBAC to limit user permissions
3. **Audit Monitoring**: Review audit logs regularly
4. **Network Security**: Use VPNs and firewalls appropriately

## Troubleshooting

### Common Issues

#### 1. System Won't Start
```bash
# Check service dependencies
amas health --check-services

# Check logs
tail -f logs/amas.log

# Restart services
docker-compose restart
```

#### 2. Task Submission Fails
```bash
# Verify system status
amas status

# Check agent availability
amas list-agents

# Review task parameters
amas validate-task <task-description>
```

#### 3. Poor Performance
```bash
# Monitor resources
amas monitor --resources

# Check GPU utilization
nvidia-smi

# Optimize configuration
amas config-optimize
```

### Getting Help

1. **Check Logs**: `logs/amas.log` contains detailed information
2. **System Health**: Run `amas health --check-all`
3. **Documentation**: Comprehensive docs in `docs/` directory
4. **Community**: GitHub Issues and Discussions

### Advanced Troubleshooting

For complex issues, enable debug mode:

```bash
# Enable debug logging
export AMAS_LOG_LEVEL=DEBUG
amas start

# Generate diagnostic report
amas generate-diagnostic-report
```

## What's Next?

1. **Explore Examples**: Check out `examples/` directory
2. **Customize Agents**: Create specialized agents for your needs
3. **Build Workflows**: Design complex multi-agent processes
4. **Integrate APIs**: Connect AMAS to your existing systems
5. **Scale Deployment**: Move to production infrastructure

For more advanced topics, see the [Developer Guide](../developer/README.md).

---

**Need help?** Check our [FAQ](FAQ.md) or [contact support](SUPPORT.md).