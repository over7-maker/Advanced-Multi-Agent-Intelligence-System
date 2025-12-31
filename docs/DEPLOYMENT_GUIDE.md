# AMAS Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Deployment](#development-deployment)
3. [Staging Deployment](#staging-deployment)
4. [Production Deployment](#production-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Docker Compose Deployment](#docker-compose-deployment)
7. [Post-Deployment Verification](#post-deployment-verification)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Python** 3.11+
- **Node.js** 18+ and **npm** 9+
- **PostgreSQL** 15+ (if not using Docker)
- **Redis** 7+ (if not using Docker)
- **Neo4j** 5+ (if not using Docker)

### Required Accounts

- GitHub account (for CI/CD)
- Container registry access (GHCR, Docker Hub, etc.)
- Domain name (for production)
- SSL certificate (Let's Encrypt recommended)

### Required Secrets

- Database passwords
- Redis password
- Neo4j password
- JWT secret key
- API keys for 16 AI providers
- Integration tokens (GitHub, Slack, etc.)

## Development Deployment

### 1. Clone Repository

```bash
git clone https://github.com/your-org/amas.git
cd amas
```

### 2. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 3. Start Databases

```bash
# Windows
scripts\start_databases.bat

# Linux/Mac
./scripts/start_databases.sh
```

### 4. Start Backend

```bash
# Windows
set ENVIRONMENT=development
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000 --reload

# Linux/Mac
export ENVIRONMENT=development
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

### 6. Verify Deployment

- Backend: http://localhost:8000/health
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

## Staging Deployment

### 1. Build Docker Images

```bash
docker build -t amas-backend:staging .
cd frontend
docker build -t amas-frontend:staging -f Dockerfile .
```

### 2. Start Services

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Run Migrations

```bash
docker-compose exec amas-backend alembic upgrade head
```

### 4. Verify Deployment

```bash
# Check all services
docker-compose ps

# Check logs
docker-compose logs -f amas-backend

# Test health endpoint
curl http://localhost:8000/health
```

## Production Deployment

### Option 1: Docker Compose

#### 1. Prepare Production Environment

```bash
# Create production .env file
cp .env.example .env.production

# Set production values
export ENVIRONMENT=production
export SECRET_KEY=$(openssl rand -hex 32)
export DB_PASSWORD=$(openssl rand -hex 16)
export REDIS_PASSWORD=$(openssl rand -hex 16)
export NEO4J_PASSWORD=$(openssl rand -hex 16)
```

#### 2. Build Production Images

```bash
docker build -t amas-backend:latest .
cd frontend
npm run build:prod
```

#### 3. Start Production Stack

```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### 4. Configure Nginx

```bash
# Copy nginx config
cp nginx/nginx.conf.example nginx/nginx.conf

# Update domain name
sed -i 's/your-domain.com/amas.example.com/g' nginx/nginx.conf

# Restart nginx
docker-compose restart nginx
```

### Option 2: Kubernetes

#### 1. Prepare Kubernetes Cluster

```bash
# Create namespace
kubectl create namespace amas-production

# Create secrets
kubectl create secret generic amas-secrets \
  --from-literal=DB_PASSWORD=your_password \
  --from-literal=SECRET_KEY=your_secret_key \
  --from-literal=REDIS_PASSWORD=your_redis_password \
  --from-literal=NEO4J_PASSWORD=your_neo4j_password \
  -n amas-production
```

#### 2. Apply Kubernetes Manifests

```bash
# Apply all manifests
kubectl apply -f k8s/deployment-production.yaml
kubectl apply -f k8s/service-production.yaml
kubectl apply -f k8s/ingress-production.yaml
kubectl apply -f k8s/configmap-production.yaml
kubectl apply -f k8s/hpa-production.yaml
```

#### 3. Verify Deployment

```bash
# Check pods
kubectl get pods -n amas-production

# Check services
kubectl get svc -n amas-production

# Check ingress
kubectl get ingress -n amas-production

# Check logs
kubectl logs -f deployment/amas-backend -n amas-production
```

#### 4. Set Up SSL/TLS

```bash
# Install cert-manager (if not already installed)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f k8s/cert-manager-issuer.yaml

# SSL will be automatically provisioned by cert-manager
```

## Kubernetes Deployment

### Complete Production Setup

1. **Create Namespace**
   ```bash
   kubectl create namespace amas-production
   ```

2. **Create Secrets**
   ```bash
   kubectl create secret generic amas-secrets \
     --from-file=secrets.yaml \
     -n amas-production
   ```

3. **Apply ConfigMap**
   ```bash
   kubectl apply -f k8s/configmap-production.yaml
   ```

4. **Deploy Application**
   ```bash
   kubectl apply -f k8s/deployment-production.yaml
   ```

5. **Create Services**
   ```bash
   kubectl apply -f k8s/service-production.yaml
   ```

6. **Set Up Ingress**
   ```bash
   kubectl apply -f k8s/ingress-production.yaml
   ```

7. **Configure HPA**
   ```bash
   kubectl apply -f k8s/hpa-production.yaml
   ```

### Rolling Updates

```bash
# Update image
kubectl set image deployment/amas-backend \
  amas-backend=your-registry/amas-backend:new-version \
  -n amas-production

# Monitor rollout
kubectl rollout status deployment/amas-backend -n amas-production

# Rollback if needed
kubectl rollout undo deployment/amas-backend -n amas-production
```

## Docker Compose Deployment

### Production Stack

The production Docker Compose stack includes 15 services:

1. **amas-backend** - Main application
2. **nginx** - Reverse proxy
3. **postgres** - Primary database
4. **redis** - Cache layer
5. **neo4j** - Graph database
6. **prometheus** - Metrics collection
7. **grafana** - Dashboards
8. **jaeger** - Distributed tracing
9. **alertmanager** - Alert management
10. **node-exporter** - System metrics
11. **cadvisor** - Container metrics
12. **postgres-exporter** - Database metrics
13. **redis-exporter** - Cache metrics
14. **loki** - Log aggregation
15. **promtail** - Log shipper

### Start Production Stack

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Stop Production Stack

```bash
# Stop all services
docker-compose -f docker-compose.prod.yml down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose -f docker-compose.prod.yml down -v
```

## Post-Deployment Verification

### 1. Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/health/ready

# Liveness check
curl http://localhost:8000/health/live
```

### 2. Database Connectivity

```bash
# PostgreSQL
docker-compose exec postgres psql -U amas -d amas -c "SELECT 1"

# Redis
docker-compose exec redis redis-cli ping

# Neo4j
docker-compose exec neo4j cypher-shell -u neo4j -p password "RETURN 1"
```

### 3. API Endpoints

```bash
# Test API
curl http://localhost:8000/api/v1/health

# Test authentication
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
```

### 4. Monitoring

```bash
# Prometheus
curl http://localhost:9090/-/healthy

# Grafana
curl http://localhost:3001/api/health

# Jaeger
curl http://localhost:16686/
```

### 5. Create Test Task

```bash
# Get token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}' | jq -r '.access_token')

# Create task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "task_type": "security_scan",
    "target": "example.com",
    "priority": 5
  }'
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

```bash
# Check database status
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Verify connection string
echo $DATABASE_URL
```

#### 2. Redis Connection Failed

```bash
# Check Redis status
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping
```

#### 3. Port Already in Use

```bash
# Find process using port
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Kill process
kill -9 <PID>
```

#### 4. Docker Network Issues

```bash
# Remove conflicting networks
docker network prune

# Recreate network
docker-compose down
docker-compose up -d
```

#### 5. Kubernetes Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n amas-production

# Check logs
kubectl logs <pod-name> -n amas-production

# Check events
kubectl get events -n amas-production --sort-by='.lastTimestamp'
```

### Logs

#### Docker Compose

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f amas-backend

# Last 100 lines
docker-compose logs --tail=100 amas-backend
```

#### Kubernetes

```bash
# Pod logs
kubectl logs -f deployment/amas-backend -n amas-production

# Previous container logs
kubectl logs -f deployment/amas-backend -n amas-production --previous

# All pods
kubectl logs -f -l app=amas-backend -n amas-production
```

### Performance Issues

1. **Check resource usage**
   ```bash
   # Docker
   docker stats
   
   # Kubernetes
   kubectl top pods -n amas-production
   ```

2. **Check database performance**
   ```bash
   # PostgreSQL
   docker-compose exec postgres psql -U amas -d amas -c "SELECT * FROM pg_stat_activity;"
   ```

3. **Check cache hit rate**
   ```bash
   # Redis
   docker-compose exec redis redis-cli INFO stats | grep keyspace
   ```

## Backup and Recovery

### Database Backups

```bash
# PostgreSQL backup
docker-compose exec postgres pg_dump -U amas amas > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U amas amas < backup_20240101.sql
```

### Neo4j Backups

```bash
# Neo4j backup
docker-compose exec neo4j neo4j-admin database backup neo4j --backup-dir=/backups
```

### Automated Backups

Set up cron job or Kubernetes CronJob for automated backups.

## Security Checklist

- [ ] All secrets stored in secure vault (Kubernetes secrets, external secrets)
- [ ] SSL/TLS enabled for all external endpoints
- [ ] Rate limiting configured
- [ ] Security headers configured (CSP, HSTS, etc.)
- [ ] Database access restricted to application network
- [ ] Redis password enabled
- [ ] Neo4j authentication enabled
- [ ] API keys rotated regularly
- [ ] Audit logging enabled
- [ ] Monitoring and alerting configured

## Next Steps

1. Configure monitoring dashboards
2. Set up alerting rules
3. Configure backup schedules
4. Set up CI/CD pipeline
5. Configure load balancing
6. Set up auto-scaling
7. Configure disaster recovery procedures
