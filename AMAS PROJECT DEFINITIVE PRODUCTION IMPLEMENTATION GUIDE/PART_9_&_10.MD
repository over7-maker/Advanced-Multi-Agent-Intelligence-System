# **🎯 AMAS PROJECT: PART 9 & 10 - DEPLOYMENT & PRODUCTION CHECKLIST**
## **Production Docker Compose & Complete Deployment Guide**

***

## **PART 9: PRODUCTION DEPLOYMENT CONFIGURATION**

### **Step 9.1: Production Docker Compose (Complete Stack)**

**File**: `docker-compose.prod.yml` (PRODUCTION-READY - COMPLETE VERSION)

```yaml
# docker-compose.prod.yml (COMPLETE PRODUCTION STACK)
version: '3.8'

services:
  # ============================================================================
  # AMAS BACKEND API
  # ============================================================================
  amas-backend:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        - BUILD_DATE=${BUILD_DATE}
        - VERSION=${VERSION:-1.0.0}
    image: amas-backend:${VERSION:-latest}
    container_name: amas-backend
    restart: unless-stopped
    ports:
      - "${API_PORT:-8000}:8000"
    environment:
      # Application
      - ENVIRONMENT=production
      - APP_VERSION=${VERSION:-1.0.0}
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - JSON_LOGS=true
      
      # Database
      - DATABASE_URL=postgresql://amas:${DB_PASSWORD}@postgres:5432/amas
      - DATABASE_POOL_SIZE=20
      - DATABASE_MAX_OVERFLOW=10
      
      # Redis
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      
      # Neo4j
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      
      # AI Providers (16 providers)
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - COHERE_API_KEY=${COHERE_API_KEY}
      - MISTRAL_API_KEY=${MISTRAL_API_KEY}
      - TOGETHER_API_KEY=${TOGETHER_API_KEY}
      - PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY}
      - FIREWORKS_API_KEY=${FIREWORKS_API_KEY}
      - REPLICATE_API_KEY=${REPLICATE_API_KEY}
      - HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY}
      - AI21_API_KEY=${AI21_API_KEY}
      - ALEPHALPHA_API_KEY=${ALEPHALPHA_API_KEY}
      - WRITER_API_KEY=${WRITER_API_KEY}
      - MOONSHOT_API_KEY=${MOONSHOT_API_KEY}
      
      # Integrations
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
      - SLACK_SIGNING_SECRET=${SLACK_SIGNING_SECRET}
      - N8N_BASE_URL=${N8N_BASE_URL}
      - N8N_API_KEY=${N8N_API_KEY}
      
      # Monitoring
      - JAEGER_ENDPOINT=jaeger:6831
      - OTLP_ENDPOINT=tempo:4317
      
      # CORS
      - CORS_ORIGINS=${CORS_ORIGINS:-https://your-domain.com}
      
    volumes:
      - amas-logs:/app/logs
      - amas-data:/app/data
    networks:
      - amas-backend
      - amas-monitoring
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  # ============================================================================
  # POSTGRESQL DATABASE
  # ============================================================================
  postgres:
    image: postgres:15-alpine
    container_name: amas-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=amas
      - POSTGRES_USER=amas
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - PGDATA=/var/lib/postgresql/data/pgdata
      - POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=en_US.UTF-8 --lc-ctype=en_US.UTF-8
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
      - ./backups:/backups
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    networks:
      - amas-backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U amas -d amas"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  # ============================================================================
  # REDIS CACHE
  # ============================================================================
  redis:
    image: redis:7-alpine
    container_name: amas-redis
    restart: unless-stopped
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD}
      --appendonly yes
      --appendfsync everysec
      --maxmemory 2gb
      --maxmemory-policy allkeys-lru
    volumes:
      - redis-data:/data
    ports:
      - "${REDIS_PORT:-6379}:6379"
    networks:
      - amas-backend
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G

  # ============================================================================
  # NEO4J GRAPH DATABASE
  # ============================================================================
  neo4j:
    image: neo4j:5-community
    container_name: amas-neo4j
    restart: unless-stopped
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
      - NEO4J_dbms_memory_heap_max__size=2G
      - NEO4J_dbms_memory_pagecache_size=1G
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*
      - NEO4J_dbms_security_procedures_allowlist=apoc.*
    volumes:
      - neo4j-data:/data
      - neo4j-logs:/logs
      - neo4j-plugins:/plugins
    ports:
      - "${NEO4J_HTTP_PORT:-7474}:7474"
      - "${NEO4J_BOLT_PORT:-7687}:7687"
    networks:
      - amas-backend
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  # ============================================================================
  # NGINX REVERSE PROXY
  # ============================================================================
  nginx:
    image: nginx:alpine
    container_name: amas-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./frontend/build:/usr/share/nginx/html:ro
      - nginx-logs:/var/log/nginx
    networks:
      - amas-backend
      - amas-monitoring
    depends_on:
      - amas-backend
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M

  # ============================================================================
  # MONITORING STACK
  # ============================================================================
  
  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: amas-prometheus
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./monitoring/prometheus/rules:/etc/prometheus/rules:ro
      - prometheus-data:/prometheus
    ports:
      - "${PROMETHEUS_PORT:-9090}:9090"
    networks:
      - amas-monitoring
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G

  # Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: amas-grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_USER:-admin}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_ROOT_URL=${GRAFANA_ROOT_URL:-http://localhost:3001}
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
      - grafana-data:/var/lib/grafana
    ports:
      - "${GRAFANA_PORT:-3001}:3000"
    networks:
      - amas-monitoring
    depends_on:
      - prometheus
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M

  # Jaeger (Distributed Tracing)
  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: amas-jaeger
    restart: unless-stopped
    environment:
      - COLLECTOR_OTLP_ENABLED=true
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
    ports:
      - "5775:5775/udp"
      - "6831:6831/udp"
      - "6832:6832/udp"
      - "5778:5778"
      - "${JAEGER_UI_PORT:-16686}:16686"
      - "14250:14250"
      - "14268:14268"
      - "14269:14269"
      - "4317:4317"
      - "4318:4318"
      - "9411:9411"
    networks:
      - amas-monitoring
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  # Alertmanager
  alertmanager:
    image: prom/alertmanager:latest
    container_name: amas-alertmanager
    restart: unless-stopped
    command:
      - '--config.file=/etc/alertmanager/config.yml'
      - '--storage.path=/alertmanager'
    volumes:
      - ./monitoring/alertmanager/config.yml:/etc/alertmanager/config.yml:ro
      - alertmanager-data:/alertmanager
    ports:
      - "${ALERTMANAGER_PORT:-9093}:9093"
    networks:
      - amas-monitoring
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M

  # Node Exporter (System Metrics)
  node-exporter:
    image: prom/node-exporter:latest
    container_name: amas-node-exporter
    restart: unless-stopped
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    ports:
      - "9100:9100"
    networks:
      - amas-monitoring
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 128M
        reservations:
          cpus: '0.1'
          memory: 64M

  # cAdvisor (Container Metrics)
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: amas-cadvisor
    restart: unless-stopped
    privileged: true
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    ports:
      - "8080:8080"
    networks:
      - amas-monitoring
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M

  # PostgreSQL Exporter
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: amas-postgres-exporter
    restart: unless-stopped
    environment:
      - DATA_SOURCE_NAME=postgresql://amas:${DB_PASSWORD}@postgres:5432/amas?sslmode=disable
    ports:
      - "9187:9187"
    networks:
      - amas-backend
      - amas-monitoring
    depends_on:
      - postgres
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 128M
        reservations:
          cpus: '0.1'
          memory: 64M

  # Redis Exporter
  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: amas-redis-exporter
    restart: unless-stopped
    environment:
      - REDIS_ADDR=redis:6379
      - REDIS_PASSWORD=${REDIS_PASSWORD}
    ports:
      - "9121:9121"
    networks:
      - amas-backend
      - amas-monitoring
    depends_on:
      - redis
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 128M
        reservations:
          cpus: '0.1'
          memory: 64M

  # Loki (Log Aggregation)
  loki:
    image: grafana/loki:latest
    container_name: amas-loki
    restart: unless-stopped
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - ./monitoring/loki/config.yml:/etc/loki/local-config.yaml:ro
      - loki-data:/loki
    ports:
      - "3100:3100"
    networks:
      - amas-monitoring
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  # Promtail (Log Shipper)
  promtail:
    image: grafana/promtail:latest
    container_name: amas-promtail
    restart: unless-stopped
    command: -config.file=/etc/promtail/config.yml
    volumes:
      - ./monitoring/promtail/config.yml:/etc/promtail/config.yml:ro
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - amas-logs:/app/logs:ro
    networks:
      - amas-monitoring
    depends_on:
      - loki
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M

# ============================================================================
# VOLUMES
# ============================================================================
volumes:
  postgres-data:
    driver: local
  redis-data:
    driver: local
  neo4j-data:
    driver: local
  neo4j-logs:
    driver: local
  neo4j-plugins:
    driver: local
  prometheus-data:
    driver: local
  grafana-data:
    driver: local
  alertmanager-data:
    driver: local
  loki-data:
    driver: local
  amas-logs:
    driver: local
  amas-data:
    driver: local
  nginx-logs:
    driver: local

# ============================================================================
# NETWORKS
# ============================================================================
networks:
  amas-backend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
  amas-monitoring:
    driver: bridge
    ipam:
      config:
        - subnet: 172.21.0.0/16
```

