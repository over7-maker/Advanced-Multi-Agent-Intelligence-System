# AMAS Deployment Guide

This guide provides comprehensive instructions for deploying the Advanced Multi-Agent Intelligence System (AMAS) in various environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Production Deployment](#production-deployment)
- [Docker Configuration](#docker-configuration)
- [Service Configuration](#service-configuration)
- [Monitoring Setup](#monitoring-setup)
- [Security Configuration](#security-configuration)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

## Prerequisites

### System Requirements

**Minimum Requirements:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB SSD
- OS: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2

**Recommended Requirements:**
- CPU: 8+ cores
- RAM: 32GB+
- Storage: 200GB+ SSD
- GPU: NVIDIA RTX 4080+ (for LLM operations)
- OS: Ubuntu 22.04 LTS

### Software Dependencies

1. **Docker & Docker Compose**
   ```bash
   # Ubuntu/Debian
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo usermod -aG docker $USER
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Python 3.11+** (for development)
   ```bash
   sudo apt update
   sudo apt install python3.11 python3.11-venv python3.11-pip
   ```

3. **Node.js 18+** (for web interface)
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

4. **Git**
   ```bash
   sudo apt install git
   ```

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System
```

### 2. Run Setup Script
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 3. Deploy the System
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh development deploy
```

### 4. Access the System
- **Web Interface**: http://localhost
- **API Documentation**: http://localhost:8000/docs
- **Grafana Dashboard**: http://localhost:3001
- **Neo4j Browser**: http://localhost:7474

## Development Setup

### Environment Setup

1. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Running Services

1. **Start Infrastructure Services**
   ```bash
   docker-compose up -d postgres redis neo4j
   ```

2. **Start Application Services**
   ```bash
   docker-compose up -d ollama vector-service amas-api
   ```

3. **Start Web Interface** (optional)
   ```bash
   cd web
   npm install
   npm start
   ```

### Development Workflow

1. **Run Tests**
   ```bash
   python -m pytest tests/ -v
   ```

2. **Run Linting**
   ```bash
   python -m flake8 src/
   python -m black src/
   ```

3. **Run API Server**
   ```bash
   python -m uvicorn src.amas.api.main:app --reload
   ```

## Production Deployment

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone and Configure

```bash
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System

# Configure production environment
cp .env.production .env
# Edit .env with production values
```

### 3. Deploy Production System

```bash
./scripts/deploy.sh production deploy
```

### 4. Configure SSL (Optional)

```bash
# Generate SSL certificates
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to Docker volume
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/nginx/ssl/key.pem
```

## Docker Configuration

### Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx LB      │    │   AMAS API      │    │   Vector Svc    │
│   Port: 80/443  │────│   Port: 8000    │────│   Port: 8001    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │    │     Neo4j       │
│   Port: 5432    │    │   Port: 6379    │    │ Port: 7474/7687│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Ollama      │    │   Prometheus    │    │    Grafana      │
│   Port: 11434   │    │   Port: 9090    │    │   Port: 3001    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Container Configuration

#### AMAS API Service
- **Image**: Custom build from `docker/Dockerfile`
- **Resources**: 2 CPU cores, 4GB RAM
- **Health Check**: HTTP GET `/health`
- **Restart Policy**: `unless-stopped`

#### Vector Service
- **Image**: Custom build from `docker/Dockerfile.vector`
- **Resources**: 1 CPU core, 2GB RAM
- **Health Check**: HTTP GET `/health`
- **Restart Policy**: `unless-stopped`

#### Database Services
- **PostgreSQL**: 2GB RAM, persistent storage
- **Redis**: 1GB RAM, persistent storage
- **Neo4j**: 4GB RAM, persistent storage

#### Monitoring Services
- **Prometheus**: 1GB RAM, 30-day retention
- **Grafana**: 1GB RAM, persistent dashboards

## Service Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AMAS_ENVIRONMENT` | Environment mode | `development` | Yes |
| `POSTGRES_PASSWORD` | Database password | `amas_secure_password_123` | Yes |
| `REDIS_PASSWORD` | Redis password | `amas_redis_password_123` | Yes |
| `NEO4J_AUTH` | Neo4j credentials | `neo4j/amas_neo4j_password_123` | Yes |
| `JWT_SECRET` | JWT signing secret | Random | Yes |
| `ENCRYPTION_KEY` | Data encryption key | Random | Yes |

### Database Configuration

#### PostgreSQL
```yaml
environment:
  POSTGRES_DB: amas
  POSTGRES_USER: amas
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
volumes:
  - postgres_data:/var/lib/postgresql/data
```

#### Redis
```yaml
command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
volumes:
  - redis_data:/data
```

#### Neo4j
```yaml
environment:
  NEO4J_AUTH: ${NEO4J_AUTH}
  NEO4J_PLUGINS: '["apoc", "graph-data-science"]'
volumes:
  - neo4j_data:/data
  - neo4j_logs:/logs
```

### API Configuration

#### Load Balancer (Nginx)
```nginx
upstream amas_api {
    server amas-api:8000;
    keepalive 32;
}

location /api/ {
    proxy_pass http://amas_api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

#### Rate Limiting
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req zone=api burst=20 nodelay;
```

## Monitoring Setup

### Prometheus Configuration

```yaml
scrape_configs:
  - job_name: 'amas-api'
    static_configs:
      - targets: ['amas-api:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

### Grafana Dashboards

1. **System Overview Dashboard**
   - CPU and Memory usage
   - Service health status
   - Request rates and response times

2. **AMAS Specific Dashboard**
   - Agent performance metrics
   - Task processing rates
   - Error rates and logs

3. **Database Dashboard**
   - Connection pools
   - Query performance
   - Storage usage

### Alerting Rules

```yaml
groups:
  - name: amas_alerts
    rules:
      - alert: AMASApiDown
        expr: up{job="amas-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "AMAS API is down"
```

## Security Configuration

### SSL/TLS Setup

1. **Generate Certificates**
   ```bash
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout docker/nginx/ssl/key.pem \
     -out docker/nginx/ssl/cert.pem
   ```

2. **Configure Nginx**
   ```nginx
   server {
       listen 443 ssl http2;
       ssl_certificate /etc/nginx/ssl/cert.pem;
       ssl_certificate_key /etc/nginx/ssl/key.pem;
   }
   ```

### Authentication

1. **JWT Configuration**
   ```python
   JWT_SECRET = "your-super-secret-key"
   JWT_ALGORITHM = "HS256"
   JWT_EXPIRATION = 3600  # 1 hour
   ```

2. **API Key Authentication**
   ```python
   API_KEYS = {
       "admin": "admin-api-key",
       "user": "user-api-key"
   }
   ```

### Network Security

1. **Firewall Rules**
   ```bash
   # Allow only necessary ports
   ufw allow 22    # SSH
   ufw allow 80    # HTTP
   ufw allow 443   # HTTPS
   ufw enable
   ```

2. **Docker Network Isolation**
   ```yaml
   networks:
     amas-network:
       driver: bridge
       ipam:
         config:
           - subnet: 172.20.0.0/16
   ```

## Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check logs
docker-compose logs amas-api

# Check service status
docker-compose ps

# Restart service
docker-compose restart amas-api
```

#### 2. Database Connection Issues
```bash
# Check database status
docker-compose exec postgres pg_isready

# Check connection logs
docker-compose logs postgres
```

#### 3. Memory Issues
```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
```

#### 4. Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8000

# Change ports in docker-compose.yml
ports:
  - "8001:8000"
```

### Debug Mode

1. **Enable Debug Logging**
   ```bash
   export AMAS_DEBUG=true
   docker-compose up
   ```

2. **Access Container Shell**
   ```bash
   docker-compose exec amas-api bash
   ```

3. **View Real-time Logs**
   ```bash
   docker-compose logs -f amas-api
   ```

## Maintenance

### Backup Procedures

1. **Database Backup**
   ```bash
   # PostgreSQL
   docker-compose exec postgres pg_dump -U amas amas > backup.sql
   
   # Neo4j
   docker-compose exec neo4j neo4j-admin dump --database=neo4j --to=/tmp/neo4j.dump
   ```

2. **Configuration Backup**
   ```bash
   tar -czf amas-config-backup.tar.gz .env docker/ scripts/
   ```

### Update Procedures

1. **Pull Latest Changes**
   ```bash
   git pull origin main
   ```

2. **Rebuild Images**
   ```bash
   docker-compose build --no-cache
   ```

3. **Update Services**
   ```bash
   docker-compose up -d
   ```

### Health Monitoring

1. **Automated Health Checks**
   ```bash
   # Create health check script
   cat > health-check.sh << 'EOF'
   #!/bin/bash
   curl -f http://localhost:8000/health || exit 1
   EOF
   
   # Add to crontab
   */5 * * * * /path/to/health-check.sh
   ```

2. **Log Rotation**
   ```bash
   # Configure logrotate
   cat > /etc/logrotate.d/amas << 'EOF'
   /var/log/amas/*.log {
       daily
       rotate 30
       compress
       delaycompress
       missingok
       notifempty
   }
   EOF
   ```

## Performance Optimization

### Resource Tuning

1. **Database Optimization**
   ```sql
   -- PostgreSQL tuning
   ALTER SYSTEM SET shared_buffers = '256MB';
   ALTER SYSTEM SET effective_cache_size = '1GB';
   ```

2. **Redis Optimization**
   ```bash
   # Redis configuration
   maxmemory 1gb
   maxmemory-policy allkeys-lru
   ```

3. **Application Optimization**
   ```python
   # Worker processes
   workers = 4
   worker_class = "uvicorn.workers.UvicornWorker"
   ```

### Scaling

1. **Horizontal Scaling**
   ```yaml
   # Scale API service
   docker-compose up -d --scale amas-api=3
   ```

2. **Load Balancer Configuration**
   ```nginx
   upstream amas_api {
       server amas-api-1:8000;
       server amas-api-2:8000;
       server amas-api-3:8000;
   }
   ```

## Support

For deployment issues:
1. Check the troubleshooting section
2. Review service logs
3. Verify configuration
4. Open an issue on GitHub
5. Contact the development team

## Conclusion

This deployment guide provides comprehensive instructions for deploying AMAS in various environments. Follow the procedures carefully and monitor the system health regularly to ensure optimal performance.