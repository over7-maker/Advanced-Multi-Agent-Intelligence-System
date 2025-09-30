#!/bin/bash

# AMAS Deployment Script
# This script deploys the complete AMAS system using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    log_success "All requirements met"
}

create_env_file() {
    log_info "Creating environment file..."
    
    if [ ! -f "$ENV_FILE" ]; then
        cat > "$ENV_FILE" << EOF
# AMAS Environment Configuration
AMAS_ENVIRONMENT=$ENVIRONMENT

# Database Configuration
POSTGRES_DB=amas
POSTGRES_USER=amas
POSTGRES_PASSWORD=amas_secure_password_123

# Redis Configuration
REDIS_PASSWORD=amas_redis_password_123

# Neo4j Configuration
NEO4J_AUTH=neo4j/amas_neo4j_password_123

# Security Configuration
JWT_SECRET=your_super_secret_jwt_key_change_this_in_production
ENCRYPTION_KEY=your_32_byte_encryption_key_change_this_in_production

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Monitoring Configuration
PROMETHEUS_RETENTION=30d
GRAFANA_ADMIN_PASSWORD=amas_admin_password
EOF
        log_success "Environment file created: $ENV_FILE"
    else
        log_info "Environment file already exists: $ENV_FILE"
    fi
}

build_images() {
    log_info "Building Docker images..."
    
    # Build main API image
    log_info "Building AMAS API image..."
    docker-compose build amas-api
    
    # Build vector service image
    log_info "Building Vector Service image..."
    docker-compose build vector-service
    
    log_success "All images built successfully"
}

start_services() {
    log_info "Starting AMAS services..."
    
    # Start infrastructure services first
    log_info "Starting infrastructure services..."
    docker-compose up -d postgres redis neo4j
    
    # Wait for infrastructure to be ready
    log_info "Waiting for infrastructure services to be ready..."
    sleep 30
    
    # Start application services
    log_info "Starting application services..."
    docker-compose up -d ollama vector-service amas-api
    
    # Wait for application services
    log_info "Waiting for application services to be ready..."
    sleep 30
    
    # Start monitoring and load balancer
    log_info "Starting monitoring and load balancer..."
    docker-compose up -d prometheus grafana nginx
    
    log_success "All services started successfully"
}

check_health() {
    log_info "Checking service health..."
    
    # Check API health
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "API service is healthy"
    else
        log_warning "API service health check failed"
    fi
    
    # Check Neo4j
    if curl -f http://localhost:7474 &> /dev/null; then
        log_success "Neo4j is accessible"
    else
        log_warning "Neo4j health check failed"
    fi
    
    # Check Grafana
    if curl -f http://localhost:3001 &> /dev/null; then
        log_success "Grafana is accessible"
    else
        log_warning "Grafana health check failed"
    fi
}

show_status() {
    log_info "AMAS System Status:"
    echo ""
    echo "🌐 Web Interface: http://localhost"
    echo "🔧 API Endpoints: http://localhost/api"
    echo "📊 Grafana Dashboard: http://localhost:3001"
    echo "🔍 Neo4j Browser: http://localhost:7474"
    echo "📈 Prometheus: http://localhost:9090"
    echo ""
    echo "📋 Service Status:"
    docker-compose ps
}

cleanup() {
    log_info "Cleaning up..."
    docker-compose down
    log_success "Cleanup completed"
}

show_help() {
    echo "AMAS Deployment Script"
    echo ""
    echo "Usage: $0 [ENVIRONMENT] [COMMAND]"
    echo ""
    echo "Environments:"
    echo "  development  - Development environment (default)"
    echo "  production   - Production environment"
    echo ""
    echo "Commands:"
    echo "  deploy       - Deploy the system (default)"
    echo "  start        - Start existing services"
    echo "  stop         - Stop services"
    echo "  restart      - Restart services"
    echo "  status       - Show service status"
    echo "  logs         - Show service logs"
    echo "  cleanup      - Stop and remove all containers"
    echo "  help         - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 development deploy"
    echo "  $0 production start"
    echo "  $0 status"
}

# Main script logic
case "${2:-deploy}" in
    "deploy")
        log_info "Deploying AMAS system in $ENVIRONMENT mode..."
        check_requirements
        create_env_file
        build_images
        start_services
        check_health
        show_status
        log_success "AMAS system deployed successfully!"
        ;;
    "start")
        log_info "Starting AMAS services..."
        docker-compose up -d
        show_status
        ;;
    "stop")
        log_info "Stopping AMAS services..."
        docker-compose down
        log_success "Services stopped"
        ;;
    "restart")
        log_info "Restarting AMAS services..."
        docker-compose restart
        show_status
        ;;
    "status")
        show_status
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "cleanup")
        cleanup
        ;;
    "help")
        show_help
        ;;
    *)
        log_error "Unknown command: $2"
        show_help
        exit 1
        ;;
esac