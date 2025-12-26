# 🚀 Landing Page Integration Guide

**Status:** ✅ Complete  
**Date:** December 26, 2025  
**Integration:** Lovable → AMAS Main Repository  
**Quality:** Production-Ready

---

## 📋 Overview

This document describes the complete integration of the Lovable landing page into the main AMAS repository. All components, APIs, Docker configuration, and documentation are production-ready.

### ✅ What Has Been Done

#### Frontend Integration
- ✅ Landing page components migrated
- ✅ Dark mode with theme switcher
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ TypeScript for type safety
- ✅ Vite for fast builds
- ✅ Production optimizations

#### Backend API
- ✅ `/api/v1/landing/metrics` - System metrics dashboard
- ✅ `/api/v1/landing/agents-status` - Agent status display
- ✅ `/api/v1/landing/demo-data` - Interactive demos
- ✅ `/api/v1/landing/feedback` - User feedback collection
- ✅ `/api/v1/landing/health` - Health check endpoint

#### Database
- ✅ PostgreSQL integration for feedback storage
- ✅ Feedback schema (email, name, message, sentiment, context)
- ✅ Automatic timestamp tracking

#### Docker
- ✅ Frontend containerization
- ✅ Multi-stage build (optimized image size)
- ✅ Health checks configured
- ✅ Docker-compose orchestration
- ✅ Automatic service startup

#### Documentation
- ✅ This guide (setup, deployment, troubleshooting)
- ✅ API documentation
- ✅ Architecture overview
- ✅ Environment configuration

---

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose (recommended)
- OR Node.js 18+ and Python 3.9+
- Git

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System

# Start all services
docker-compose up -d

# Wait for services to start (30-60 seconds)
sleep 30

# Access services:
# - Dashboard: http://localhost:3000 (or http://yourdomain.com/ui)
# - API: http://localhost:8000/api/v1
# - Docs: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Start backend
cd .
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in a new terminal)
cd frontend
npm install
npm run dev
```

---

## 📁 Project Structure

```
Advanced-Multi-Agent-Intelligence-System/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── landing.py          # Landing page endpoints
│   │       └── __init__.py
│   ├── main.py                     # FastAPI app
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── lib/
│   │   │   └── landing-api.ts      # API client
│   │   ├── hooks/
│   │   │   └── useTheme.ts         # Dark mode hook
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── Dockerfile                  # Frontend container
│   └── ...
├── docker-compose.yml              # Orchestration
├── LANDING_PAGE_INTEGRATION.md      # This file
├── requirements.txt
└── ...
```

---

## 🔌 API Endpoints

### Public Endpoints (No Authentication)

#### 1. Get System Metrics
```bash
GET /api/v1/landing/metrics

Response:
{
  "cpu_usage_percent": 25.5,
  "memory_usage_percent": 45.2,
  "active_tasks": 12,
  "completed_tasks": 542,
  "failed_tasks": 3,
  "active_agents": 7,
  "queue_depth": 2,
  "uptime_hours": 168.5,
  "avg_task_duration": 32.4,
  "success_rate": 0.9943
}
```

#### 2. Get Agent Status
```bash
GET /api/v1/landing/agents-status

Response:
[
  {
    "agent_id": "agent-001",
    "name": "Data Analyst",
    "status": "active",
    "executions_today": 45,
    "success_rate": 0.96,
    "avg_response_time": 5.2,
    "specialization": "data-analysis"
  },
  ...
]
```

#### 3. Get Demo Data
```bash
GET /api/v1/landing/demo-data

Response:
{
  "sample_task_id": "task-demo-001",
  "sample_agents": ["agent-001", "agent-002"],
  "estimated_duration": 35.5,
  "estimated_cost": 2.45,
  "quality_prediction": 0.92
}
```

#### 4. Submit User Feedback
```bash
POST /api/v1/landing/feedback

Request:
{
  "email": "user@example.com",
  "name": "John Doe",
  "message": "Great service!",
  "sentiment": "positive",
  "page_context": "/landing"
}

Response:
{
  "feedback_id": "feedback-1703585698.123",
  "message": "Thank you! Your feedback has been received.",
  "timestamp": "2025-12-26T08:35:00Z"
}
```

#### 5. Health Check
```bash
GET /api/v1/landing/health

Response:
{
  "status": "healthy",
  "timestamp": "2025-12-26T08:35:00Z",
  "service": "AMAS Landing Page"
}
```

---

## 🎨 Dark Mode

Dark mode is built-in and automatic:

```typescript
// In your components
import { useTheme } from '@/hooks/useTheme';

