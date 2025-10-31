# 🔌 AMAS API Documentation - Fully Integrated (January 2025)
# 🔌 AMAS API Documentation

> **Integration Status**: ✅ All endpoints verified and operational following PR #162 fixes

## Overview

The Advanced Multi-Agent Intelligence System (AMAS) provides a comprehensive RESTful API for interacting with the multi-agent platform. This API enables programmatic access to all AMAS features including agent orchestration, task management, monitoring, AI provider integration, and revolutionary **AI Agentic Workflows**.

**✅ 100% Implementation Verified** - All critical improvements from the project audit have been implemented and verified.

**🚀 AI Agentic Workflows API** - Access the revolutionary 4-layer AI agent architecture and 16 AI providers through comprehensive API endpoints.

### Phase 4 API Notes (PR #189)
- Security/auth internals enhanced; API surface remains compatible
- Sessions and user management improved for stability and auditing
- Relevant modules: `src/amas/security/enterprise_auth.py`, `session_management.py`, `user_management.py`, `advanced_security.py`, `data_management.py`
- Operators: review auth/session configuration per `docs/security/AUTHENTICATION_SETUP.md`

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
3. [AI Agentic Workflows API](#ai-agentic-workflows-api)
4. [Agent Management](#agent-management)
5. [Task Management](#task-management)
6. [AI Provider Management](#ai-provider-management)
7. [Monitoring & Metrics](#monitoring--metrics)
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

## 🚀 AI Agentic Workflows API

### **Revolutionary AI Agentic Workflow Endpoints**

The AI Agentic Workflows API provides access to the most advanced workflow automation system ever created, featuring a 4-layer AI agent architecture with 16 AI providers and intelligent failover.

#### **Master AI Orchestrator API**

##### **Trigger Master Orchestrator**
```http
POST /api/v1/workflows/orchestrator/trigger
```

**Request Body**:
```json
{
  "orchestration_mode": "intelligent",
  "target_components": "all",
  "priority_level": "normal",
  "ai_providers": "all"
}
```

**Parameters**:
- `orchestration_mode` (string): `intelligent`, `full_analysis`, `emergency_response`, `performance_optimization`, `security_audit`, `documentation_update`
- `target_components` (string): `all` or comma-separated list of components
- `priority_level` (string): `low`, `normal`, `high`, `critical`
- `ai_providers` (string): `all` or comma-separated list of providers

**Response**:
```json
{
  "workflow_id": "orchestrator-abc123",
  "status": "triggered",
  "message": "Master AI Orchestrator triggered successfully",
  "estimated_duration": "5-10 minutes",
  "layers": {
    "layer1_detection_analysis": "queued",
    "layer2_intelligence_decision": "pending",
    "layer3_execution_fix": "pending",
    "layer4_orchestration_management": "pending"
  }
}
```

##### **Get Orchestrator Status**
```http
GET /api/v1/workflows/orchestrator/{workflow_id}/status
```

**Response**:
```json
{
  "workflow_id": "orchestrator-abc123",
  "status": "running",
  "progress": 45,
  "current_layer": "layer2_intelligence_decision",
  "layers": {
    "layer1_detection_analysis": "completed",
    "layer2_intelligence_decision": "running",
    "layer3_execution_fix": "pending",
    "layer4_orchestration_management": "pending"
  },
  "results": {
    "analysis_results": {...},
    "decisions": {...}
  },
  "ai_providers_used": ["deepseek", "claude", "gpt4"],
  "estimated_completion": "2025-01-15T10:30:00Z"
}
```

#### **AI Agentic Project Self-Improver API**

##### **Trigger Self-Improver**
```http
POST /api/v1/workflows/self-improver/trigger
```

**Request Body**:
```json
{
  "improvement_mode": "intelligent",
  "target_areas": "all",
  "learning_depth": "deep",
  "auto_apply": false
}
```

**Parameters**:
- `improvement_mode` (string): `intelligent`, `aggressive`, `conservative`, `performance_focused`, `security_focused`, `documentation_focused`
- `target_areas` (string): `all` or comma-separated list of areas
- `learning_depth` (string): `surface`, `medium`, `deep`, `comprehensive`
- `auto_apply` (boolean): Whether to automatically apply improvements

**Response**:
```json
{
  "workflow_id": "self-improver-xyz789",
  "status": "triggered",
  "message": "AI Agentic Project Self-Improver triggered successfully",
  "estimated_duration": "10-15 minutes",
  "phases": {
    "project_analysis_learning": "queued",
    "intelligent_improvement_generation": "pending",
    "automated_implementation": "pending",
    "learning_adaptation": "pending"
  }
}
```

##### **Get Self-Improver Results**
```http
GET /api/v1/workflows/self-improver/{workflow_id}/results
```

**Response**:
```json
{
  "workflow_id": "self-improver-xyz789",
  "status": "completed",
  "phases": {
    "project_analysis_learning": "completed",
    "intelligent_improvement_generation": "completed",
    "automated_implementation": "completed",
    "learning_adaptation": "completed"
  },
  "improvements": [
    {
      "type": "code_quality",
      "description": "Optimized function performance",
      "file": "src/utils/helper.py",
      "line": 45,
      "suggestion": "Use list comprehension instead of for loop",
      "confidence": 0.95,
      "applied": true
    },
    {
      "type": "security",
      "description": "Added input validation",
      "file": "src/api/endpoints.py",
      "line": 123,
      "suggestion": "Validate user input before processing",
      "confidence": 0.88,
      "applied": false
    }
  ],
  "metrics": {
    "total_improvements": 15,
    "applied_improvements": 12,
    "confidence_score": 0.91,
    "performance_gain": "23%"
  }
}
```

#### **AI Agentic Issue Auto-Responder API**

##### **Trigger Issue Responder**
```http
POST /api/v1/workflows/issue-responder/trigger
```

**Request Body**:
```json
{
  "response_mode": "intelligent",
  "response_depth": "comprehensive",
  "auto_fix": true,
  "language_preference": "auto",
  "target_issues": "all"
}
```

**Parameters**:
- `response_mode` (string): `intelligent`, `aggressive`, `conservative`, `technical_focused`, `user_friendly`, `automated_fix`
- `response_depth` (string): `basic`, `detailed`, `comprehensive`, `expert`
- `auto_fix` (boolean): Whether to automatically fix issues
- `language_preference` (string): `auto`, `english`, `spanish`, `french`, `german`, `chinese`, `japanese`
- `target_issues` (string): `all` or comma-separated list of issue numbers

**Response**:
```json
{
  "workflow_id": "issue-responder-def456",
  "status": "triggered",
  "message": "AI Agentic Issue Auto-Responder triggered successfully",
  "estimated_duration": "3-5 minutes",
  "phases": {
    "issue_analysis_categorization": "queued",
    "intelligent_response_generation": "pending",
    "automated_response_fix_implementation": "pending",
    "learning_adaptation": "pending"
  }
}
```

##### **Get Issue Response Results**
```http
GET /api/v1/workflows/issue-responder/{workflow_id}/results
```

**Response**:
```json
{
  "workflow_id": "issue-responder-def456",
  "status": "completed",
  "phases": {
    "issue_analysis_categorization": "completed",
    "intelligent_response_generation": "completed",
    "automated_response_fix_implementation": "completed",
    "learning_adaptation": "completed"
  },
  "responses": [
    {
      "issue_number": 123,
      "title": "Bug in authentication system",
      "category": "bug",
      "severity": "high",
      "response": "I've identified the authentication issue and implemented a fix. The problem was in the token validation logic...",
      "fix_applied": true,
      "fix_details": {
        "file": "src/auth/token_validator.py",
        "changes": "Added proper token expiration check",
        "confidence": 0.92
      },
      "language": "english"
    }
  ],
  "metrics": {
    "total_issues_processed": 5,
    "responses_generated": 5,
    "fixes_applied": 3,
    "average_confidence": 0.89
  }
}
```

#### **AI Provider Management API**

##### **Get AI Provider Status**
```http
GET /api/v1/ai-providers/status
```

**Response**:
```json
{
  "providers": [
    {
      "name": "deepseek",
      "priority": 1,
      "status": "active",
      "response_time": 1.2,
      "success_rate": 0.98,
      "last_used": "2025-01-15T10:25:00Z"
    },
    {
      "name": "claude",
      "priority": 2,
      "status": "active",
      "response_time": 1.5,
      "success_rate": 0.96,
      "last_used": "2025-01-15T10:24:00Z"
    },
    {
      "name": "gpt4",
      "priority": 3,
      "status": "rate_limited",
      "response_time": 2.1,
      "success_rate": 0.94,
      "last_used": "2025-01-15T10:20:00Z"
    }
  ],
  "failover_strategy": "intelligent",
  "total_providers": 16,
  "active_providers": 15
}
```

##### **Configure AI Provider**
```http
PUT /api/v1/ai-providers/{provider_name}/config
```

**Request Body**:
```json
{
  "priority": 1,
  "timeout": 30,
  "enabled": true,
  "max_retries": 3
}
```

**Response**:
```json
{
  "provider": "deepseek",
  "config": {
    "priority": 1,
    "timeout": 30,
    "enabled": true,
    "max_retries": 3
  },
  "status": "updated",
  "message": "Provider configuration updated successfully"
}
```

#### **Workflow Monitoring API**

##### **Get Workflow Metrics**
```http
GET /api/v1/workflows/metrics
```

**Query Parameters**:
- `timeframe` (string): `1h`, `24h`, `7d`, `30d`
- `workflow_type` (string): `orchestrator`, `self-improver`, `issue-responder`, `all`

**Response**:
```json
{
  "timeframe": "24h",
  "metrics": {
    "total_workflows": 45,
    "success_rate": 0.98,
    "average_duration": 8.5,
    "ai_provider_usage": {
      "deepseek": 35,
      "claude": 28,
      "gpt4": 22,
      "glm": 18
    },
    "workflow_types": {
      "orchestrator": 15,
      "self-improver": 12,
      "issue-responder": 18
    }
  },
  "performance": {
    "fastest_workflow": 2.3,
    "slowest_workflow": 25.7,
    "average_response_time": 1.8
  }
}
```

##### **Get Workflow Logs**
```http
GET /api/v1/workflows/{workflow_id}/logs
```

**Query Parameters**:
- `level` (string): `debug`, `info`, `warning`, `error`
- `limit` (integer): Number of log entries to return

**Response**:
```json
{
  "workflow_id": "orchestrator-abc123",
  "logs": [
    {
      "timestamp": "2025-01-15T10:25:00Z",
      "level": "info",
      "message": "Layer 1 analysis completed successfully",
      "layer": "detection_analysis"
    },
    {
      "timestamp": "2025-01-15T10:26:00Z",
      "level": "info",
      "message": "Layer 2 intelligence processing started",
      "layer": "intelligence_decision"
    },
    {
      "timestamp": "2025-01-15T10:27:00Z",
      "level": "warning",
      "message": "Provider gpt4 rate limited, switching to claude",
      "layer": "intelligence_decision"
    }
  ],
  "total_logs": 25,
  "has_more": false
}
```

#### **Workflow Configuration API**

##### **Get Workflow Configuration**
```http
GET /api/v1/workflows/config
```

**Response**:
```json
{
  "orchestrator": {
    "modes": ["intelligent", "full_analysis", "emergency_response", "performance_optimization", "security_audit", "documentation_update"],
    "components": ["all", "code_quality", "security", "performance", "documentation"],
    "priorities": ["low", "normal", "high", "critical"]
  },
  "self_improver": {
    "modes": ["intelligent", "aggressive", "conservative", "performance_focused", "security_focused", "documentation_focused"],
    "areas": ["all", "code_quality", "performance", "security", "documentation", "testing", "architecture", "dependencies"],
    "depths": ["surface", "medium", "deep", "comprehensive"]
  },
  "issue_responder": {
    "modes": ["intelligent", "aggressive", "conservative", "technical_focused", "user_friendly", "automated_fix"],
    "depths": ["basic", "detailed", "comprehensive", "expert"],
    "languages": ["auto", "english", "spanish", "french", "german", "chinese", "japanese"]
  }
}
```

##### **Update Workflow Configuration**
```http
PUT /api/v1/workflows/config
```

**Request Body**:
```json
{
  "orchestrator": {
    "default_mode": "intelligent",
    "default_priority": "normal",
    "timeout": 1800
  },
  "self_improver": {
    "default_mode": "intelligent",
    "default_depth": "deep",
    "auto_apply": false
  },
  "issue_responder": {
    "default_mode": "intelligent",
    "default_depth": "comprehensive",
    "auto_fix": false
  }
}
```

**Response**:
```json
{
  "status": "updated",
  "message": "Workflow configuration updated successfully",
  "config": {
    "orchestrator": {...},
    "self_improver": {...},
    "issue_responder": {...}
  }
}
```

#### **Error Handling**

All AI Agentic Workflow API endpoints return consistent error responses:

```json
{
  "error": {
    "code": "WORKFLOW_TRIGGER_FAILED",
    "message": "Failed to trigger workflow",
    "details": "Invalid configuration parameters",
    "timestamp": "2025-01-15T10:30:00Z",
    "workflow_id": "orchestrator-abc123"
  }
}
```

**Common Error Codes**:
- `WORKFLOW_NOT_FOUND`: Workflow ID not found
- `WORKFLOW_TRIGGER_FAILED`: Failed to trigger workflow
- `INVALID_CONFIGURATION`: Invalid configuration parameters
- `AI_PROVIDER_UNAVAILABLE`: AI provider not available
- `RATE_LIMIT_EXCEEDED`: Rate limit exceeded
- `AUTHENTICATION_FAILED`: Authentication failed

#### **Rate Limiting**

AI Agentic Workflow API endpoints are rate limited:

- **Orchestrator**: 10 requests per minute
- **Self-Improver**: 5 requests per minute
- **Issue Responder**: 20 requests per minute
- **Provider Management**: 30 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1642248000
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