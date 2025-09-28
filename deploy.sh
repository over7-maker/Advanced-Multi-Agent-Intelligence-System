#!/bin/bash

# AMAS Intelligence System - Production Deployment Script
# Advanced Multi-Agent Intelligence System Automated Deployment

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="amas"
ENVIRONMENT="${ENVIRONMENT:-production}"
LOG_FILE="/var/log/amas-deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check NVIDIA Docker (for GPU support)
    if command -v nvidia-smi &> /dev/null; then
        if ! docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi &> /dev/null; then
            warning "NVIDIA Docker runtime not properly configured. GPU acceleration will be disabled."
        else
            log "GPU support detected and configured"
        fi
    else
        warning "NVIDIA GPU not detected. Running in CPU-only mode."
    fi
    
    # Check available disk space (minimum 50GB)
    AVAILABLE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    if [[ $AVAILABLE_SPACE -lt 50 ]]; then
        error "Insufficient disk space. At least 50GB required, found ${AVAILABLE_SPACE}GB"
        exit 1
    fi
    
    # Check available memory (minimum 16GB)
    AVAILABLE_MEMORY=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $AVAILABLE_MEMORY -lt 16 ]]; then
        warning "Low memory detected (${AVAILABLE_MEMORY}GB). Recommended minimum is 16GB."
    fi
    
    log "System requirements check completed"
}

# Generate secure secrets
generate_secrets() {
    log "Generating secure secrets..."
    
    # Create .env file if it doesn't exist
    if [[ ! -f .env ]]; then
        cat > .env << EOF
# AMAS Production Environment Variables
ENVIRONMENT=production
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -base64 32)
NEO4J_PASSWORD=$(openssl rand -base64 32)
GRAFANA_PASSWORD=$(openssl rand -base64 16)

# Optional: Cloud backup configuration
# S3_BACKUP_BUCKET=your-backup-bucket
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key

# AI API Keys (optional)
# DEEPSEEK_API_KEY=your-deepseek-key
# GLM_API_KEY=your-glm-key
# GROK_API_KEY=your-grok-key
# KIMI_API_KEY=your-kimi-key
# QWEN_API_KEY=your-qwen-key
# GPTOSS_API_KEY=your-gptoss-key
EOF
        log "Generated .env file with secure secrets"
    else
        info ".env file already exists, skipping secret generation"
    fi
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    sudo mkdir -p /opt/amas/{data,backups,logs,models,ssl}
    sudo mkdir -p /opt/amas/data/{postgres,redis,neo4j,ollama,vectors}
    sudo mkdir -p /opt/amas/backups/{postgres,neo4j,redis}
    
    # Set appropriate permissions
    sudo chown -R $USER:$USER /opt/amas
    chmod -R 755 /opt/amas
    
    # Create log directory
    sudo mkdir -p /var/log/amas
    sudo chown $USER:$USER /var/log/amas
    
    log "Directories created successfully"
}

# Generate SSL certificates
generate_ssl() {
    log "Generating SSL certificates..."
    
    SSL_DIR="/opt/amas/ssl"
    
    if [[ ! -f "$SSL_DIR/server.crt" ]]; then
        # Generate self-signed certificate for development
        openssl req -x509 -newkey rsa:4096 -keyout "$SSL_DIR/server.key" \
            -out "$SSL_DIR/server.crt" -days 365 -nodes \
            -subj "/C=US/ST=State/L=City/O=AMAS/CN=localhost"
        
        log "SSL certificates generated"
    else
        info "SSL certificates already exist"
    fi
}

