# 🔌 AMAS API Documentation - Fully Integrated (January 2025)
# 🔌 AMAS API Documentation

> **Integration Status**: ✅ All endpoints verified and operational following PR #162 fixes

## Overview

The Advanced Multi-Agent Intelligence System (AMAS) provides a comprehensive RESTful API for interacting with the multi-agent platform. This API enables programmatic access to all AMAS features including agent orchestration, task management, monitoring, and AI provider integration.

**✅ 100% Implementation Verified** - All critical improvements from the project audit have been implemented and verified.

## 🚀 Quick Start

### Base URL
```
http://localhost:8000/api/v1
```

**Interactive Documentation:**
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Authentication
```bash
# Include API key in headers
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/health
```

### Example Request
```bash
# Submit a task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "task_type": "security_scan",
    "parameters": {
      "target": "example.com"
    }
  }'
```

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Core Endpoints](#core-endpoints)
3. [Agent Management](#agent-management)
4. [Task Management](#task-management)
5. [AI Provider Management](#ai-provider-management)
6. [Monitoring & Metrics](#monitoring--metrics)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [Webhooks](#webhooks)
10. [API Versioning](#api-versioning)

---

## 🔐 Authentication

AMAS API uses API key authentication for all endpoints except health checks.

### API Key Authentication
```http
X-API-Key: your-api-key-here
```

### Obtaining API Keys
API keys can be generated through:
- CLI: `amas api-key generate --name "My App"`
- Web UI: Settings → API Keys → Generate New
- Environment: Set `AMAS_API_KEY` in `.env`

### Security Best Practices
- Rotate API keys regularly
- Use environment variables for keys
- Never commit keys to version control
- Use HTTPS in production

---

## 🎯 Core Endpoints

### Health Check
Check system health and availability.

```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.1.0",
  "uptime": 3600,
  "services": {
    "orchestrator": "running",
    "ai_manager": "running",
    "monitoring": "running"
  }
}
```

### System Information
Get detailed system information.

```http
GET /api/v1/system/info
```

**Response:**
```json
{
  "version": "1.1.0",
  "agents": {
    "total": 8,
    "active": 8,
    "types": ["osint", "security", "analysis", "reporting"]
  },
  "ai_providers": {
    "total": 16,
    "active": 15,
    "failed": 1
  },
  "performance": {
    "avg_response_time": 2.3,
    "throughput": 250,
    "success_rate": 0.999
  }
}
```

---

## 🤖 Agent Management

### List Agents
Get all available agents and their capabilities.

```http
GET /api/v1/agents
```

**Response:**
```json
{
  "agents": [
    {
      "id": "osint-agent",
      "name": "OSINT Agent",
      "status": "active",
      "capabilities": [
        "web_scraping",
        "data_collection",
        "pattern_analysis"
      ],
      "performance": {
        "tasks_completed": 1520,
        "success_rate": 0.98,
        "avg_completion_time": 3.2
      }
    }
  ]
}
```

### Get Agent Details
Get detailed information about a specific agent.

```http
GET /api/v1/agents/{agent_id}
```

**Parameters:**
- `agent_id` (string, required): The agent identifier

**Response:**
```json
{
  "id": "security-agent",
  "name": "Security Expert Agent",
  "description": "Specialized in security analysis and vulnerability assessment",
  "status": "active",
  "capabilities": {
    "vulnerability_scanning": {
      "description": "Scan for security vulnerabilities",
      "parameters": ["target", "scan_type", "depth"]
    },
    "threat_analysis": {
      "description": "Analyze potential threats",
      "parameters": ["data", "threat_model"]
    }
  },
  "configuration": {
    "timeout": 300,
    "max_concurrent_tasks": 5,
    "priority": "high"
  }
}
```

### Update Agent Configuration
Update agent configuration parameters.

```http
PUT /api/v1/agents/{agent_id}/config
```

**Request Body:**
```json
{
  "timeout": 600,
  "max_concurrent_tasks": 10,
  "priority": "critical"
}
```

---

## 📋 Task Management

### Submit Task
Submit a new task for processing.

```http
POST /api/v1/tasks
```

**Request Body:**
```json
{
  "task_type": "security_scan",
  "parameters": {
    "target": "example.com",
    "scan_type": "comprehensive",
    "include_subdomains": true
  },
  "priority": "high",
  "callback_url": "https://your-app.com/webhook"
}
```

**Response:**
```json
{
  "task_id": "task-abc123",
  "status": "queued",
  "estimated_completion": "2025-01-07T12:30:00Z",
  "assigned_agents": ["security-agent", "osint-agent"]
}
```

### Get Task Status
Get the current status of a task.

```http
GET /api/v1/tasks/{task_id}
```

**Response:**
```json
{
  "task_id": "task-abc123",
  "status": "in_progress",
  "progress": 65,
  "started_at": "2025-01-07T12:00:00Z",
  "updated_at": "2025-01-07T12:15:00Z",
  "agents": {
    "security-agent": {
      "status": "working",
      "progress": 80
    },
    "osint-agent": {
      "status": "working",
      "progress": 50
    }
  }
}
```

### Get Task Results
Retrieve the results of a completed task.

```http
GET /api/v1/tasks/{task_id}/results
```

**Response:**
```json
{
  "task_id": "task-abc123",
  "status": "completed",
  "completed_at": "2025-01-07T12:25:00Z",
  "results": {
    "security_scan": {
      "vulnerabilities": [
        {
          "severity": "medium",
          "type": "outdated_software",
          "description": "Apache version 2.4.41 has known vulnerabilities",
          "remediation": "Update to Apache 2.4.54 or later"
        }
      ],
      "security_score": 85,
      "recommendations": [
        "Enable HTTPS",
        "Implement rate limiting",
        "Update server software"
      ]
    }
  }
}
```

### Cancel Task
Cancel a running or queued task.

```http
DELETE /api/v1/tasks/{task_id}
```

**Response:**
```json
{
  "task_id": "task-abc123",
  "status": "cancelled",
  "cancelled_at": "2025-01-07T12:20:00Z"
}
```

### List Tasks
List all tasks with filtering options.

```http
GET /api/v1/tasks?status=completed&limit=10&offset=0
```

**Query Parameters:**
- `status` (string, optional): Filter by status (queued, in_progress, completed, failed, cancelled)
- `agent_id` (string, optional): Filter by assigned agent
- `task_type` (string, optional): Filter by task type
- `priority` (string, optional): Filter by priority
- `from_date` (string, optional): Filter by start date (ISO 8601)
- `to_date` (string, optional): Filter by end date (ISO 8601)
- `limit` (integer, optional): Number of results per page (default: 20, max: 100)
- `offset` (integer, optional): Pagination offset (default: 0)

---

## 🤖 AI Provider Management

### List AI Providers
Get all configured AI providers and their status.

```http
GET /api/v1/ai-providers
```

**Response:**
```json
{
  "total_providers": 15,
  "active_providers": 12,
  "providers": [
    {
      "id": "deepseek",
      "name": "DeepSeek V3.1",
      "status": "active",
      "priority": 1,
      "provider_type": "openai_compatible",
      "health": {
        "status": "healthy",
        "success_rate": 0.99,
        "avg_response_time": 1.2,
        "last_checked": "2025-01-07T12:00:00Z",
        "consecutive_failures": 0
      }
    },
    {
      "id": "glm",
      "name": "GLM 4.5 Air",
      "status": "active",
      "priority": 2,
      "provider_type": "openai_compatible",
      "health": {
        "status": "healthy",
        "success_rate": 0.98,
        "avg_response_time": 1.5,
        "rate_limited": false
      }
    }
  ],
  "fallback_chain": ["deepseek", "glm", "grok", "kimi", "qwen"],
  "selection_strategy": "priority"
}
```

### Get Provider Details
Get detailed information about a specific AI provider.

```http
GET /api/v1/ai-providers/{provider_id}
```

**Response:**
```json
{
  "id": "deepseek",
  "name": "DeepSeek V3.1",
  "status": "active",
  "configuration": {
    "endpoint": "https://api.deepseek.com/v1",
    "model": "deepseek-chat",
    "max_tokens": 4096,
    "temperature": 0.7
  },
  "metrics": {
    "total_requests": 15420,
    "successful_requests": 15267,
    "failed_requests": 153,
    "avg_response_time": 1.2,
    "avg_tokens_used": 2500
  },
  "rate_limits": {
    "requests_per_minute": 60,
    "tokens_per_minute": 150000
  }
}
```

### Test AI Provider
Test connectivity and functionality of an AI provider.

```http
POST /api/v1/ai-providers/{provider_id}/test
```

**Response:**
```json
{
  "provider_id": "deepseek",
  "test_status": "success",
  "response_time": 1.15,
  "test_results": {
    "connectivity": "pass",
    "authentication": "pass",
    "model_access": "pass",
    "response_quality": "pass"
  }
}
```

---

## 🧠 ML & Optimization

### Get ML Decision Engine Status
Retrieve ML decision engine metrics and performance.

```http
GET /api/v1/ml/decision-engine/status
```

**Response:**
```json
{
  "status": "active",
  "model_version": "1.2.0",
  "metrics": {
    "accuracy": 0.95,
    "predictions_made": 15420,
    "avg_decision_time": 0.023,
    "optimization_score": 0.87
  },
  "recent_decisions": [
    {
      "task_id": "task-abc123",
      "decision": "allocate_to_security_agent",
      "confidence": 0.92,
      "factors": ["task_type", "agent_availability", "performance_history"]
    }
  ]
}
```

### Get RL Optimizer Status
Get Reinforcement Learning optimizer performance and actions.

```http
GET /api/v1/rl/optimizer/status
```

**Response:**
```json
{
  "status": "optimizing",
  "environment": "amas_gym_v1",
  "metrics": {
    "episodes_completed": 5420,
    "avg_reward": 0.82,
    "optimization_actions_taken": 1523,
    "performance_improvement": 0.52
  },
  "recent_optimizations": [
    {
      "action": "scale_up_workers",
      "reward": 0.91,
      "impact": "15% throughput increase"
    },
    {
      "action": "enable_caching",
      "reward": 0.78,
      "impact": "23% latency reduction"
    }
  ],
  "current_policy": {
    "exploration_rate": 0.1,
    "learning_rate": 0.001
  }
}
```

---

## 📊 Monitoring & Metrics

### Get System Metrics
Retrieve current system metrics.

```http
GET /api/v1/metrics
```

**Response:**
```json
{
  "timestamp": "2025-01-07T12:00:00Z",
  "system": {
    "cpu_usage": 45.2,
    "memory_usage": 62.8,
    "disk_usage": 35.4,
    "network_io": {
      "bytes_sent": 1048576,
      "bytes_received": 2097152
    }
  },
  "performance": {
    "active_tasks": 15,
    "queued_tasks": 8,
    "completed_tasks_1h": 120,
    "failed_tasks_1h": 2,
    "avg_task_duration": 3.5
  },
  "agents": {
    "active": 8,
    "idle": 0,
    "error": 0
  }
}
```

### Get Performance History
Retrieve historical performance data.

```http
GET /api/v1/metrics/history?period=1h&metric=response_time
```

**Query Parameters:**
- `period` (string, required): Time period (1h, 6h, 24h, 7d, 30d)
- `metric` (string, required): Metric name
- `agent_id` (string, optional): Filter by agent

**Response:**
```json
{
  "metric": "response_time",
  "period": "1h",
  "data_points": [
    {
      "timestamp": "2025-01-07T11:00:00Z",
      "value": 2.1
    },
    {
      "timestamp": "2025-01-07T11:05:00Z",
      "value": 2.3
    }
  ]
}
```

---

## ⚠️ Error Handling

AMAS API uses standard HTTP status codes and consistent error responses.

### Error Response Format
```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "The 'target' parameter is required",
    "details": {
      "parameter": "target",
      "provided": null,
      "expected": "string"
    },
    "request_id": "req-xyz789",
    "timestamp": "2025-01-07T12:00:00Z"
  }
}
```

### Common Error Codes
| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | INVALID_REQUEST | Invalid request format |
| 401 | UNAUTHORIZED | Missing or invalid API key |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 429 | RATE_LIMITED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |
| 503 | SERVICE_UNAVAILABLE | Service temporarily unavailable |

---

## 🚦 Rate Limiting

API requests are rate-limited to ensure fair usage and system stability.

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 998
X-RateLimit-Reset: 1704628800
```

### Rate Limits by Tier
| Tier | Requests/Hour | Burst Limit | Concurrent Tasks |
|------|---------------|-------------|------------------|
| Free | 100 | 10 | 2 |
| Basic | 1,000 | 50 | 10 |
| Pro | 10,000 | 200 | 50 |
| Enterprise | Unlimited | Unlimited | Unlimited |

---

## 🔔 Webhooks

Configure webhooks to receive real-time updates about task status changes.

### Webhook Configuration
```http
POST /api/v1/webhooks
```

**Request Body:**
```json
{
  "url": "https://your-app.com/amas-webhook",
  "events": ["task.completed", "task.failed"],
  "secret": "your-webhook-secret"
}
```

### Webhook Payload
```json
{
  "event": "task.completed",
  "timestamp": "2025-01-07T12:25:00Z",
  "data": {
    "task_id": "task-abc123",
    "status": "completed",
    "results_summary": {
      "security_score": 85,
      "vulnerabilities_found": 3
    }
  },
  "signature": "sha256=..."
}
```

### Webhook Events
- `task.created` - Task created
- `task.started` - Task execution started
- `task.progress` - Task progress update
- `task.completed` - Task completed successfully
- `task.failed` - Task failed
- `task.cancelled` - Task cancelled
- `agent.error` - Agent encountered error
- `system.alert` - System alert triggered

---

## 🔄 API Versioning

AMAS API uses URL-based versioning to ensure backward compatibility.

### Current Version
```
/api/v1/
```

### Version History
| Version | Status | Released | Sunset Date |
|---------|--------|----------|-------------|
| v1 | Current | 2025-01-01 | - |
| v0 | Deprecated | 2024-06-01 | 2025-06-01 |

### Version Migration
When migrating between versions:
1. Review the [migration guide](../MIGRATION_GUIDE.md)
2. Update your API base URL
3. Test in staging environment
4. Update production configuration

---

## 📚 Additional Resources

### SDKs and Libraries
- **Python SDK**: `pip install amas-sdk`
- **JavaScript SDK**: `npm install @amas/sdk`
- **Go SDK**: `go get github.com/amas/go-sdk`
- **Java SDK**: Coming soon

### Code Examples
- [Python Examples](../../examples/python/)
- [JavaScript Examples](../../examples/javascript/)
- [cURL Examples](../../examples/curl/)

### Tools
- [API Explorer](http://localhost:8000/api/explorer)
- [Postman Collection](../../tools/postman/amas-api.json)
- [OpenAPI Specification](../../tools/openapi/amas-api.yaml)

### Support
- [API Support](mailto:api-support@amas.ai)
- [GitHub Issues](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues)
- [Discord Community](https://discord.gg/amas)

---

**Last Updated**: January 2025  
**API Version**: v1  
**Documentation Version**: 1.1.0