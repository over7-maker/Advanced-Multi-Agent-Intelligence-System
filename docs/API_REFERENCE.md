# AMAS API Reference

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://amas.example.com`

## Authentication

All API endpoints (except `/health` and `/api/v1/landing`) require authentication.

### Authentication Methods

1. **JWT Token** (Recommended)
   ```http
   Authorization: Bearer <jwt_token>
   ```

2. **API Key**
   ```http
   X-API-Key: <api_key>
   ```

### Getting a Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "refresh_token_here"
}
```

## Endpoints

### Health Check

#### GET /health

Check system health.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

#### GET /health/ready

Check if system is ready to accept requests.

#### GET /health/live

Check if system is alive (liveness probe).

### Tasks

#### POST /api/v1/tasks

Create a new task.

**Request**:
```json
{
  "title": "Security Scan",
  "description": "Scan example.com for vulnerabilities",
  "task_type": "security_scan",
  "target": "example.com",
  "parameters": {
    "scan_depth": "deep",
    "include_cves": true
  },
  "priority": 5
}
```

**Response**:
```json
{
  "id": 1,
  "title": "Security Scan",
  "description": "Scan example.com for vulnerabilities",
  "status": "pending",
  "priority": 5,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET /api/v1/tasks

List all tasks with optional filtering.

**Query Parameters**:
- `status` (optional): Filter by status (pending, in_progress, completed, failed)
- `task_type` (optional): Filter by task type
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records (default: 10)

**Response**:
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Security Scan",
      "status": "completed",
      "priority": 5,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

#### GET /api/v1/tasks/{task_id}

Get a specific task by ID.

**Response**:
```json
{
  "id": 1,
  "title": "Security Scan",
  "description": "Scan example.com for vulnerabilities",
  "status": "completed",
  "priority": 5,
  "result": {
    "vulnerabilities_found": 3,
    "critical": 1,
    "high": 2
  },
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:05:00Z"
}
```

#### PUT /api/v1/tasks/{task_id}

Update a task.

**Request**:
```json
{
  "status": "in_progress",
  "priority": 7
}
```

#### DELETE /api/v1/tasks/{task_id}

Delete a task.

**Response**: 204 No Content

#### POST /api/v1/tasks/{task_id}/execute

Manually trigger task execution.

**Response**:
```json
{
  "message": "Task execution initiated",
  "task_id": 1
}
```

#### GET /api/v1/tasks/{task_id}/status

Get task status.

**Response**:
```json
{
  "task_id": 1,
  "status": "in_progress",
  "progress": 0.65
}
```

#### GET /api/v1/tasks/{task_id}/result

Get task result (only for completed tasks).

**Response**:
```json
{
  "task_id": 1,
  "result": {
    "vulnerabilities_found": 3,
    "details": [...]
  }
}
```

### Agents

#### GET /api/v1/agents

List all available agents.

**Response**:
```json
{
  "agents": [
    {
      "id": "security_expert",
      "name": "Security Expert Agent",
      "status": "active",
      "capabilities": ["port_scanning", "cve_lookup", "vulnerability_assessment"]
    }
  ]
}
```

#### GET /api/v1/agents/{agent_id}

Get agent details.

**Response**:
```json
{
  "id": "security_expert",
  "name": "Security Expert Agent",
  "status": "active",
  "capabilities": ["port_scanning", "cve_lookup"],
  "performance": {
    "total_executions": 150,
    "success_rate": 0.95,
    "average_duration": 12.5
  }
}
```

### Analytics

#### GET /api/v1/analytics/tasks

Get task analytics.

**Query Parameters**:
- `start_date` (optional): Start date (ISO 8601)
- `end_date` (optional): End date (ISO 8601)
- `group_by` (optional): Group by field (day, week, month)

**Response**:
```json
{
  "total_tasks": 1000,
  "completed_tasks": 950,
  "failed_tasks": 50,
  "average_duration": 25.5,
  "success_rate": 0.95,
  "by_status": {
    "completed": 950,
    "failed": 50
  }
}
```

#### GET /api/v1/analytics/agents

Get agent performance analytics.

**Response**:
```json
{
  "agents": [
    {
      "agent_id": "security_expert",
      "total_executions": 150,
      "success_rate": 0.95,
      "average_duration": 12.5,
      "total_cost": 45.50
    }
  ]
}
```

### Integrations

#### GET /api/v1/integrations

List all integrations.

**Response**:
```json
{
  "integrations": [
    {
      "id": "github",
      "name": "GitHub",
      "status": "connected",
      "type": "platform"
    }
  ]
}
```

#### POST /api/v1/integrations/{integration_id}/connect

Connect an integration.

**Request**:
```json
{
  "credentials": {
    "token": "github_token_here"
  }
}
```

#### DELETE /api/v1/integrations/{integration_id}/disconnect

Disconnect an integration.

### Testing

#### GET /api/v1/testing/agents

Test all agents.

**Response**:
```json
{
  "results": {
    "security_expert": {
      "status": "success",
      "duration": 1.2
    }
  }
}
```

#### GET /api/v1/testing/providers

Test all AI providers.

**Response**:
```json
{
  "results": {
    "cerebras": {
      "status": "success",
      "latency": 0.5
    }
  }
}
```

## WebSocket API

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

### Events

#### task.created
```json
{
  "event": "task.created",
  "data": {
    "task_id": 1,
    "title": "Security Scan",
    "status": "pending"
  }
}
```

#### task.updated
```json
{
  "event": "task.updated",
  "data": {
    "task_id": 1,
    "status": "in_progress",
    "progress": 0.5
  }
}
```

#### task.completed
```json
{
  "event": "task.completed",
  "data": {
    "task_id": 1,
    "status": "completed",
    "result": {...}
  }
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

- `VALIDATION_ERROR` (400): Request validation failed
- `UNAUTHORIZED` (401): Authentication required
- `FORBIDDEN` (403): Insufficient permissions
- `NOT_FOUND` (404): Resource not found
- `CONFLICT` (409): Resource conflict
- `INTERNAL_ERROR` (500): Internal server error
- `SERVICE_UNAVAILABLE` (503): Service temporarily unavailable

## Rate Limiting

Rate limits are applied per user:
- **60 requests per minute**
- **1000 requests per hour**
- **10000 requests per day**

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination:

```
GET /api/v1/tasks?skip=0&limit=10
```

Response includes pagination metadata:
```json
{
  "items": [...],
  "total": 100,
  "skip": 0,
  "limit": 10,
  "has_more": true
}
```

## Examples

### Python

```python
import requests

# Authenticate
response = requests.post('http://localhost:8000/api/v1/auth/login', json={
    'username': 'user@example.com',
    'password': 'password123'
})
token = response.json()['access_token']

# Create task
headers = {'Authorization': f'Bearer {token}'}
response = requests.post('http://localhost:8000/api/v1/tasks', json={
    'title': 'Security Scan',
    'task_type': 'security_scan',
    'target': 'example.com',
    'priority': 5
}, headers=headers)
task = response.json()
print(f"Created task: {task['id']}")
```

### JavaScript

```javascript
// Authenticate
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'user@example.com',
    password: 'password123'
  })
});
const { access_token } = await loginResponse.json();

// Create task
const taskResponse = await fetch('http://localhost:8000/api/v1/tasks', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Security Scan',
    task_type: 'security_scan',
    target: 'example.com',
    priority: 5
  })
});
const task = await taskResponse.json();
console.log(`Created task: ${task.id}`);
```