# Configure Nginx
configure_nginx() {
    log "Configuring Nginx..."
    
    mkdir -p nginx
    
    cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream amas_api {
        server amas-api-1:8000 weight=1 max_fails=3 fail_timeout=30s;
        server amas-api-2:8000 weight=1 max_fails=3 fail_timeout=30s;
    }

    server {
        listen 80;
        server_name localhost;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name localhost;

        ssl_certificate /etc/nginx/ssl/server.crt;
        ssl_certificate_key /etc/nginx/ssl/server.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # API routes
        location /api/ {
            proxy_pass http://amas_api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_timeout 60s;
        }

        # WebSocket support
        location /ws {
            proxy_pass http://amas_api/ws;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }

        # Web interface
        location / {
            proxy_pass http://amas-web:3000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF
    
    log "Nginx configuration created"
}

# Configure monitoring
configure_monitoring() {
    log "Configuring monitoring..."
    
    mkdir -p monitoring/grafana/{dashboards,datasources}
    
    # Prometheus configuration
    cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'amas-api'
    static_configs:
      - targets: ['amas-api-1:8000', 'amas-api-2:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'neo4j'
    static_configs:
      - targets: ['neo4j:7474']

  - job_name: 'ollama'
    static_configs:
      - targets: ['ollama:11434']
EOF
    
    log "Monitoring configuration created"
}

# Pre-pull Docker images
pull_images() {
    log "Pulling Docker images..."
    
    docker-compose -f docker-compose.production.yml pull
    
    log "Docker images pulled successfully"
}

# Start services
start_services() {
    log "Starting AMAS Intelligence System..."
    
    # Start infrastructure services first
    docker-compose -f docker-compose.production.yml up -d postgres redis neo4j
    
    # Wait for databases to be ready
    log "Waiting for databases to initialize..."
    sleep 30
    
    # Start remaining services
    docker-compose -f docker-compose.production.yml up -d
    
    log "All services started successfully"
}

# Verify deployment
verify_deployment() {
    log "Verifying deployment..."
    
    # Wait for services to be ready
    sleep 60
    
    # Check service health
    local failed_services=()
    
    services=("amas-api-1" "amas-api-2" "amas-web" "postgres" "redis" "neo4j" "ollama")
    
    for service in "${services[@]}"; do
        if ! docker-compose -f docker-compose.production.yml ps "$service" | grep -q "Up"; then
            failed_services+=("$service")
        fi
    done
    
    if [[ ${#failed_services[@]} -eq 0 ]]; then
        log "All services are running successfully"
        
        # Test API endpoint
        if curl -f -s http://localhost/api/health > /dev/null; then
            log "API health check passed"
        else
            warning "API health check failed"
        fi
        
        # Test web interface
        if curl -f -s http://localhost > /dev/null; then
            log "Web interface is accessible"
        else
            warning "Web interface health check failed"
        fi
        
    else
        error "The following services failed to start: ${failed_services[*]}"
        return 1
    fi
}

# Download and setup models
setup_models() {
    log "Setting up AI models..."
    
    # Pull Ollama models
    docker exec amas-ollama ollama pull llama2:13b
    docker exec amas-ollama ollama pull codellama:13b
    docker exec amas-ollama ollama pull mistral:7b
    
    log "AI models setup completed"
}

# Show deployment information
show_deployment_info() {
    log "AMAS Intelligence System deployment completed successfully!"
    echo
    echo "=== DEPLOYMENT INFORMATION ==="
    echo "Web Interface: https://localhost"
    echo "API Endpoint: https://localhost/api"
    echo "Grafana Dashboard: http://localhost:3001"
    echo "Kibana Logs: http://localhost:5601"
    echo
    echo "Default Credentials:"
    echo "- Grafana: admin / $(grep GRAFANA_PASSWORD .env | cut -d'=' -f2)"
    echo
    echo "Service Status:"
    docker-compose -f docker-compose.production.yml ps
    echo
    echo "To view logs: docker-compose -f docker-compose.production.yml logs -f"
    echo "To stop services: docker-compose -f docker-compose.production.yml down"
    echo
    log "Deployment information displayed"
}

# Main deployment function
main() {
    log "Starting AMAS Intelligence System deployment..."
    
    check_root
    check_requirements
    generate_secrets
    create_directories
    generate_ssl
    configure_nginx
    configure_monitoring
    pull_images
    start_services
    verify_deployment
    setup_models
    show_deployment_info
    
    log "AMAS Intelligence System deployment completed successfully!"
}

# Handle script interruption
cleanup() {
    error "Deployment interrupted. Cleaning up..."
    docker-compose -f docker-compose.production.yml down
    exit 1
}

trap cleanup INT TERM

# Run main function
main "$@"