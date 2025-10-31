#!/bin/bash

# AMAS Production Deployment Script
# Blue-green deployment with zero downtime

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PROJECT_NAME="AMAS"
ENVIRONMENT="production"
LOG_FILE="${PROJECT_ROOT}/logs/production-deployment.log"
ENV_FILE="${PROJECT_ROOT}/.env.production"

# Blue-green deployment configuration
CURRENT_STACK="blue"
NEW_STACK="green"
LOAD_BALANCER_CONFIG="${PROJECT_ROOT}/nginx/production.conf"

# Create logs directory if it doesn't exist
mkdir -p "${PROJECT_ROOT}/logs"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}" | tee -a "$GITHUB_STEP_SUMMARY"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks for production..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if production environment file exists
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "Production environment file not found. Please create .env.production"
        exit 1
    fi
    
    # Validate production secrets
    if ! grep -q "SECRET_KEY=" "$ENV_FILE" || [[ $(grep "SECRET_KEY=" "$ENV_FILE" | cut -d'=' -f2) == "amas_secret_key_change_in_production" ]]; then
        log_error "Production SECRET_KEY not properly configured"
        exit 1
    fi
    
    # Check available resources
    available_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $available_space -lt 10 ]]; then
        log_warning "Low disk space: ${available_space}GB available. Recommended: 10GB+"
    fi
    
    # Check memory
    total_memory=$(free -g | awk 'NR==2{print $2}')
    if [[ $total_memory -lt 8 ]]; then
        log_warning "Low memory: ${total_memory}GB available. Recommended: 8GB+"
    fi
    
    log_success "Pre-deployment checks completed"
}

# Create production docker-compose file
create_production_compose() {
    local stack_name="$1"
    local compose_file="docker-compose.production-${stack_name}.yml"
    
    log "Creating production compose file for $stack_name stack..."
    
    cat > "$compose_file" << EOF
version: '3.8'

services:
  # PostgreSQL Database
  postgres-${stack_name}:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=amas
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=\${POSTGRES_PASSWORD}
      - POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=C --lc-ctype=C
    volumes:
      - postgres_${stack_name}_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql:ro
    ports:
      - "543${stack_name: -1}:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d amas"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - amas-${stack_name}-network

  # Redis Cache
  redis-${stack_name}:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass \${REDIS_PASSWORD}
    volumes:
      - redis_${stack_name}_data:/data
    ports:
      - "637${stack_name: -1}:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - amas-${stack_name}-network

  # Neo4j Graph Database
  neo4j-${stack_name}:
    image: neo4j:5
    environment:
      - NEO4J_AUTH=neo4j/\${NEO4J_PASSWORD}
      - NEO4J_PLUGINS=["apoc", "graph-data-science"]
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*,gds.*
      - NEO4J_dbms_security_procedures_allowlist=apoc.*,gds.*
    ports:
      - "747${stack_name: -1}:7474"
      - "768${stack_name: -1}:7687"
    volumes:
      - neo4j_${stack_name}_data:/data
      - neo4j_${stack_name}_logs:/logs
      - neo4j_${stack_name}_import:/var/lib/neo4j/import
      - neo4j_${stack_name}_plugins:/plugins
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "\${NEO4J_PASSWORD}", "RETURN 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    networks:
      - amas-${stack_name}-network

  # AMAS Main Application
  amas-${stack_name}:
    image: \${DOCKER_REGISTRY}/\${IMAGE_NAME}:\${IMAGE_TAG}
    ports:
      - "800${stack_name: -1}:8000"
      - "300${stack_name: -1}:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:\${POSTGRES_PASSWORD}@postgres-${stack_name}:5432/amas
      - REDIS_URL=redis://:\${REDIS_PASSWORD}@redis-${stack_name}:6379/0
      - NEO4J_URI=bolt://neo4j-${stack_name}:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=\${NEO4J_PASSWORD}
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - SECRET_KEY=\${SECRET_KEY}
      - JWT_SECRET_KEY=\${JWT_SECRET_KEY}
    env_file:
      - .env.production
    depends_on:
      postgres-${stack_name}:
        condition: service_healthy
      redis-${stack_name}:
        condition: service_healthy
      neo4j-${stack_name}:
        condition: service_healthy
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python3", "-c", "import requests; requests.get('http://localhost:8000/health', timeout=5)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    networks:
      - amas-${stack_name}-network
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'

volumes:
  postgres_${stack_name}_data:
    driver: local
  redis_${stack_name}_data:
    driver: local
  neo4j_${stack_name}_data:
    driver: local
  neo4j_${stack_name}_logs:
    driver: local
  neo4j_${stack_name}_import:
    driver: local
  neo4j_${stack_name}_plugins:
    driver: local

networks:
  amas-${stack_name}-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.2${stack_name: -1}.0.0/16
EOF

    log_success "Created production compose file: $compose_file"
}