***

### **Step 9.2: Environment Configuration**

**File**: `.env.production` (CREATE NEW)

```bash
# .env.production (PRODUCTION ENVIRONMENT VARIABLES)

# ============================================================================
# APPLICATION
# ============================================================================
VERSION=1.0.0
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
ENVIRONMENT=production

# Ports
API_PORT=8000
POSTGRES_PORT=5432
REDIS_PORT=6379
NEO4J_HTTP_PORT=7474
NEO4J_BOLT_PORT=7687
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
JAEGER_UI_PORT=16686
ALERTMANAGER_PORT=9093

# Security
SECRET_KEY=CHANGE_THIS_TO_SECURE_RANDOM_STRING_MIN_32_CHARS
JWT_SECRET=CHANGE_THIS_TO_SECURE_RANDOM_STRING_MIN_32_CHARS
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Logging
LOG_LEVEL=INFO

# ============================================================================
# DATABASE PASSWORDS
# ============================================================================
DB_PASSWORD=CHANGE_THIS_SECURE_POSTGRES_PASSWORD
REDIS_PASSWORD=CHANGE_THIS_SECURE_REDIS_PASSWORD
NEO4J_PASSWORD=CHANGE_THIS_SECURE_NEO4J_PASSWORD

# ============================================================================
# AI PROVIDERS (Add your API keys)
# ============================================================================
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
GROQ_API_KEY=gsk_...
DEEPSEEK_API_KEY=...
COHERE_API_KEY=...
MISTRAL_API_KEY=...
TOGETHER_API_KEY=...
PERPLEXITY_API_KEY=...
FIREWORKS_API_KEY=...
REPLICATE_API_KEY=...
HUGGINGFACE_API_KEY=...
AI21_API_KEY=...
ALEPHALPHA_API_KEY=...
WRITER_API_KEY=...
MOONSHOT_API_KEY=...

# ============================================================================
# INTEGRATIONS
# ============================================================================
GITHUB_TOKEN=ghp_...
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...
N8N_BASE_URL=https://n8n.your-domain.com
N8N_API_KEY=...

# ============================================================================
# MONITORING
# ============================================================================
GRAFANA_USER=admin
GRAFANA_PASSWORD=CHANGE_THIS_SECURE_GRAFANA_PASSWORD
GRAFANA_ROOT_URL=https://monitoring.your-domain.com
```

