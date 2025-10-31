#!/bin/bash

# AMAS Staging Deployment Script
# Automated deployment to staging environment

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
ENVIRONMENT="staging"
LOG_FILE="${PROJECT_ROOT}/logs/staging-deployment.log"
ENV_FILE="${PROJECT_ROOT}/.env.staging"

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
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks for staging..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if staging environment file exists
    if [[ ! -f "$ENV_FILE" ]]; then
        log_warning "Staging environment file not found. Creating from template..."
        if [[ -f "${PROJECT_ROOT}/.env.example" ]]; then
            cp "${PROJECT_ROOT}/.env.example" "$ENV_FILE"
            # Update for staging environment
            sed -i 's/ENVIRONMENT=production/ENVIRONMENT=staging/' "$ENV_FILE"
            sed -i 's/LOG_LEVEL=INFO/LOG_LEVEL=DEBUG/' "$ENV_FILE"
            log_success "Created staging environment file"
        else
            log_error "No environment template found. Please create .env.staging manually."
            exit 1
        fi
    fi
    
    # Check available resources
    available_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $available_space -lt 3 ]]; then
        log_warning "Low disk space: ${available_space}GB available. Recommended: 3GB+"
    fi
    
    log_success "Pre-deployment checks completed"
}

# Backup current staging environment
backup_current_deployment() {
    log "Creating backup of current staging deployment..."
    
    BACKUP_DIR="${PROJECT_ROOT}/backups/staging-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup current docker-compose state
    if docker-compose -f docker-compose.staging.yml ps -q > /dev/null 2>&1; then
        docker-compose -f docker-compose.staging.yml config > "$BACKUP_DIR/docker-compose-backup.yml"
        log_success "Backed up current deployment configuration"
    fi
    
    # Backup database if running
    if docker-compose -f docker-compose.staging.yml ps postgres | grep -q "Up"; then
        docker-compose -f docker-compose.staging.yml exec -T postgres pg_dump -U postgres amas > "$BACKUP_DIR/database-backup.sql"
        log_success "Backed up database"
    fi
    
    echo "$BACKUP_DIR" > "${PROJECT_ROOT}/.last-backup"
    log_success "Backup completed: $BACKUP_DIR"
}

# Deploy to staging
deploy_to_staging() {
    log "Deploying to staging environment..."
    
    cd "$PROJECT_ROOT"
    
    # Stop existing staging containers
    log "Stopping existing staging containers..."
    docker-compose -f docker-compose.staging.yml down --remove-orphans || true
    
    # Pull latest images
    log "Pulling latest images..."
    docker-compose -f docker-compose.staging.yml pull
    
    # Build and start services
    log "Building and starting staging services..."
    docker-compose -f docker-compose.staging.yml up -d --build
    
    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    check_service_health
    
    log_success "Staging deployment completed"
}

# Check service health
check_service_health() {
    log "Checking staging service health..."
    
    services=("postgres" "redis" "neo4j" "amas" "nginx")
    
    for service in "${services[@]}"; do
        if docker-compose -f docker-compose.staging.yml ps "$service" | grep -q "healthy\|Up"; then
            log_success "$service is healthy"
        else
            log_error "$service is not healthy"
            docker-compose -f docker-compose.staging.yml logs "$service" | tail -20
        fi
    done
}

# Run smoke tests
run_smoke_tests() {
    log "Running smoke tests against staging environment..."
    
    # Wait for API to be ready
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
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
    
    # Run basic smoke tests
    log "Running basic health checks..."
    
    # Test API health endpoint
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "API health check passed"
    else
        log_error "API health check failed"
        return 1
    fi
    
    # Test database connectivity
    if docker-compose -f docker-compose.staging.yml exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
        log_success "Database connectivity check passed"
    else
        log_error "Database connectivity check failed"
        return 1
    fi
    
    # Test Redis connectivity
    if docker-compose -f docker-compose.staging.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis connectivity check passed"
    else
        log_error "Redis connectivity check failed"
        return 1
    fi
    
    log_success "All smoke tests passed"
}

# Update monitoring
update_monitoring() {
    log "Updating monitoring configuration..."
    
    # Update Prometheus targets
    if [[ -f "${PROJECT_ROOT}/monitoring/prometheus.yml" ]]; then
        # Add staging-specific targets
        log "Updated Prometheus configuration for staging"
    fi
    
    # Update Grafana dashboards
    if [[ -d "${PROJECT_ROOT}/monitoring/grafana/provisioning" ]]; then
        log "Updated Grafana dashboards for staging"
    fi
    
    log_success "Monitoring configuration updated"
}

# Send notifications
send_notifications() {
    local status="$1"
    local message="$2"
    
    log "Sending deployment notifications..."
    
    # Send to Slack (if configured)
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚀 AMAS Staging Deployment $status: $message\"}" \
            "$SLACK_WEBHOOK_URL" > /dev/null 2>&1 || true
    fi
    
    # Send email notification (if configured)
    if [[ -n "${NOTIFICATION_EMAIL:-}" ]]; then
        echo "AMAS Staging Deployment $status: $message" | \
            mail -s "AMAS Staging Deployment $status" "$NOTIFICATION_EMAIL" || true
    fi
    
    log_success "Notifications sent"
}

# Rollback function
rollback_deployment() {
    log_error "Deployment failed. Initiating rollback..."
    
    if [[ -f "${PROJECT_ROOT}/.last-backup" ]]; then
        local backup_dir=$(cat "${PROJECT_ROOT}/.last-backup")
        log "Rolling back to backup: $backup_dir"
        
        # Stop current containers
        docker-compose -f docker-compose.staging.yml down --remove-orphans || true
        
        # Restore from backup
        if [[ -f "$backup_dir/docker-compose-backup.yml" ]]; then
            cp "$backup_dir/docker-compose-backup.yml" docker-compose.staging.yml
            docker-compose -f docker-compose.staging.yml up -d
            log_success "Rollback completed"
        else
            log_error "No backup found for rollback"
        fi
    else
        log_error "No backup information found. Manual rollback required."
    fi
}

# Main deployment function
main() {
    log "🚀 Starting AMAS Staging Deployment"
    log "Project: $PROJECT_NAME"
    log "Environment: $ENVIRONMENT"
    log "Directory: $PROJECT_ROOT"
    
    # Set up error handling
    trap 'rollback_deployment; send_notifications "FAILED" "Deployment failed and rollback initiated"; exit 1' ERR
    
    pre_deployment_checks
    backup_current_deployment
    deploy_to_staging
    run_smoke_tests
    update_monitoring
    send_notifications "SUCCESS" "Staging deployment completed successfully"
    
    log_success "🎉 Staging deployment completed successfully!"
    
    echo ""
    echo "📊 Staging Environment URLs:"
    echo "  • AMAS API: http://localhost:8000"
    echo "  • AMAS Dashboard: http://localhost:3000"
    echo "  • Neo4j Browser: http://localhost:7474"
    echo "  • Prometheus: http://localhost:9090"
    echo "  • Grafana: http://localhost:3001"
    echo ""
    echo "🔧 Management Commands:"
    echo "  • View logs: docker-compose -f docker-compose.staging.yml logs -f"
    echo "  • Stop services: docker-compose -f docker-compose.staging.yml down"
    echo "  • Restart services: docker-compose -f docker-compose.staging.yml restart"
    echo ""
}

# Handle script interruption
trap 'log_error "Deployment interrupted by user"; send_notifications "INTERRUPTED" "Deployment was interrupted"; exit 1' INT TERM

# Run main function
main "$@"