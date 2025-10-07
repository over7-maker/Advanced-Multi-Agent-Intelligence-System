# 📖 AMAS User Guide

> **Version**: 2.0.0 | **Status**: ✅ Fully Integrated and Production Ready

## Welcome to AMAS!

The Advanced Multi-Agent Intelligence System (AMAS) is a powerful AI platform that leverages multiple intelligent agents to perform complex tasks. This guide will help you get the most out of AMAS, whether you're using it for security analysis, data processing, or research.

**✅ 100% Implementation Verified** - All critical improvements from the project audit have been implemented and verified.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Interactive Mode](#interactive-mode)
3. [Command Reference](#command-reference)
4. [Task Types](#task-types)
5. [Working with Results](#working-with-results)
6. [Web Interface](#web-interface)
7. [API Usage](#api-usage)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## 🚀 Quick Start

### Getting Started with AMAS

#### 1. Environment Validation
```bash
# Validate your setup with minimal configuration
python scripts/validate_env.py --mode basic --verbose
```

#### 2. Minimal Configuration (3 API Keys)
```bash
# Set minimal required API keys
export DEEPSEEK_API_KEY="your_deepseek_key"
export GLM_API_KEY="your_glm_key"
export GROK_API_KEY="your_grok_key"
```

#### 3. Start AMAS
```bash
# Interactive Mode (Recommended for beginners)
./start-amas-interactive.sh

# Or use Docker
docker-compose up -d

# Or run locally
python -m uvicorn src.amas.api.main:app --reload
```

#### 4. Try Your First Command
```bash
🤖 AMAS> scan example.com
```

#### 5. View Results
```bash
🤖 AMAS> show results
```

That's it! You've just performed your first security scan with AMAS.

### Quick Test with Python API

Submit your first task programmatically:

```python
# Python API with new unified orchestrator
import asyncio
from src.amas.core.unified_orchestrator import UnifiedIntelligenceOrchestrator

async def test_amas():
    orchestrator = UnifiedIntelligenceOrchestrator()
    await orchestrator.initialize()
    
    # Submit OSINT task
    task_id = await orchestrator.submit_task(
        agent_type="osint",
        description="Analyze security threats from example.com",
        priority=1
    )
    
    result = await orchestrator.get_task_result(task_id)
    print(f"Task result: {result}")
    
    await orchestrator.shutdown()

asyncio.run(test_amas())
```

---

## 🗣️ Interactive Mode

Interactive Mode provides a natural language interface to AMAS, making it easy to use without remembering complex commands.

### Starting Interactive Mode

```bash
# Using the startup script
./start-amas-interactive.sh

# Or directly with Python
python simple-amas-interactive.py
```

### Natural Language Commands

AMAS understands plain English commands:

```bash
# Security scanning
🤖 AMAS> scan google.com for vulnerabilities
🤖 AMAS> check security of my-website.com
🤖 AMAS> find open ports on 192.168.1.1

# Code analysis
🤖 AMAS> analyze code quality of github.com/user/repo
🤖 AMAS> review security of my python project
🤖 AMAS> check for bugs in src/main.py

# Research and intelligence
🤖 AMAS> research latest AI security threats
🤖 AMAS> gather intelligence on ransomware trends
🤖 AMAS> find information about zero-day exploits

# Data analysis
🤖 AMAS> analyze trends in dataset.csv
🤖 AMAS> create report from sales_data.json
🤖 AMAS> visualize network traffic patterns
```

### Interactive Features

#### Real-time Progress
Watch agents work in real-time:
```
⠋ Security Expert Agent working...
⠋ OSINT Agent gathering data...
⠋ Analysis Agent processing...
✅ Task completed in 4.32 seconds
```

#### Rich Output Display
Results are displayed in beautiful, easy-to-read tables:
```
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Attribute       ┃ Value                        ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Target          │ example.com                  │
│ Security Score  │ A+ (95/100)                  │
│ Vulnerabilities │ 2 Low, 0 Medium, 0 High      │
│ SSL Grade       │ A+                           │
│ Headers         │ ✓ Secure                     │
└─────────────────┴──────────────────────────────┘
```

#### Command History
Use arrow keys to navigate through previous commands:
- ↑ Previous command
- ↓ Next command
- Ctrl+R Search history

---

## 📚 Command Reference

### Core Commands

#### System Commands
| Command | Description | Example |
|---------|-------------|---------|
| `help` | Show available commands | `help` |
| `status` | Show system status | `status` |
| `agents` | List available agents | `agents` |
| `providers` | Show AI providers | `providers` |
| `config` | View configuration | `config` |
| `exit/quit` | Exit AMAS | `exit` |

#### Task Commands
| Command | Description | Example |
|---------|-------------|---------|
| `scan` | Security scan | `scan example.com` |
| `analyze` | Analyze code/data | `analyze repo.git` |
| `research` | Research topics | `research AI trends` |
| `monitor` | Monitor resources | `monitor server-01` |
| `report` | Generate reports | `report security audit` |

#### Result Commands
| Command | Description | Example |
|---------|-------------|---------|
| `show` | Show task results | `show task-abc123` |
| `list` | List recent tasks | `list tasks` |
| `export` | Export results | `export pdf report.pdf` |
| `share` | Share results | `share via email` |

### Advanced Commands

#### Batch Operations
```bash
# Process multiple targets
🤖 AMAS> scan example.com, test.com, demo.com

# Analyze multiple repositories
🤖 AMAS> analyze github.com/org/* for security issues

# Generate comparative report
🤖 AMAS> compare security between prod and staging
```

#### Scheduled Tasks
```bash
# Schedule daily scans
🤖 AMAS> schedule daily scan of production servers at 2am

# Weekly reports
🤖 AMAS> schedule weekly security report every monday

# Monitor continuously
🤖 AMAS> monitor api.example.com every 5 minutes
```

#### Custom Workflows
```bash
# Create workflow
🤖 AMAS> create workflow "security-audit" with steps:
         1. scan all servers
         2. analyze vulnerabilities
         3. generate report
         4. send to security team

# Run workflow
🤖 AMAS> run workflow security-audit
```

---

## 🎯 Task Types

### Security Tasks

#### Vulnerability Scanning
```bash
# Basic scan
🤖 AMAS> scan example.com

# Comprehensive scan
🤖 AMAS> deep scan example.com including subdomains

# Specific checks
🤖 AMAS> check example.com for SQL injection vulnerabilities
🤖 AMAS> scan network 192.168.1.0/24 for open ports
```

#### Security Analysis
```bash
# Code security review
🤖 AMAS> analyze security of github.com/user/repo

# Configuration audit
🤖 AMAS> audit nginx configuration for security issues

# Compliance check
🤖 AMAS> check GDPR compliance of user-service
```

### Intelligence Gathering

#### OSINT Operations
```bash
# Domain intelligence
🤖 AMAS> gather intelligence on example.com

# Threat research
🤖 AMAS> research latest ransomware campaigns

# Technology stack discovery
🤖 AMAS> identify technologies used by competitor.com
```

#### Threat Intelligence
```bash
# Threat monitoring
🤖 AMAS> monitor for threats targeting financial sector

# IOC analysis
🤖 AMAS> analyze IOCs from threat-intel-feed.json

# Attack pattern analysis
🤖 AMAS> identify attack patterns in security logs
```

### Data Analysis

#### Pattern Recognition
```bash
# Anomaly detection
🤖 AMAS> find anomalies in access_logs.csv

# Trend analysis
🤖 AMAS> analyze trends in sales_data_2024.json

# Behavioral analysis
🤖 AMAS> analyze user behavior patterns in app_logs
```

#### Reporting
```bash
# Executive summary
🤖 AMAS> create executive summary of security posture

# Detailed reports
🤖 AMAS> generate detailed vulnerability report for web-app

# Custom reports
🤖 AMAS> create custom report with charts from analytics_data
```

---

## 📊 Working with Results

### Understanding Results

#### Result Structure
Every task returns structured results:
```json
{
  "task_id": "task-abc123",
  "status": "completed",
  "summary": {
    "security_score": 85,
    "vulnerabilities": {
      "critical": 0,
      "high": 1,
      "medium": 3,
      "low": 5
    }
  },
  "details": {
    // Detailed findings
  },
  "recommendations": [
    // Actionable recommendations
  ]
}
```

#### Interpreting Security Scores
- **A+ (95-100)**: Excellent security posture
- **A (90-94)**: Very good security
- **B (80-89)**: Good with minor issues
- **C (70-79)**: Moderate security concerns
- **D (60-69)**: Significant vulnerabilities
- **F (0-59)**: Critical security issues

### Exporting Results

#### Export Formats
```bash
# PDF report
🤖 AMAS> export results to pdf security_audit.pdf

# JSON data
🤖 AMAS> export results to json data_export.json

# CSV for analysis
🤖 AMAS> export vulnerabilities to csv vulns.csv

# HTML report
🤖 AMAS> export results to html report.html
```

#### Integration Options
```bash
# Send to ticketing system
🤖 AMAS> create jira tickets from vulnerabilities

# Update dashboard
🤖 AMAS> push results to grafana dashboard

# Notify team
🤖 AMAS> send results to security-team@company.com
```

---

## 💻 Web Interface

### Accessing the Web UI

1. Open your browser to: `http://localhost:3000`
2. Login with your credentials
3. Navigate using the intuitive interface

### Web UI Features

#### Dashboard
- **System Overview**: Real-time system status
- **Active Tasks**: Currently running operations
- **Recent Results**: Latest completed tasks
- **Performance Metrics**: System performance graphs

#### Task Management
- **Create Tasks**: Visual task builder
- **Task Templates**: Pre-configured task templates
- **Batch Operations**: Run multiple tasks
- **Schedule Tasks**: Set up recurring tasks

#### Results Viewer
- **Interactive Reports**: Drill-down into findings
- **Visualizations**: Charts and graphs
- **Export Options**: Download in various formats
- **Sharing**: Share results with team members

#### Settings
- **API Keys**: Manage your API keys
- **Notifications**: Configure alerts
- **Integrations**: Connect third-party services
- **Preferences**: Customize your experience

---

## 🔌 API Usage

### Quick API Example

```bash
# Submit a task via API
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "task_type": "security_scan",
    "parameters": {
      "target": "example.com"
    }
  }'

# Get results
curl -H "X-API-Key: your-api-key" \
  http://localhost:8000/api/v1/tasks/task-abc123/results
```

### SDK Usage

#### Python SDK
```python
from amas_sdk import AMASClient

# Initialize client
client = AMASClient(api_key="your-api-key")

# Submit task
task = client.create_task(
    task_type="security_scan",
    parameters={"target": "example.com"}
)

# Wait for completion
result = task.wait_for_completion()

# Process results
print(f"Security Score: {result.security_score}")
for vuln in result.vulnerabilities:
    print(f"- {vuln.severity}: {vuln.description}")
```

#### JavaScript SDK
```javascript
const { AMASClient } = require('@amas/sdk');

// Initialize client
const client = new AMASClient({ apiKey: 'your-api-key' });

// Submit task
const task = await client.createTask({
  taskType: 'security_scan',
  parameters: { target: 'example.com' }
});

// Get results
const result = await task.waitForCompletion();
console.log(`Security Score: ${result.securityScore}`);
```

---

## 💡 Best Practices

### Task Optimization

#### 1. Use Specific Commands
```bash
# Good - Specific and clear
🤖 AMAS> scan example.com for XSS vulnerabilities in contact forms

# Less optimal - Too general
🤖 AMAS> check example.com
```

#### 2. Batch Similar Tasks
```bash
# Good - Batch processing
🤖 AMAS> scan all production servers: prod-01, prod-02, prod-03

# Less optimal - Individual tasks
🤖 AMAS> scan prod-01
🤖 AMAS> scan prod-02
🤖 AMAS> scan prod-03
```

#### 3. Use Templates
```bash
# Create template
🤖 AMAS> save template "weekly-audit" from last scan

# Reuse template
🤖 AMAS> run template weekly-audit on staging environment
```

### Security Best Practices

1. **Regular Scans**: Schedule regular security scans
2. **Monitor Changes**: Track security score trends
3. **Act on Findings**: Address vulnerabilities promptly
4. **Document Actions**: Keep audit trail of remediation

### Performance Tips

1. **Off-Peak Scanning**: Run intensive scans during off-peak hours
2. **Incremental Scans**: Use incremental scans for large targets
3. **Result Caching**: Leverage cached results when appropriate
4. **Resource Limits**: Set appropriate resource limits

---

## 🔧 Troubleshooting

### Common Issues

#### Connection Issues
```bash
# Check system status
🤖 AMAS> status

# Test connectivity
🤖 AMAS> test connection to api

# View detailed logs
🤖 AMAS> show logs --level debug
```

#### Task Failures
```bash
# View task details
🤖 AMAS> show task task-abc123 --verbose

# Retry failed task
🤖 AMAS> retry task task-abc123

# Check agent status
🤖 AMAS> show agent security-agent status
```

#### Performance Issues
```bash
# Check system resources
🤖 AMAS> show system resources

# View performance metrics
🤖 AMAS> show performance metrics

# Optimize task
🤖 AMAS> optimize task for speed
```

### Getting Help

```bash
# Built-in help
🤖 AMAS> help [command]

# Show examples
🤖 AMAS> examples security scan

# Contact support
🤖 AMAS> support "describe your issue"
```

---

## 🌟 Advanced Features

### ML-Powered Intelligence
AMAS uses machine learning to optimize every aspect of operation:

```bash
# Let ML decide the best approach
🤖 AMAS> optimize my security scan workflow

# View ML decision insights
🤖 AMAS> show ml decision for task-abc123

# Enable intelligent mode
🤖 AMAS> set mode intelligent
```

### Multi-Provider AI Fallback
Never experience AI failures with our 15+ provider system:

```bash
# Check provider status
🤖 AMAS> show ai providers

# Force specific provider
🤖 AMAS> use provider deepseek for next task

# View provider performance
🤖 AMAS> show provider stats
```

### Reinforcement Learning Optimization
AMAS continuously improves itself:

```bash
# View optimization status
🤖 AMAS> show rl optimizer status

# Enable aggressive optimization
🤖 AMAS> enable optimization mode aggressive

# View performance improvements
🤖 AMAS> show optimization history
```

### Enterprise Compliance
Built-in compliance for regulated industries:

```bash
# Run compliance check
🤖 AMAS> check compliance for HIPAA

# Generate compliance report
🤖 AMAS> generate SOC2 compliance report

# Enable compliance mode
🤖 AMAS> enable compliance mode GDPR
```

---

## ❓ FAQ

### General Questions

**Q: What makes AMAS different from other security tools?**
A: AMAS uses multiple AI agents working together, providing more comprehensive analysis than single-purpose tools. It also features intelligent fallback across 16 AI providers, ensuring reliable operation.

**Q: Can I use AMAS offline?**
A: Yes! AMAS supports offline operation for sensitive environments. See the [Offline Guide](OFFLINE_SYSTEM_GUIDE.md).

**Q: How do I integrate AMAS with my existing tools?**
A: AMAS provides REST APIs, webhooks, and SDKs for easy integration. It also supports common formats like JIRA, Slack, and email notifications.

### Technical Questions

**Q: What AI providers does AMAS support?**
A: AMAS supports 16 AI providers including DeepSeek, GLM, Grok, and more. It automatically fails over between providers for maximum reliability.

**Q: How secure is AMAS?**
A: AMAS implements enterprise-grade security including encryption, authentication, and compliance with GDPR, SOC2, HIPAA, and other frameworks.

**Q: Can I add custom agents?**
A: Yes! AMAS is extensible. See the [Developer Guide](../developer/README.md) for creating custom agents.

### Operational Questions

**Q: How do I monitor AMAS performance?**
A: AMAS includes built-in monitoring with Prometheus and Grafana. Access dashboards at `http://localhost:3000`.

**Q: What are the system requirements?**
A: Minimum: 8GB RAM, 4 CPU cores, 50GB storage. Recommended: 16GB+ RAM, 8+ CPU cores, 100GB+ SSD storage.

**Q: How do I update AMAS?**
A: Use the update command: `docker-compose pull && docker-compose up -d` or follow the [Update Guide](../deployment/UPDATE_GUIDE.md).

---

## 📚 Additional Resources

### Guides
- [Setup Guide](SETUP_GUIDE.md) - Detailed installation instructions
- [API Documentation](../api/README.md) - Complete API reference
- [Security Guide](../security/SECURITY.md) - Security best practices
- [Performance Guide](DOCKER_OPTIMIZATION_GUIDE.md) - Performance optimization

### Examples
- [Example Scripts](../../examples/) - Sample code and scripts
- [Use Cases](../../docs/USE_CASES.md) - Real-world scenarios
- [Tutorials](../../docs/TUTORIALS.md) - Step-by-step tutorials

### Support
- [GitHub Issues](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues)
- [Community Discord](https://discord.gg/amas)
- [Documentation](https://docs.amas.ai)
- Email: support@amas.ai

---

**Happy Analyzing with AMAS! 🚀🤖✨**

**Last Updated**: January 2025  
**Version**: 1.1.0