***

### **Step 9.3: Deployment Scripts**

**File**: `scripts/deploy-production.sh` (CREATE NEW)

```bash
#!/bin/bash
# scripts/deploy-production.sh (PRODUCTION DEPLOYMENT SCRIPT)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="amas"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"

# ============================================================================
# FUNCTIONS
# ============================================================================

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# ============================================================================
# PRE-DEPLOYMENT CHECKS
# ============================================================================

pre_flight_checks() {
    log "Running pre-flight checks..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    
    # Check if .env.production exists
    if [ ! -f "$ENV_FILE" ]; then
        error "$ENV_FILE not found. Please create it from .env.production.example"
    fi
    
    # Check if required environment variables are set
    source "$ENV_FILE"
    
    required_vars=(
        "SECRET_KEY"
        "JWT_SECRET"
        "DB_PASSWORD"
        "REDIS_PASSWORD"
        "NEO4J_PASSWORD"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ] || [[ "${!var}" == *"CHANGE_THIS"* ]]; then
            error "Required environment variable $var is not set or using default value"
        fi
    done
    
    log "✅ Pre-flight checks passed"
}

# ============================================================================
# BACKUP
# ============================================================================

backup_database() {
    log "Creating database backup before deployment..."
    
    if docker ps | grep -q "amas-postgres"; then
        ./scripts/backup.sh || warn "Backup failed, continuing anyway..."
    else
        warn "Database not running, skipping backup"
    fi
}

# ============================================================================
# BUILD
# ============================================================================

build_images() {
    log "Building Docker images..."
    
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build --no-cache
    
    log "✅ Images built successfully"
}

# ============================================================================
# DEPLOY
# ============================================================================

deploy() {
    log "Deploying $PROJECT_NAME to production..."
    
    # Pull latest images (if using registry)
    info "Pulling latest images..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull || true
    
    # Stop old containers
    info "Stopping old containers..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
    
    # Start new containers
    info "Starting new containers..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    
    # Wait for services to be healthy
    info "Waiting for services to be healthy..."
    sleep 10
    
    # Check health
    check_health
    
    log "✅ Deployment completed successfully"
}

# ============================================================================
# HEALTH CHECK
# ============================================================================

check_health() {
    log "Checking service health..."
    
    # Check if containers are running
    services=(
        "amas-backend"
        "amas-postgres"
        "amas-redis"
        "amas-nginx"
        "amas-prometheus"
        "amas-grafana"
    )
    
    for service in "${services[@]}"; do
        if docker ps | grep -q "$service"; then
            echo -e "${GREEN}✓${NC} $service is running"
        else
            error "$service is not running"
        fi
    done
    
    # Check API health endpoint
    sleep 5
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} API health check passed"
    else
        error "API health check failed"
    fi
    
    log "✅ All health checks passed"
}

# ============================================================================
# DATABASE MIGRATION
# ============================================================================

run_migrations() {
    log "Running database migrations..."
    
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T amas-backend \
        alembic upgrade head
    
    log "✅ Database migrations completed"
}

# ============================================================================
# POST-DEPLOYMENT
# ============================================================================

post_deployment() {
    log "Running post-deployment tasks..."
    
    # Show logs
    info "Displaying recent logs..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs --tail=50
    
    # Show status
    info "Service status:"
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
    
    log "✅ Post-deployment tasks completed"
}

# ============================================================================
# ROLLBACK
# ============================================================================

rollback() {
    warn "Rolling back deployment..."
    
    # Stop current containers
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
    
    # Restore from backup
    ./scripts/restore.sh "$1"
    
    # Start previous version
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    
    log "✅ Rollback completed"
}

# ============================================================================
# MAIN DEPLOYMENT FLOW
# ============================================================================

main() {
    echo "╔══════════════════════════════════════════╗"
    echo "║   AMAS Production Deployment Script     ║"
    echo "╚══════════════════════════════════════════╝"
    echo ""
    
    # Pre-flight checks
    pre_flight_checks
    
    # Backup
    backup_database
    
    # Build
    if [ "$1" == "--build" ]; then
        build_images
    fi
    
    # Deploy
    deploy
    
    # Migrations
    run_migrations
    
    # Post-deployment
    post_deployment
    
    echo ""
    echo "╔══════════════════════════════════════════╗"
    echo "║     Deployment Completed Successfully!   ║"
    echo "╚══════════════════════════════════════════╝"
    echo ""
    echo "🌐 Application: http://localhost:8000"
    echo "📊 Grafana: http://localhost:3001"
    echo "🔍 Jaeger: http://localhost:16686"
    echo "📈 Prometheus: http://localhost:9090"
    echo ""
}

# ============================================================================
# SCRIPT EXECUTION
# ============================================================================

case "$1" in
    --build)
        main --build
        ;;
    --rollback)
        rollback "$2"
        ;;
    --health)
        check_health
        ;;
    *)
        main
        ;;
esac
```