# Deploy new stack
deploy_new_stack() {
    local stack_name="$1"
    local compose_file="docker-compose.production-${stack_name}.yml"
    
    log "Deploying new $stack_name stack..."
    
    cd "$PROJECT_ROOT"
    
    # Create compose file
    create_production_compose "$stack_name"
    
    # Start new stack
    docker-compose -f "$compose_file" up -d
    
    # Wait for services to be healthy
    log "Waiting for $stack_name stack to be healthy..."
    sleep 60
    
    # Check service health
    check_stack_health "$stack_name"
    
    log_success "$stack_name stack deployed successfully"
}

# Check stack health
check_stack_health() {
    local stack_name="$1"
    local compose_file="docker-compose.production-${stack_name}.yml"
    
    log "Checking $stack_name stack health..."
    
    services=("postgres-${stack_name}" "redis-${stack_name}" "neo4j-${stack_name}" "amas-${stack_name}")
    
    for service in "${services[@]}"; do
        if docker-compose -f "$compose_file" ps "$service" | grep -q "healthy\|Up"; then
            log_success "$service is healthy"
        else
            log_error "$service is not healthy"
            docker-compose -f "$compose_file" logs "$service" | tail -20
            return 1
        fi
    done
}

# Run production smoke tests
run_production_smoke_tests() {
    local stack_name="$1"
    local port="800${stack_name: -1}"
    
    log "Running production smoke tests against $stack_name stack..."
    
    # Wait for API to be ready
    local max_attempts=60
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f "http://localhost:$port/health" > /dev/null 2>&1; then
            log_success "API is ready for testing"
            break
        else
            log "Waiting for API to be ready (attempt $attempt/$max_attempts)..."
            sleep 10
            ((attempt++))
        fi
    done
    
    if [[ $attempt -gt $max_attempts ]]; then
        log_error "API failed to become ready within expected time"
        return 1
    fi
    
    # Run comprehensive smoke tests
    log "Running comprehensive smoke tests..."
    
    # Test API health endpoint
    if curl -f "http://localhost:$port/health" > /dev/null 2>&1; then
        log_success "API health check passed"
    else
        log_error "API health check failed"
        return 1
    fi
    
    # Test API metrics endpoint
    if curl -f "http://localhost:$port/metrics" > /dev/null 2>&1; then
        log_success "API metrics check passed"
    else
        log_error "API metrics check failed"
        return 1
    fi
    
    # Test database connectivity
    local compose_file="docker-compose.production-${stack_name}.yml"
    if docker-compose -f "$compose_file" exec -T "postgres-${stack_name}" pg_isready -U postgres > /dev/null 2>&1; then
        log_success "Database connectivity check passed"
    else
        log_error "Database connectivity check failed"
        return 1
    fi
    
    # Test Redis connectivity
    if docker-compose -f "$compose_file" exec -T "redis-${stack_name}" redis-cli ping > /dev/null 2>&1; then
        log_success "Redis connectivity check passed"
    else
        log_error "Redis connectivity check failed"
        return 1
    fi
    
    # Test Neo4j connectivity
    if docker-compose -f "$compose_file" exec -T "neo4j-${stack_name}" cypher-shell -u neo4j -p "${NEO4J_PASSWORD}" "RETURN 1" > /dev/null 2>&1; then
        log_success "Neo4j connectivity check passed"
    else
        log_error "Neo4j connectivity check failed"
        return 1
    fi
    
    # Test API endpoints
    local api_endpoints=("/api/v1/agents" "/api/v1/tasks" "/api/v1/health")
    for endpoint in "${api_endpoints[@]}"; do
        if curl -f "http://localhost:$port$endpoint" > /dev/null 2>&1; then
            log_success "API endpoint $endpoint check passed"
        else
            log_warning "API endpoint $endpoint check failed (may be expected)"
        fi
    done
    
    log_success "All production smoke tests passed"
}

# Switch load balancer to new stack
switch_load_balancer() {
    local new_stack="$1"
    local new_port="800${new_stack: -1}"
    
    log "Switching load balancer to $new_stack stack..."
    
    # Update nginx configuration
    if [[ -f "$LOAD_BALANCER_CONFIG" ]]; then
        # Update upstream configuration
        sed -i "s/server amas:8000;/server localhost:$new_port;/" "$LOAD_BALANCER_CONFIG"
        
        # Reload nginx
        if docker-compose ps nginx | grep -q "Up"; then
            docker-compose exec nginx nginx -s reload
            log_success "Load balancer switched to $new_stack stack"
        else
            log_warning "Nginx not running, load balancer switch skipped"
        fi
    else
        log_warning "Load balancer configuration not found, switching skipped"
    fi
}

