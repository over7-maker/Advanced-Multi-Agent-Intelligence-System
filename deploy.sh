#!/bin/bash

# AMAS Production Deployment Script
# One-command deployment for production readiness

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="AMAS"
LOG_FILE="${SCRIPT_DIR}/logs/deployment.log"
ENV_FILE="${SCRIPT_DIR}/.env"

# Create logs directory if it doesn't exist
mkdir -p "${SCRIPT_DIR}/logs"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
}

# Pre-flight checks
preflight_checks() {
    log "Running pre-flight checks..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env file exists
    if [[ ! -f "$ENV_FILE" ]]; then
        log_warning ".env file not found. Creating from .env.example..."
        if [[ -f "${SCRIPT_DIR}/.env.example" ]]; then
            cp "${SCRIPT_DIR}/.env.example" "$ENV_FILE"
            log_success "Created .env file from .env.example"
        else
            log_error ".env.example file not found. Please create .env file manually."
            exit 1
        fi
    fi
    
    # Check available disk space (minimum 5GB)
    available_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $available_space -lt 5 ]]; then
        log_warning "Low disk space: ${available_space}GB available. Recommended: 5GB+"
    fi
    
    # Check available memory (minimum 4GB)
    total_memory=$(free -g | awk 'NR==2{print $2}')
    if [[ $total_memory -lt 4 ]]; then
        log_warning "Low memory: ${total_memory}GB available. Recommended: 4GB+"
    fi
    
    log_success "Pre-flight checks completed"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    directories=(
        "data"
        "logs"
        "config"
        "nginx"
        "nginx/ssl"
        "nginx/logs"
        "monitoring"
        "monitoring/grafana/provisioning"
        "scripts"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "${SCRIPT_DIR}/${dir}"
        log "Created directory: ${dir}"
    done
    
    log_success "Directories created successfully"
}

# Create configuration files
create_config_files() {
    log "Creating configuration files..."
    
    # Create nginx configuration
    cat > "${SCRIPT_DIR}/nginx/nginx.conf" << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream amas_backend {
        server amas:8000;
    }
    
    upstream amas_frontend {
        server amas:3000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        
        # API routes
        location /api/ {
            proxy_pass http://amas_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health check
        location /health {
            proxy_pass http://amas_backend/health;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # Frontend routes
        location / {
            proxy_pass http://amas_frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF
    
    # Create Prometheus configuration
    cat > "${SCRIPT_DIR}/monitoring/prometheus.yml" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'amas'
    static_configs:
      - targets: ['amas:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
EOF
    
    # Create database initialization script
    cat > "${SCRIPT_DIR}/scripts/init-db.sql" << 'EOF'
-- AMAS Database Initialization Script
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_agents_created_at ON agents(created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_agent_id ON tasks(agent_id);
EOF
    
    log_success "Configuration files created successfully"
}

# Deploy the application
deploy_application() {
    log "Deploying AMAS application..."
    
    # Stop existing containers
    log "Stopping existing containers..."
    docker-compose down --remove-orphans || true
    
    # Build and start services
    log "Building and starting services..."
    docker-compose up -d --build
    
    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    check_service_health
    
    log_success "Application deployed successfully"
}

# Check service health
check_service_health() {
    log "Checking service health..."
    
    services=("postgres" "redis" "neo4j" "amas" "nginx")
    
    for service in "${services[@]}"; do
        if docker-compose ps "$service" | grep -q "healthy\|Up"; then
            log_success "$service is healthy"
        else
            log_error "$service is not healthy"
            docker-compose logs "$service" | tail -20
        fi
    done
}

# Display deployment information
display_info() {
    log_success "🎉 AMAS Deployment Complete!"
    echo ""
    echo "📊 Service URLs:"
    echo "  • AMAS API: http://localhost:8000"
    echo "  • AMAS Dashboard: http://localhost:3000"
    echo "  • Neo4j Browser: http://localhost:7474"
    echo "  • Prometheus: http://localhost:9090"
    echo "  • Grafana: http://localhost:3001"
    echo ""
    echo "🔧 Management Commands:"
    echo "  • View logs: docker-compose logs -f"
    echo "  • Stop services: docker-compose down"
    echo "  • Restart services: docker-compose restart"
    echo "  • Update services: docker-compose pull && docker-compose up -d"
    echo ""
    echo "📝 Default Credentials:"
    echo "  • PostgreSQL: postgres/amas_password"
    echo "  • Neo4j: neo4j/amas_password"
    echo "  • Redis: amas_redis_password"
    echo "  • Grafana: admin/amas_grafana_password"
    echo ""
    echo "📋 Health Check:"
    echo "  • API Health: curl http://localhost:8000/health"
    echo "  • Dashboard: http://localhost:3000"
    echo ""
}

# Main deployment function
main() {
    log "🚀 Starting AMAS Production Deployment"
    log "Project: $PROJECT_NAME"
    log "Directory: $SCRIPT_DIR"
    
    preflight_checks
    create_directories
    create_config_files
    deploy_application
    display_info
    
    log_success "Deployment completed successfully!"
}

# Handle script interruption
trap 'log_error "Deployment interrupted by user"; exit 1' INT TERM

# Run main function
main "$@"