**Make executable**:
```bash
chmod +x scripts/deploy-production.sh
```

***

## **PART 10: FINAL PRODUCTION CHECKLIST**

### **Step 10.1: Complete Production Deployment Checklist**

**File**: `docs/PRODUCTION_CHECKLIST.md` (CREATE NEW)

```markdown
# AMAS Production Deployment Checklist

## Pre-Deployment (1-2 weeks before)

### 1. Infrastructure Preparation

#### 1.1 Server Setup
- [ ] Provision production servers (minimum specs: 8 vCPU, 32GB RAM, 500GB SSD)
- [ ] Install Docker (version 24.0+)
- [ ] Install Docker Compose (version 2.20+)
- [ ] Configure firewall rules
  - [ ] Allow port 80 (HTTP)
  - [ ] Allow port 443 (HTTPS)
  - [ ] Allow port 22 (SSH - restricted IPs only)
  - [ ] Block all other ports from external access
- [ ] Set up SSH key-based authentication
- [ ] Disable password authentication
- [ ] Configure automatic security updates

#### 1.2 Domain & DNS
- [ ] Register domain name
- [ ] Configure DNS records
  - [ ] A record for main domain → server IP
  - [ ] A record for www → server IP
  - [ ] A record for api → server IP
  - [ ] A record for monitoring → server IP
- [ ] SSL certificate obtained (Let's Encrypt or commercial)
- [ ] Configure SSL auto-renewal

#### 1.3 Monitoring & Alerting
- [ ] Set up monitoring dashboards
- [ ] Configure alert rules
- [ ] Set up Slack/email notifications
- [ ] Configure on-call schedule
- [ ] Test alert delivery

### 2. Security Configuration

#### 2.1 Secrets Management
- [ ] Generate strong SECRET_KEY (32+ chars)
- [ ] Generate strong JWT_SECRET (32+ chars)
- [ ] Generate strong database passwords
- [ ] Generate strong Redis password
- [ ] Generate strong Neo4j password
- [ ] Store all secrets in secure vault (AWS Secrets Manager / HashiCorp Vault)
- [ ] Never commit secrets to Git

#### 2.2 AI Provider API Keys
- [ ] OpenAI API key configured
- [ ] Anthropic API key configured
- [ ] Google AI API key configured
- [ ] Groq API key configured
- [ ] DeepSeek API key configured
- [ ] Cohere API key configured
- [ ] Mistral API key configured
- [ ] Together API key configured
- [ ] Perplexity API key configured
- [ ] Fireworks API key configured
- [ ] Replicate API key configured
- [ ] HuggingFace API key configured
- [ ] AI21 API key configured
- [ ] Aleph Alpha API key configured
- [ ] Writer API key configured
- [ ] Moonshot API key configured
- [ ] Set spending limits on all providers
- [ ] Configure rate limiting

#### 2.3 Integration Credentials
- [ ] GitHub token generated (if using GitHub integration)
- [ ] Slack bot token generated (if using Slack integration)
- [ ] Slack signing secret configured
- [ ] N8N base URL and API key configured
- [ ] Other integration credentials as needed

#### 2.4 Security Hardening
- [ ] Enable HTTPS only (redirect HTTP to HTTPS)
- [ ] Configure HSTS headers
- [ ] Set up Content Security Policy (CSP)
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up fail2ban or similar
- [ ] Configure regular security scans

### 3. Database Setup

#### 3.1 PostgreSQL
- [ ] Database created (name: amas)
- [ ] User created with strong password
- [ ] Connection pooling configured
- [ ] Backup strategy implemented
  - [ ] Daily automated backups
  - [ ] Weekly full backups
  - [ ] Off-site backup storage (S3/GCS)
  - [ ] Backup retention policy (30 days)
  - [ ] Backup restoration tested
- [ ] Database indexes optimized
- [ ] Query performance tuned

#### 3.2 Redis
- [ ] Redis password set
- [ ] Persistence enabled (AOF + RDB)
- [ ] Memory limit configured (maxmemory)
- [ ] Eviction policy set (allkeys-lru)
- [ ] Backup configured

#### 3.3 Neo4j (Optional)
- [ ] Neo4j password set
- [ ] Memory configured (heap + page cache)
- [ ] Indexes created
- [ ] Backup configured

### 4. Application Configuration

#### 4.1 Environment Variables
- [ ] Copy `.env.production.example` to `.env.production`
- [ ] Update all `CHANGE_THIS` placeholders
- [ ] Verify all required variables are set
- [ ] Test environment file loading

#### 4.2 CORS Configuration
- [ ] Update CORS_ORIGINS with production domain(s)
- [ ] Remove development origins
- [ ] Test CORS from production domain

#### 4.3 Logging
- [ ] Log level set to INFO or WARNING
- [ ] JSON logging enabled
- [ ] Log rotation configured
- [ ] Log aggregation set up (Loki)
- [ ] Log retention policy defined

### 5. Code Preparation

#### 5.1 Testing
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] End-to-end tests passing
- [ ] Code coverage > 80%
- [ ] Performance tests passing
- [ ] Load tests passing

#### 5.2 Code Quality
- [ ] Code reviewed by team
- [ ] No critical security vulnerabilities (run safety check)
- [ ] No high-priority bugs
- [ ] Dependencies up to date
- [ ] Dependency vulnerabilities resolved

#### 5.3 Documentation
- [ ] README.md updated
- [ ] API documentation complete
- [ ] Deployment documentation reviewed
- [ ] Runbook created for common issues
- [ ] Architecture diagrams updated

## Deployment Day

### 6. Pre-Deployment Steps

#### 6.1 Communication
- [ ] Notify team of deployment window
- [ ] Notify users of potential downtime (if applicable)
- [ ] Have rollback plan ready
- [ ] Have team on standby

#### 6.2 Final Checks
- [ ] Run pre-flight checks script
- [ ] Verify server resources available
- [ ] Verify SSL certificates valid
- [ ] Verify DNS propagation complete
- [ ] Test database connectivity
- [ ] Test Redis connectivity

### 7. Deployment Execution

#### 7.1 Backup
```
# Create backup before deployment
./scripts/backup.sh
```
- [ ] Database backup completed
- [ ] Backup verified

#### 7.2 Build & Deploy
```
# Deploy to production
./scripts/deploy-production.sh --build
```
- [ ] Docker images built successfully
- [ ] Containers started successfully
- [ ] Health checks passing

#### 7.3 Database Migration
```
# Run migrations
docker-compose -f docker-compose.prod.yml exec amas-backend alembic upgrade head
```
- [ ] Migrations completed successfully
- [ ] Database schema verified

#### 7.4 Verification
- [ ] API responding (http://your-domain.com/health)
- [ ] Frontend loading correctly
- [ ] User authentication working
- [ ] Task creation working
- [ ] Task execution working
- [ ] Integrations working
- [ ] Monitoring dashboards showing data

### 8. Post-Deployment

#### 8.1 Monitoring
- [ ] Check Grafana dashboards
- [ ] Verify metrics collection
- [ ] Check for errors in logs
- [ ] Monitor resource usage (CPU, memory, disk)
- [ ] Monitor response times
- [ ] Monitor error rates

#### 8.2 Smoke Tests
- [ ] Create test user account
- [ ] Create test task
- [ ] Execute test task
- [ ] Verify results
- [ ] Test integration triggers
- [ ] Test API endpoints
- [ ] Test WebSocket connection

#### 8.3 Performance
- [ ] Check API response times (< 200ms p95)
- [ ] Check database query times (< 50ms p95)
- [ ] Check cache hit rate (> 80%)
- [ ] Monitor system load
- [ ] Check for memory leaks

#### 8.4 Documentation
- [ ] Update deployment log
- [ ] Document any issues encountered
- [ ] Document any configuration changes
- [ ] Update version in Git (tag release)

## Day 1-7 Post-Deployment

### 9. Continuous Monitoring

#### 9.1 Daily Checks
- [ ] Review error logs
- [ ] Check system metrics
- [ ] Verify backups completed
- [ ] Monitor cost/usage of AI providers
- [ ] Check for security alerts

#### 9.2 Weekly Review
- [ ] Performance trends analysis
- [ ] Cost analysis
- [ ] User feedback review
- [ ] Plan optimizations

## Emergency Procedures

### 10. Rollback Plan

If deployment fails:

```
# Rollback to previous version
./scripts/deploy-production.sh --rollback <backup-file>
```

Steps:
1. Stop current containers
2. Restore database from backup
3. Deploy previous version
4. Verify rollback successful
5. Notify team
6. Investigate issue

### 11. Common Issues & Solutions

#### Issue: Database connection fails
```
# Check database is running
docker ps | grep postgres

