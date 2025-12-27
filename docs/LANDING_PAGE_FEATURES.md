# Landing Page Features - Complete Guide

## Overview

This document describes the complete landing page integration features including database migration, email service, error handling, and testing.

---

## 1. Database Migration - Feedback Table

### Migration File
`alembic/versions/004_add_feedback_table.py`

### Schema
```sql
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    feedback_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    sentiment VARCHAR(50),  -- 'positive', 'neutral', 'negative'
    page_context VARCHAR(255),  -- Which page the feedback came from
    email_sent BOOLEAN DEFAULT false,
    email_sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes
- `ix_feedback_feedback_id` - Primary lookup
- `ix_feedback_email` - Email queries
- `ix_feedback_created_at` - Time-based queries
- `ix_feedback_sentiment` - Sentiment analysis
- `ix_feedback_email_sent` - Email tracking

### Usage
```bash
# Run migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

---

## 2. Email Service

### Service Location
`src/amas/services/email_service.py`

### Configuration
Set these environment variables:

```bash
# Enable email service
EMAIL_ENABLED=true

# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@amas.ai
SMTP_FROM_NAME=AMAS Intelligence System
```

### Features
- **HTML Email Templates**: Beautiful, responsive email design
- **Plain Text Fallback**: For email clients that don't support HTML
- **Error Handling**: Graceful fallback when email service unavailable
- **Background Tasks**: Non-blocking email sending

### Usage
```python
from src.amas.services.email_service import get_email_service

email_service = get_email_service()
result = await email_service.send_feedback_confirmation(
    to_email="user@example.com",
    to_name="John Doe",
    feedback_id="feedback-123"
)

if result["status"] == "success":
    print("Email sent successfully")
```

### Email Template
The confirmation email includes:
- Professional HTML design
- Thank you message
- Feedback ID for reference
- Branding and footer

---

## 3. Enhanced Error Handling (Frontend)

### Improvements Made

#### MonitoringDashboard Component
- **Error State**: Displays user-friendly error messages
- **Retry Mechanism**: Automatic retry with exponential backoff
- **Loading States**: Clear loading indicators
- **Fallback Data**: Uses mock data when API unavailable

#### API Client (`frontend/src/lib/api.ts`)
- **Timeout Handling**: 10-second timeout for all requests
- **AbortController**: Proper request cancellation
- **Input Validation**: Validates API response structure
- **Data Sanitization**: Clamps values to valid ranges
- **Error Logging**: Detailed error messages for debugging

### Error States

```typescript
// Error display in MonitoringDashboard
if (error && !metrics) {
  return (
    <section>
      <AlertCircle />
      <h3>Failed to Load Dashboard</h3>
      <p>{error}</p>
      <button onClick={loadData}>Retry</button>
    </section>
  );
}
```

### Timeout Configuration
```typescript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 10000);

const response = await fetch(url, {
  signal: controller.signal,
  // ...
});
```

---

## 4. Comprehensive Tests

### Test File
`tests/api/test_landing_endpoints.py`

### Test Coverage

#### TestLandingMetrics
- ✅ Successful metrics retrieval
- ✅ Metrics with database integration
- ✅ Fallback when services unavailable

#### TestLandingAgentsStatus
- ✅ Successful agent status retrieval
- ✅ Fallback when orchestrator unavailable

#### TestLandingDemoData
- ✅ Successful demo data retrieval

#### TestLandingFeedback
- ✅ Successful feedback submission
- ✅ Invalid email validation
- ✅ Missing fields validation
- ✅ Database storage
- ✅ Fallback without database

#### TestLandingHealth
- ✅ Health check endpoint

#### TestLandingEmailService
- ✅ Email sending when enabled
- ✅ Email skipping when disabled

#### TestLandingEndpointsIntegration
- ✅ All endpoints are public (no auth required)
- ✅ Feedback endpoint is public

