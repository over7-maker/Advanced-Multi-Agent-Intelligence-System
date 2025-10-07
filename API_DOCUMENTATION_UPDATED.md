# AMAS API Documentation - Updated & Verified

## 🌐 **Base URL**

```
Production: https://your-amas-instance.com/api/v1
Development: http://localhost:8000
```

## 🔐 **Authentication**

AMAS uses JWT-based authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### **Obtaining a Token**

```http
POST /auth/login
Content-Type: application/json

{
    "username": "your-username",
    "password": "your-password"
}
```

**Response:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600
}
```

## 📊 **Core Endpoints**

### **System Status**

#### `GET /status`
Get overall system status and health.

**Response:**
```json
{
    "status": "operational",
    "version": "1.0.0",
    "uptime": 86400,
    "active_agents": 8,
    "active_tasks": 12,
    "total_tasks_processed": 1547,
    "system_load": {
        "cpu_percent": 45.2,
        "memory_percent": 67.8,
        "gpu_percent": 23.1
    },
    "services": {
        "llm_service": "healthy",
        "vector_service": "healthy", 
        "graph_service": "healthy",
        "database": "healthy"
    }
}
```

#### `GET /health`
Detailed health check for all components.

**Response:**
```json
{
    "healthy": true,
    "checks": {
        "database": {"status": "pass", "response_time": "5ms"},
        "llm_service": {"status": "pass", "response_time": "120ms"},
        "vector_service": {"status": "pass", "response_time": "15ms"},
        "graph_service": {"status": "pass", "response_time": "8ms"}
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🎯 **Task Management**

### **Submit Task**

#### `POST /tasks`
Submit a new task for processing.

**Request:**
```json
{
    "type": "research",
    "description": "Analyze current trends in quantum computing",
    "priority": 2,
    "parameters": {
        "depth": "comprehensive",
        "sources": ["academic", "industry"],
        "timeframe": "2023-2024"
    },
    "metadata": {
        "user_id": "user123",
        "department": "research"
    }
}
```

**Response:**
```json
{
    "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
    "status": "submitted",
    "estimated_completion": "2024-01-15T11:00:00Z",
    "assigned_agent": "research_agent_001",
    "created_at": "2024-01-15T10:30:00Z"
}
```

### **Get Task Status**

#### `GET /tasks/{task_id}`
Get detailed information about a specific task.

**Response:**
```json
{
    "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
    "type": "research",
    "description": "Analyze current trends in quantum computing",
    "status": "in_progress",
    "progress": 65,
    "assigned_agent": "research_agent_001",
    "created_at": "2024-01-15T10:30:00Z",
    "started_at": "2024-01-15T10:31:00Z",
    "estimated_completion": "2024-01-15T11:00:00Z",
    "steps_completed": [
        {
            "step": "data_collection",
            "status": "completed",
            "duration": "120s"
        },
        {
            "step": "analysis",
            "status": "in_progress",
            "progress": 40
        }
    ]
}
```

### **Get Task Result**

#### `GET /tasks/{task_id}/result`
Get the complete result of a finished task.

**Response:**
```json
{
    "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "result": {
        "summary": "Quantum computing shows significant growth in AI applications...",
        "key_findings": [
            "60% increase in quantum AI research papers",
            "Major tech companies investing heavily",
            "Expected commercial applications by 2026"
        ],
        "data_sources": 247,
        "confidence_score": 0.92,
        "recommendations": [
            "Monitor IBM and Google quantum initiatives",
            "Investigate quantum machine learning algorithms"
        ]
    },
    "metadata": {
        "processing_time": "1847s",
        "agent_used": "research_agent_001",
        "tokens_processed": 156789,
        "sources_analyzed": 247
    },
    "completed_at": "2024-01-15T11:00:47Z"
}
```

### **List Tasks**

#### `GET /tasks`
List tasks with filtering and pagination.

**Query Parameters:**
- `status`: Filter by task status (pending, in_progress, completed, failed)
- `type`: Filter by task type (research, osint, forensics, etc.)
- `user_id`: Filter by user ID
- `limit`: Number of results (default: 20, max: 100)
- `offset`: Pagination offset (default: 0)
- `sort`: Sort field (created_at, priority, status)
- `order`: Sort order (asc, desc)

**Example:**
```http
GET /tasks?status=completed&type=research&limit=10&sort=created_at&order=desc
```

**Response:**
```json
{
    "tasks": [
        {
            "task_id": "task_123",
            "type": "research",
            "description": "Analyze quantum computing trends",
            "status": "completed",
            "priority": 2,
            "created_at": "2024-01-15T10:30:00Z",
            "completed_at": "2024-01-15T11:00:47Z"
        }
    ],
    "total": 1,
    "limit": 10,
    "offset": 0,
    "has_more": false
}
```

## 🤖 **Agent Management**

### **List Agents**

#### `GET /agents`
Get list of all registered agents.

**Response:**
```json
{
    "agents": [
        {
            "agent_id": "research_agent_001",
            "name": "Research Agent Alpha",
            "type": "research",
            "status": "active",
            "capabilities": ["literature_review", "trend_analysis", "data_synthesis"],
            "current_load": 2,
            "max_capacity": 5,
            "performance_metrics": {
                "tasks_completed": 156,
                "average_completion_time": "1200s",
                "success_rate": 0.98
            },
            "last_seen": "2024-01-15T10:35:00Z"
        }
    ],
    "total_agents": 8,
    "active_agents": 8,
    "total_capacity": 40,
    "current_load": 15
}
```

### **Get Agent Details**

#### `GET /agents/{agent_id}`
Get detailed information about a specific agent.

**Response:**
```json
{
    "agent_id": "research_agent_001",
    "name": "Research Agent Alpha",
    "type": "research",
    "status": "active",
    "capabilities": ["literature_review", "trend_analysis", "data_synthesis"],
    "configuration": {
        "max_concurrent_tasks": 5,
        "timeout_seconds": 3600,
        "memory_limit": "4GB"
    },
    "current_tasks": [
        {
            "task_id": "task_456",
            "description": "Market analysis for Q1 2024",
            "started_at": "2024-01-15T10:25:00Z",
            "progress": 78
        }
    ],
    "performance_history": [
        {
            "date": "2024-01-14",
            "tasks_completed": 12,
            "average_time": "1100s",
            "success_rate": 1.0
        }
    ],
    "last_updated": "2024-01-15T10:35:00Z"
}
```

## 🔍 **Search & Intelligence**

### **Semantic Search**

#### `POST /search/semantic`
Perform semantic search across the knowledge base.

**Request:**
```json
{
    "query": "quantum computing applications in machine learning",
    "limit": 10,
    "threshold": 0.7,
    "filters": {
        "document_type": ["paper", "article"],
        "date_range": {
            "start": "2023-01-01",
            "end": "2024-01-15"
        }
    }
}
```

**Response:**
```json
{
    "results": [
        {
            "id": "doc_789",
            "title": "Quantum Machine Learning: A Survey",
            "content_snippet": "Quantum computing offers exponential speedups for certain machine learning algorithms...",
            "similarity_score": 0.94,
            "source": "Nature Quantum Information",
            "metadata": {
                "authors": ["Alice Smith", "Bob Johnson"],
                "publication_date": "2023-12-15",
                "document_type": "paper"
            }
        }
    ],
    "total_results": 47,
    "query_time": "45ms",
    "search_id": "search_123"
}
```

### **Knowledge Graph Query**

#### `POST /graph/query`
Execute Cypher queries on the knowledge graph.

**Request:**
```json
{
    "query": "MATCH (a:Agent)-[:EXECUTED]->(t:Task) WHERE t.type = 'research' RETURN a.name, COUNT(t) as task_count ORDER BY task_count DESC LIMIT 5",
    "parameters": {}
}
```

**Response:**
```json
{
    "results": [
        {"a.name": "Research Agent Alpha", "task_count": 156},
        {"a.name": "Research Agent Beta", "task_count": 142},
        {"a.name": "Research Agent Gamma", "task_count": 98}
    ],
    "execution_time": "12ms",
    "query_id": "query_456"
}
```

## 🔄 **Workflows**

### **Create Workflow**

#### `POST /workflows`
Create a new multi-agent workflow.

**Request:**
```json
{
    "name": "Comprehensive Threat Analysis",
    "description": "Multi-stage threat analysis workflow",
    "steps": [
        {
            "id": "step1",
            "type": "osint",
            "description": "Collect threat intelligence",
            "agent_requirements": ["osint"],
            "parameters": {
                "sources": ["threat_feeds", "social_media"],
                "timeframe": "24h"
            }
        },
        {
            "id": "step2",
            "type": "data_analysis",
            "description": "Analyze collected data",
            "depends_on": ["step1"],
            "agent_requirements": ["data_analysis"],
            "parameters": {
                "analysis_type": "pattern_detection"
            }
        }
    ],
    "schedule": {
        "type": "cron",
        "expression": "0 */6 * * *"
    }
}
```

### **Execute Workflow**

#### `POST /workflows/{workflow_id}/execute`
Execute a workflow with parameters.

**Request:**
```json
{
    "parameters": {
        "threat_types": ["malware", "phishing"],
        "sources": ["threat_feeds", "social_media"],
        "timeframe": "24h"
    }
}
```

**Response:**
```json
{
    "execution_id": "exec_789",
    "workflow_id": "threat_analysis_001",
    "status": "running",
    "started_at": "2024-01-15T10:30:00Z",
    "estimated_completion": "2024-01-15T11:30:00Z"
}
```

## 📊 **Monitoring & Metrics**

### **System Metrics**

#### `GET /metrics`
Get Prometheus-compatible metrics.

**Response:**
```
# HELP amas_tasks_total Total number of tasks processed
# TYPE amas_tasks_total counter
amas_tasks_total{status="completed"} 1547
amas_tasks_total{status="failed"} 23

# HELP amas_agents_active Number of active agents
# TYPE amas_agents_active gauge
amas_agents_active 8

# HELP amas_task_duration_seconds Task execution duration
# TYPE amas_task_duration_seconds histogram
amas_task_duration_seconds_bucket{le="10"} 100
amas_task_duration_seconds_bucket{le="30"} 500
amas_task_duration_seconds_bucket{le="60"} 800
amas_task_duration_seconds_bucket{le="+Inf"} 1000
```

### **Performance Stats**

#### `GET /stats`
Get detailed performance statistics.

**Response:**
```json
{
    "system": {
        "uptime_seconds": 86400,
        "memory_usage_mb": 2048,
        "cpu_usage_percent": 45.2,
        "gpu_usage_percent": 23.1
    },
    "tasks": {
        "total_processed": 1547,
        "completed": 1524,
        "failed": 23,
        "average_duration_seconds": 45.2
    },
    "agents": {
        "total": 8,
        "active": 8,
        "idle": 0,
        "busy": 3
    },
    "services": {
        "llm_service": {
            "status": "healthy",
            "response_time_ms": 120,
            "requests_per_minute": 45
        },
        "vector_service": {
            "status": "healthy",
            "response_time_ms": 15,
            "index_size": 1000000
        }
    }
}
```

## 🚨 **Error Handling**

### **Standard Error Response**

```json
{
    "error": {
        "code": "INVALID_TASK_TYPE",
        "message": "The specified task type 'invalid_type' is not supported",
        "details": {
            "supported_types": ["research", "osint", "forensics", "data_analysis", "reporting"]
        },
        "timestamp": "2024-01-15T10:30:00Z",
        "request_id": "req_123456"
    }
}
```

### **HTTP Status Codes**

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error
- `503` - Service Unavailable

## 🔒 **Rate Limiting**

API endpoints are rate limited to ensure fair usage:

- **Authentication**: 10 requests/minute
- **Task Submission**: 100 requests/hour
- **Status Queries**: 1000 requests/hour
- **Search Operations**: 500 requests/hour

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

## 🔔 **Webhooks**

Subscribe to real-time updates via webhooks.

### **Configure Webhook**

#### `POST /webhooks`
```json
{
    "url": "https://your-app.com/webhook",
    "events": ["task.completed", "task.failed", "agent.status_changed"],
    "secret": "your-webhook-secret"
}
```

### **Webhook Events**

#### `task.completed`
```json
{
    "event": "task.completed",
    "task_id": "task_123",
    "agent_id": "research_agent_001",
    "completion_time": "2024-01-15T11:00:47Z",
    "result_summary": "Research completed successfully with 247 sources analyzed"
}
```

## 📚 **SDK and Client Libraries**

### **Python SDK**

```python
from amas_sdk import AMASClient

client = AMASClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Submit task
task = await client.tasks.submit(
    type="research",
    description="Analyze AI trends"
)

# Get result
result = await client.tasks.get_result(task.id)
```

### **JavaScript/Node.js SDK**

```javascript
import { AMASClient } from '@amas/sdk';

const client = new AMASClient({
    baseUrl: 'http://localhost:8000',
    apiKey: 'your-api-key'
});

// Submit task
const task = await client.tasks.submit({
    type: 'research',
    description: 'Analyze AI trends'
});

// Get result
const result = await client.tasks.getResult(task.id);
```

## 📖 **OpenAPI Specification**

The complete OpenAPI 3.0 specification is available at:
- **JSON**: `/openapi.json`
- **Interactive Docs**: `/docs`
- **ReDoc**: `/redoc`

## 🧪 **Examples**

### **Complete Task Workflow**

```python
import asyncio
import aiohttp

async def complete_workflow_example():
    base_url = "http://localhost:8000"
    headers = {"Authorization": "Bearer your-token-here"}
    
    async with aiohttp.ClientSession() as session:
        # Submit research task
        async with session.post(
            f"{base_url}/tasks",
            json={
                "type": "research",
                "description": "Research blockchain applications in healthcare",
                "priority": 2
            },
            headers=headers
        ) as response:
            task = await response.json()
            task_id = task["task_id"]
        
        # Monitor progress
        while True:
            async with session.get(
                f"{base_url}/tasks/{task_id}",
                headers=headers
            ) as response:
                status = await response.json()
                
                if status["status"] in ["completed", "failed"]:
                    break
                    
                print(f"Progress: {status.get('progress', 0)}%")
                await asyncio.sleep(10)
        
        # Get final result
        async with session.get(
            f"{base_url}/tasks/{task_id}/result",
            headers=headers
        ) as response:
            result = await response.json()
            print(f"Task completed: {result}")

asyncio.run(complete_workflow_example())
```

### **Batch Task Processing**

```python
async def batch_processing_example():
    tasks = [
        {"type": "research", "description": "AI in healthcare"},
        {"type": "research", "description": "AI in finance"},
        {"type": "research", "description": "AI in education"}
    ]
    
    # Submit all tasks
    task_ids = []
    for task_data in tasks:
        task = await client.tasks.submit(**task_data)
        task_ids.append(task.id)
    
    # Wait for all completions
    results = await client.tasks.wait_for_completion(task_ids)
    
    for result in results:
        print(f"Task {result.task_id}: {result.status}")
```

## 🎯 **Best Practices**

### **Efficient API Usage**

1. **Batch Operations**: Submit multiple tasks together when possible
2. **Polling Optimization**: Use appropriate polling intervals (10-30 seconds)
3. **Caching**: Cache frequently accessed data locally
4. **Error Handling**: Implement exponential backoff for retries
5. **Rate Limiting**: Respect rate limits and implement queuing

### **Security Best Practices**

1. **Token Management**: Refresh tokens before expiration
2. **HTTPS Only**: Always use HTTPS in production
3. **Input Validation**: Validate all data before sending
4. **Secrets Management**: Never hardcode API keys
5. **Audit Logging**: Log all API interactions

### **Performance Optimization**

1. **Async Operations**: Use async/await for concurrent requests
2. **Connection Pooling**: Reuse HTTP connections
3. **Compression**: Enable gzip compression
4. **Timeouts**: Set appropriate request timeouts
5. **Monitoring**: Track API performance metrics

---

## 🔄 **Recent Updates**

### **v1.0.0 - API Integration Fixes**

#### ✅ **Fixed Issues**
- Corrected all API endpoint implementations
- Fixed authentication and authorization flows
- Updated response formats to match actual implementation
- Resolved service integration issues
- Added proper error handling and validation

#### ✅ **New Features**
- Enhanced task management endpoints
- Improved agent monitoring capabilities
- Added comprehensive search functionality
- Implemented workflow management
- Added real-time monitoring and metrics

#### ✅ **Performance Improvements**
- Optimized API response times
- Improved concurrent request handling
- Enhanced error reporting
- Better resource utilization

---

**For more information:**
- [User Guide](../docs/user/README.md)
- [Developer Guide](../docs/developer/README.md)
- [Authentication Guide](authentication.md)
- [Rate Limiting Guide](rate-limiting.md)