# Check database logs
docker logs amas-postgres

# Verify credentials
docker exec -it amas-postgres psql -U amas -d amas
```

#### Issue: Redis connection fails
```
# Check Redis is running
docker ps | grep redis

# Test connection
docker exec -it amas-redis redis-cli ping
```

#### Issue: High memory usage
```
# Check container memory
docker stats

# Restart containers if needed
docker-compose -f docker-compose.prod.yml restart amas-backend
```

#### Issue: High CPU usage
- Check for infinite loops in logs
- Review recent deployments
- Scale horizontally if needed

## Success Criteria

Deployment is considered successful when:

- [ ] All services are running
- [ ] All health checks passing
- [ ] API response time < 200ms (p95)
- [ ] Error rate < 0.1%
- [ ] No critical alerts
- [ ] Monitoring dashboards showing data
- [ ] Users can successfully use the application
- [ ] No data loss occurred

## Post-Launch Optimization (Week 2+)

### 12. Performance Tuning
- [ ] Analyze slow queries
- [ ] Optimize database indexes
- [ ] Tune cache TTLs
- [ ] Review and optimize AI provider usage
- [ ] Set up CDN for static assets

### 13. Cost Optimization
- [ ] Review AI provider costs
- [ ] Optimize unnecessary API calls
- [ ] Review infrastructure costs
- [ ] Implement cost alerts

### 14. Security Audit
- [ ] Penetration testing
- [ ] Security scan results review
- [ ] Access logs review
- [ ] Update security policies

## Maintenance Schedule

### Daily
- Automated backups
- Log review
- Metrics review

### Weekly
- Security updates check
- Performance review
- Cost review

### Monthly
- Full security audit
- Disaster recovery test
- Capacity planning review

### Quarterly
- Major dependency updates
- Architecture review
- Security penetration test

---

## Emergency Contacts

**On-Call Engineer**: [Your contact]
**DevOps Lead**: [Your contact]
**Security Lead**: [Your contact]
**Product Owner**: [Your contact]

## Important URLs

- **Production**: https://your-domain.com
- **API**: https://api.your-domain.com
- **Monitoring**: https://monitoring.your-domain.com
- **Grafana**: https://monitoring.your-domain.com
- **Jaeger**: https://tracing.your-domain.com

---

Last Updated: $(date)
Version: 1.0.0
```