### Running Tests
```bash
# Run all landing endpoint tests
pytest tests/api/test_landing_endpoints.py -v

# Run specific test class
pytest tests/api/test_landing_endpoints.py::TestLandingMetrics -v

# Run with coverage
pytest tests/api/test_landing_endpoints.py --cov=src.api.routes.landing --cov-report=html
```

---

## 5. API Endpoints

### Public Endpoints (No Authentication Required)

#### GET `/api/v1/landing/health`
Health check for landing page service.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-27T14:00:00",
  "service": "AMAS Landing Page"
}
```

#### GET `/api/v1/landing/metrics`
Get system metrics for dashboard.

**Response:**
```json
{
  "cpu_usage_percent": 45.5,
  "memory_usage_percent": 60.0,
  "active_tasks": 10,
  "completed_tasks": 500,
  "failed_tasks": 5,
  "active_agents": 12,
  "queue_depth": 0,
  "uptime_hours": 24.0,
  "avg_task_duration": 30.5,
  "success_rate": 0.95
}
```

#### GET `/api/v1/landing/agents-status`
Get status of all agents.

**Response:**
```json
[
  {
    "agent_id": "security_expert",
    "name": "Security Expert",
    "status": "active",
    "executions_today": 45,
    "success_rate": 0.98,
    "avg_response_time": 3.2,
    "specialization": "security-analysis"
  }
]
```

#### GET `/api/v1/landing/demo-data`
Get demo data for interactive examples.

**Response:**
```json
{
  "sample_task_id": "task-demo-001",
  "sample_agents": ["security_expert", "intelligence_gathering"],
  "estimated_duration": 45.0,
  "estimated_cost": 2.50,
  "quality_prediction": 0.95
}
```

#### POST `/api/v1/landing/feedback`
Submit user feedback.

**Request:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "message": "Great product!",
  "sentiment": "positive",
  "page_context": "landing"
}
```

**Response:**
```json
{
  "feedback_id": "feedback-1735315200",
  "message": "Thank you! Your feedback has been received.",
  "timestamp": "2025-12-27T14:00:00"
}
```

---

## 6. Environment Variables

### Required for Email Service
```bash
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@amas.ai
SMTP_FROM_NAME=AMAS Intelligence System
```

### Optional
```bash
# Frontend API URL
VITE_API_URL=http://localhost:8000/api/v1

# Database (for feedback storage)
DATABASE_URL=postgresql://user:password@localhost:5432/amas
```

---

## 7. Production Deployment

### Steps

1. **Run Database Migration**
   ```bash
   alembic upgrade head
   ```

2. **Configure Email Service**
   - Set `EMAIL_ENABLED=true`
   - Configure SMTP settings
   - Test email sending

3. **Deploy Frontend**
   - Set `VITE_API_URL` to production API URL
   - Build and deploy frontend

4. **Verify Endpoints**
   - Test all landing endpoints
   - Verify email sending
   - Check error handling

### Monitoring

- Monitor feedback table growth
- Track email delivery rates
- Monitor API response times
- Check error logs

---

## 8. Troubleshooting

### Email Not Sending
- Check `EMAIL_ENABLED=true`
- Verify SMTP credentials
- Check SMTP server connectivity
- Review email service logs

### Database Errors
- Verify database connection
- Check migration status: `alembic current`
- Verify table exists: `SELECT * FROM feedback LIMIT 1;`

### Frontend Errors
- Check browser console for errors
- Verify `VITE_API_URL` is set correctly
- Check CORS configuration
- Verify API endpoints are accessible

---

## 9. Future Enhancements

- [ ] Email template customization
- [ ] Feedback analytics dashboard
- [ ] Sentiment analysis integration
- [ ] Automated response emails
- [ ] Feedback categorization
- [ ] Admin feedback management UI

---

## 10. Support

For issues or questions:
- Check logs: `tail -f logs/amas.log`
- Review test results: `pytest tests/api/test_landing_endpoints.py -v`
- Check API docs: `http://localhost:8000/docs`

---

**Last Updated:** December 27, 2025  
**Version:** 1.0.0