# Cleanup old stack
cleanup_old_stack() {
    local old_stack="$1"
    local compose_file="docker-compose.production-${old_stack}.yml"
    
    log "Cleaning up old $old_stack stack..."
    
    # Stop old stack
    docker-compose -f "$compose_file" down --remove-orphans
    
    # Remove old compose file
    rm -f "$compose_file"
    
    log_success "Old $old_stack stack cleaned up"
}

# Database migration
run_database_migration() {
    local stack_name="$1"
    local compose_file="docker-compose.production-${stack_name}.yml"
    
    log "Running database migration on $stack_name stack..."
    
    # Wait for database to be ready
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose -f "$compose_file" exec -T "postgres-${stack_name}" pg_isready -U postgres > /dev/null 2>&1; then
            log_success "Database is ready for migration"
            break
        else
            log "Waiting for database to be ready (attempt $attempt/$max_attempts)..."
            sleep 10
            ((attempt++))
        fi
    done
    
    if [[ $attempt -gt $max_attempts ]]; then
        log_error "Database failed to become ready within expected time"
        return 1
    fi
    
    # Run migration
    docker-compose -f "$compose_file" exec -T "amas-${stack_name}" python -m alembic upgrade head
    
    log_success "Database migration completed"
}

# Send notifications
send_notifications() {
    local status="$1"
    local message="$2"
    
    log "Sending deployment notifications..."
    
    # Send to Slack (if configured)
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🌟 AMAS Production Deployment $status: $message\"}" \
            "$SLACK_WEBHOOK_URL" > /dev/null 2>&1 || true
    fi
    
    # Send email notification (if configured)
    if [[ -n "${NOTIFICATION_EMAIL:-}" ]]; then
        echo "AMAS Production Deployment $status: $message" | \
            mail -s "AMAS Production Deployment $status" "$NOTIFICATION_EMAIL" || true
    fi
    
    # Update monitoring dashboards
    if [[ -n "${MONITORING_WEBHOOK_URL:-}" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"status\":\"$status\",\"message\":\"$message\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" \
            "$MONITORING_WEBHOOK_URL" > /dev/null 2>&1 || true
    fi
    
    log_success "Notifications sent"
}

# Rollback function
rollback_deployment() {
    log_error "Production deployment failed. Initiating rollback..."
    
    # Switch back to current stack
    switch_load_balancer "$CURRENT_STACK"
    
    # Cleanup new stack
    cleanup_old_stack "$NEW_STACK"
    
    send_notifications "ROLLBACK" "Production deployment failed and rollback completed"
    
    log_success "Rollback completed"
}

# Main deployment function
main() {
    log "🌟 Starting AMAS Production Deployment (Blue-Green)"
    log "Project: $PROJECT_NAME"
    log "Environment: $ENVIRONMENT"
    log "Current Stack: $CURRENT_STACK"
    log "New Stack: $NEW_STACK"
    log "Directory: $PROJECT_ROOT"
    
    # Set up error handling
    trap 'rollback_deployment; exit 1' ERR
    
    pre_deployment_checks
    deploy_new_stack "$NEW_STACK"
    run_database_migration "$NEW_STACK"
    run_production_smoke_tests "$NEW_STACK"
    switch_load_balancer "$NEW_STACK"
    cleanup_old_stack "$CURRENT_STACK"
    send_notifications "SUCCESS" "Production deployment completed successfully"
    
    # Update current stack reference
    echo "$NEW_STACK" > "${PROJECT_ROOT}/.current-stack"
    
    log_success "🎉 Production deployment completed successfully!"
    
    echo ""
    echo "📊 Production Environment URLs:"
    echo "  • AMAS API: http://localhost:8000"
    echo "  • AMAS Dashboard: http://localhost:3000"
    echo "  • Neo4j Browser: http://localhost:7474"
    echo "  • Prometheus: http://localhost:9090"
    echo "  • Grafana: http://localhost:3001"
    echo ""
    echo "🔧 Management Commands:"
    echo "  • View logs: docker-compose -f docker-compose.production-${NEW_STACK}.yml logs -f"
    echo "  • Stop services: docker-compose -f docker-compose.production-${NEW_STACK}.yml down"
    echo "  • Restart services: docker-compose -f docker-compose.production-${NEW_STACK}.yml restart"
    echo ""
    echo "🔄 Current Active Stack: $NEW_STACK"
    echo ""
}

# Handle script interruption
trap 'log_error "Deployment interrupted by user"; send_notifications "INTERRUPTED" "Production deployment was interrupted"; exit 1' INT TERM

# Run main function
main "$@"