***

### **Step 10.2: Quick Start Guide**

**File**: `docs/QUICK_START.md` (CREATE NEW)

```markdown
# AMAS Quick Start Guide

## Prerequisites

- Docker 24.0+
- Docker Compose 2.20+
- 8GB+ RAM available
- 20GB+ disk space

## Local Development (5 minutes)

### 1. Clone Repository
```
git clone https://github.com/your-org/amas.git
cd amas
```

### 2. Environment Setup
```
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

### 3. Start Development Stack
```
# Start all services
docker-compose up -d

# Watch logs
docker-compose logs -f amas-backend
```

### 4. Run Migrations
```
# Apply database migrations
docker-compose exec amas-backend alembic upgrade head
```

### 5. Create Admin User
```
# Create admin user
docker-compose exec amas-backend python scripts/create_admin.py
```

### 6. Access Application
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001 (admin/admin)

## Production Deployment (30 minutes)

### 1. Server Preparation
```
# SSH to production server
ssh user@your-server

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Deploy Application
```
# Clone repository
git clone https://github.com/your-org/amas.git
cd amas

# Copy production environment
cp .env.production.example .env.production

# ⚠️ IMPORTANT: Edit and configure all secrets
nano .env.production

# Deploy
./scripts/deploy-production.sh --build
```

### 3. Verify Deployment
```
# Check all services are running
docker ps

