# AMAS API Documentation (Phase 7.4)

## Base URL

Production: `https://your-domain.com/api/v1`  
Development: `http://localhost:8000/api/v1`

## Authentication

All API endpoints (except public endpoints) require JWT authentication.

### Get Access Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Using the Token

Include the token in the Authorization header:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Core Endpoints

### Tasks

#### Create Task
```http
POST /api/v1/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Security Scan",
  "description": "Scan example.com for vulnerabilities",
  "task_type": "security_scan",
  "target": "example.com",
  "priority": 5,
  "parameters": {}
}
```

Response includes ML prediction:
```json
{
  "id": "task_20250121_120000_abc12345",
  "title": "Security Scan",
  "status": "pending",
  "prediction": {
    "success_probability": 0.85,
    "estimated_duration": 120.0,
    "quality_score_prediction": 0.9,
    "recommended_agents": [...]
  },
  "assigned_agents": ["security_expert"]
}
```

#### Execute Task
```http
POST /api/v1/tasks/{task_id}/execute
Authorization: Bearer <token>
```

#### Get Task Status
```http
GET /api/v1/tasks/{task_id}
Authorization: Bearer <token>
```

#### Get Task Progress (WebSocket)
```javascript
const ws = new WebSocket('wss://your-domain.com/ws?token=<token>');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.event === 'task_progress') {
    console.log('Progress:', data.data.percentage);
  }
};
```

### Agents

#### List Agents
```http
GET /api/v1/agents
Authorization: Bearer <token>
```

#### Get Agent Status
```http
GET /api/v1/agents/{agent_id}
Authorization: Bearer <token>
```

### System

#### Orchestrator Status
```http
GET /api/v1/system/orchestrator/status
Authorization: Bearer <token>
```

Response:
```json
{
  "orchestrator_status": "active",
  "active_agents": 15,
  "active_tasks": 3,
  "total_tasks": 1250,
  "metrics": {
    "tasks_processed": 1250,
    "tasks_completed": 1180,
    "tasks_failed": 70,
    "average_task_time": 45.2
  },
  "agent_health": {...}
}
```

#### System Health
```http
GET /api/v1/system/health
```

#### System Metrics
```http
GET /api/v1/system/metrics
Authorization: Bearer <token>
```

### Predictions

#### Predict Task Outcome
```http
POST /api/v1/predictions/predict/task
Authorization: Bearer <token>
Content-Type: application/json

{
  "task_type": "security_scan",
  "target": "example.com",
  "parameters": {}
}
```

### Integrations

#### List Integrations
```http
GET /api/v1/integrations
Authorization: Bearer <token>
```

#### Create Integration
```http
POST /api/v1/integrations
Authorization: Bearer <token>
Content-Type: application/json

{
  "platform": "github",
  "credentials": {
    "token": "ghp_..."
  }
}
```

## WebSocket Events

Connect to `wss://your-domain.com/ws?token=<token>`

### Events Received

- `connected` - Connection established
- `task_created` - New task created
- `task_execution_started` - Task execution begins
- `task_progress` - Progress update (0-100%)
- `agent_started` - Agent begins work
- `agent_completed` - Agent finishes
- `task_completed` - Task finished successfully
- `task_failed` - Task failed
- `heartbeat` - Keep-alive ping

### Commands Sent

```json
// Subscribe to task updates
{
  "command": "subscribe_task",
  "task_id": "task_123"
}

// Unsubscribe
{
  "command": "unsubscribe_task",
  "task_id": "task_123"
}

// Ping
{
  "command": "ping"
}
```

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR"
}
```

### Common Error Codes

- `VALIDATION_ERROR` - Invalid input data
- `AUTHENTICATION_REQUIRED` - Missing or invalid token
- `PERMISSION_DENIED` - Insufficient permissions
- `TASK_NOT_FOUND` - Task does not exist
- `AGENT_NOT_FOUND` - Agent does not exist
- `RATE_LIMIT_EXCEEDED` - Too many requests

## Rate Limiting

- API endpoints: 100 requests/second
- Authentication endpoints: 5 requests/second
- Per-user limits may apply

## Response Times

- Health checks: <50ms
- Task creation: <200ms
- Task execution: Variable (depends on task)
- Agent status: <100ms
- System metrics: <150ms

## Best Practices

1. **Always use HTTPS** in production
2. **Store tokens securely** (not in localStorage for sensitive apps)
3. **Handle WebSocket reconnection** automatically
4. **Implement exponential backoff** for retries
5. **Monitor rate limits** and adjust request frequency
6. **Use WebSocket for real-time updates** instead of polling

## SDK Examples

### Python
```python
import requests

base_url = "https://your-domain.com/api/v1"
token = "your_jwt_token"

headers = {"Authorization": f"Bearer {token}"}

# Create task
response = requests.post(
    f"{base_url}/tasks",
    json={
        "title": "Security Scan",
        "task_type": "security_scan",
        "target": "example.com"
    },
    headers=headers
)
task = response.json()
```

### JavaScript
```javascript
const API_URL = 'https://your-domain.com/api/v1';
const token = 'your_jwt_token';

// Create task
const response = await fetch(`${API_URL}/tasks`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Security Scan',
    task_type: 'security_scan',
    target: 'example.com'
  })
});

const task = await response.json();
```