function MyComponent() {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <button onClick={toggleTheme}>
      Switch to {theme === 'light' ? 'dark' : 'light'} mode
    </button>
  );
}
```

Theme persists across page reloads using localStorage.

---

## 🗄️ Database Setup

Feedback is stored in PostgreSQL:

```sql
-- Feedback table (create if needed)
CREATE TABLE feedback (
  id SERIAL PRIMARY KEY,
  feedback_id VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  sentiment VARCHAR(50),
  page_context VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_feedback_email ON feedback(email);
CREATE INDEX idx_feedback_created_at ON feedback(created_at);
```

---

## 📊 Monitoring

Monitoring stack included:

- **Prometheus** - Metrics collection (port 9090)
- **Grafana** - Dashboards (port 3001, password: amas_grafana_password)

---

## 🔐 Environment Variables

Create a `.env` file in the root:

```env
# Database
DATABASE_URL=postgresql://postgres:amas_password@postgres:5432/amas

# Redis
REDIS_URL=redis://:amas_redis_password@redis:6379/0

# Neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=amas_password

# Frontend
VITE_API_URL=http://localhost:8000/api/v1

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
```

---

## 🐳 Docker Deployment

### Build Images
```bash
# Build all services
docker-compose build

# Build frontend only
docker-compose build frontend

# Build backend only
docker-compose build amas
```

### Start Services
```bash
# Start all
docker-compose up -d

# Start specific service
docker-compose up -d frontend

# View logs
docker-compose logs -f frontend
```

### Stop Services
```bash
# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## 🚀 Production Deployment

### Using Docker
```bash
# Set environment to production
export ENVIRONMENT=production

# Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Using Kubernetes (Optional)
```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods
```

### SSL/HTTPS
```bash
# The nginx reverse proxy handles SSL
# Configure certificates in ./nginx/ssl/
```

---

## 🧪 Testing

### Frontend Tests
```bash
cd frontend

# Run tests
npm run test

# Run with coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

### Backend Tests
```bash
# Run tests
pytest

# With coverage
pytest --cov=app
```

### Integration Tests
```bash
# Test API endpoints
curl -X GET http://localhost:8000/api/v1/landing/metrics
curl -X GET http://localhost:8000/api/v1/landing/health
```

---

## 🐛 Troubleshooting

### Frontend won't start
```bash
# Check logs
docker-compose logs frontend

# Rebuild
docker-compose build --no-cache frontend

# Check port
lsof -i :3000
```

### API connection errors
```bash
# Check backend is running
curl http://localhost:8000/health

# Check VITE_API_URL environment variable
echo $VITE_API_URL

# Update in frontend .env
VITE_API_URL=http://backend:8000/api/v1
```

### Database errors
```bash
# Check postgres is running
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

### Dark mode not working
```bash
# Clear localStorage
localStorage.clear()

# Check hook is imported correctly
import { useTheme } from '@/hooks/useTheme';
```

---

## 📚 Additional Resources

- [API Documentation](./docs/API.md)
- [Architecture Guide](./docs/ARCHITECTURE.md)
- [Contributing Guide](./CONTRIBUTING.md)
- [Lovable Landing Page](https://github.com/over7-maker/agent-evolution-hub)

---

## ✨ Features

### Frontend
- ✅ React 18 with TypeScript
- ✅ Vite for fast development
- ✅ Dark/Light mode toggle
- ✅ Responsive design
- ✅ Real-time metrics dashboard
- ✅ Interactive agent status display
- ✅ Demo sandbox
- ✅ Feedback form with validation
- ✅ Accessibility (WCAG 2.1 AA)

### Backend
- ✅ FastAPI framework
- ✅ PostgreSQL database
- ✅ Redis caching
- ✅ Authentication/Authorization
- ✅ Real-time updates (WebSocket ready)
- ✅ Error handling and logging
- ✅ CORS configured
- ✅ Health checks

### DevOps
- ✅ Docker containerization
- ✅ Docker Compose orchestration
- ✅ Kubernetes ready (with manifests)
- ✅ Prometheus monitoring
- ✅ Grafana dashboards
- ✅ CI/CD ready
- ✅ SSL/HTTPS support

---

## 🎯 Next Steps

1. **Test locally** - Run `docker-compose up` and test all endpoints
2. **Configure domain** - Update nginx config with your domain
3. **Setup SSL** - Add certificates to `./nginx/ssl/`
4. **Deploy** - Push to production environment
5. **Monitor** - Check Prometheus/Grafana dashboards

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs: `docker-compose logs -f`
3. Open an issue on GitHub
4. Contact: over7@su.edu.ye

---

## 📄 License

MIT License - See LICENSE file for details

---

**Integration Complete! 🎉**

Your landing page is now fully integrated with the AMAS system.

Your commands to start:
```bash
docker-compose up -d
```

Then visit: `http://localhost:3000` or `http://yourdomain.com/ui`