# Check health
curl http://localhost:8000/health

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Common Commands

### Development
```
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Run tests
docker-compose exec amas-backend pytest

# Access database
docker-compose exec postgres psql -U amas -d amas

# Access Redis CLI
docker-compose exec redis redis-cli
```

### Production
```
# Deploy/Update
./scripts/deploy-production.sh --build

# Backup database
./scripts/backup.sh

# Restore database
./scripts/restore.sh <backup-file>

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart service
docker-compose -f docker-compose.prod.yml restart amas-backend
```

## Troubleshooting

### Service won't start
```
# Check logs
docker logs ontainerer-name>

# Check resources
docker stats

# Restart service
docker restart <container-name>
```

### Database connection error
```
# Check database is running
docker ps | grep postgres

# Check connection
docker exec -it amas-postgres psql -U amas -d amas

# Check password in .env matches
```

### High memory usage
```
# Check memory usage
docker stats

# Restart containers
docker-compose restart
```

## Next Steps

1. Read full documentation: `docs/`
2. Review architecture: `docs/ARCHITECTURE.md`
3. Check production checklist: `docs/PRODUCTION_CHECKLIST.md`
4. Join community: [Discord/Slack link]

## Support

- Documentation: https://docs.your-domain.com
- GitHub Issues: https://github.com/your-org/amas/issues
- Email: support@your-domain.com
```

***

**This completes Part 9 & 10 - Production Deployment & Checklist!** 🎉

**What's Fully Implemented**:

### **Part 9 - Production Deployment**:
1. ✅ Complete production docker-compose.yml (15 services)
2. ✅ Production environment configuration
3. ✅ Automated deployment script
4. ✅ Health checks & monitoring
5. ✅ Resource limits & reservations
6. ✅ Complete monitoring stack integration

### **Part 10 - Production Checklist**:
1. ✅ Comprehensive pre-deployment checklist (50+ items)
2. ✅ Deployment day procedures
3. ✅ Post-deployment verification
4. ✅ Emergency procedures & rollback plan
5. ✅ Maintenance schedule
6. ✅ Quick start guide

**Complete AMAS Stack Now Includes**:
- ✅ Backend API (FastAPI + async)
- ✅ 3 Databases (PostgreSQL, Redis, Neo4j)
- ✅ 16 AI Providers
- ✅ 6 Integrations (GitHub, Slack, Notion, Jira, N8N, Salesforce)
- ✅ ML Prediction System
- ✅ Complete Monitoring (Prometheus, Grafana, Jaeger, Loki)
- ✅ Frontend (React + Material-UI)
- ✅ Production deployment ready
- ✅ Complete documentation

**Ready to deploy to production!** 🚀
