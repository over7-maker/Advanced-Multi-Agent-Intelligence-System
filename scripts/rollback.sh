#!/bin/bash

# AMAS Rollback Script
# Automated rollback for production and staging environments

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
LOG_FILE="${PROJECT_ROOT}/logs/rollback.log"

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

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Environment to rollback (staging|production)"
    echo "  -t, --target VERSION     Target version to rollback to (optional)"
    echo "  -f, --force             Force rollback without confirmation"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --environment staging"
    echo "  $0 --environment production --target v1.2.3"
    echo "  $0 --environment production --force"
    echo ""
}

# Parse command line arguments
ENVIRONMENT=""
TARGET_VERSION=""
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -t|--target)
            TARGET_VERSION="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ -z "$ENVIRONMENT" ]]; then
    log_error "Environment is required. Use -e or --environment"
    usage
    exit 1
fi

if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    log_error "Invalid environment: $ENVIRONMENT. Must be 'staging' or 'production'"
    exit 1
fi

# Get current stack information
get_current_stack() {
    local env="$1"
    local stack_file=""
    
    if [[ "$env" == "production" ]]; then
        stack_file="${PROJECT_ROOT}/.current-stack"
        if [[ -f "$stack_file" ]]; then
            cat "$stack_file"
        else
            echo "blue"  # Default to blue if no current stack file
        fi
    else
        echo "staging"
    fi
}

# Get available backups
get_available_backups() {
    local env="$1"
    local backup_dir="${PROJECT_ROOT}/backups"
    
    if [[ -d "$backup_dir" ]]; then
        find "$backup_dir" -name "*${env}*" -type d | sort -r | head -10
    else
        echo ""
    fi
}

# Get available versions
get_available_versions() {
    local env="$1"
    
    if [[ "$env" == "production" ]]; then
        # Get available Docker image tags
        docker images --format "table {{.Tag}}" | grep -E "^v[0-9]+\.[0-9]+\.[0-9]+$" | sort -V -r | head -10
    else
        # For staging, get git tags
        git tag --sort=-version:refname | head -10
    fi
}

# Rollback staging environment
rollback_staging() {
    local target_version="$1"
    
    log "Rolling back staging environment..."
    
    cd "$PROJECT_ROOT"
    
    # Check if staging is currently running
    if ! docker-compose -f docker-compose.staging.yml ps -q > /dev/null 2>&1; then
        log_error "Staging environment is not running"
        return 1
    fi
    
    # Get available backups
    local backups=($(get_available_backups "staging"))
    if [[ ${#backups[@]} -eq 0 ]]; then
        log_error "No staging backups found"
        return 1
    fi
    
    # Select backup to restore
    local backup_to_restore=""
    if [[ -n "$target_version" ]]; then
        # Find backup matching target version
        for backup in "${backups[@]}"; do
            if [[ "$backup" == *"$target_version"* ]]; then
                backup_to_restore="$backup"
                break
            fi
        done
        
        if [[ -z "$backup_to_restore" ]]; then
            log_error "No backup found for version: $target_version"
            return 1
        fi
    else
        # Use most recent backup
        backup_to_restore="${backups[0]}"
    fi
    
    log "Using backup: $backup_to_restore"
    
    # Stop current staging environment
    log "Stopping current staging environment..."
    docker-compose -f docker-compose.staging.yml down --remove-orphans
    
    # Restore from backup
    if [[ -f "$backup_to_restore/docker-compose-backup.yml" ]]; then
        log "Restoring staging configuration..."
        cp "$backup_to_restore/docker-compose-backup.yml" docker-compose.staging.yml
        
        # Restore database if available
        if [[ -f "$backup_to_restore/database-backup.sql" ]]; then
            log "Restoring staging database..."
            docker-compose -f docker-compose.staging.yml up -d postgres
            sleep 30
            docker-compose -f docker-compose.staging.yml exec -T postgres psql -U postgres -d amas < "$backup_to_restore/database-backup.sql"
        fi
        
        # Start staging environment
        log "Starting staging environment..."
        docker-compose -f docker-compose.staging.yml up -d
        
        # Wait for services to be healthy
        sleep 30
        
        # Check service health
        check_staging_health
        
        log_success "Staging rollback completed successfully"
    else
        log_error "No valid backup found in: $backup_to_restore"
        return 1
    fi
}

# Rollback production environment
rollback_production() {
    local target_version="$1"
    
    log "Rolling back production environment..."
    
    cd "$PROJECT_ROOT"
    
    # Get current and target stacks
    local current_stack=$(get_current_stack "production")
    local target_stack=""
    
    if [[ "$current_stack" == "blue" ]]; then
        target_stack="green"
    else
        target_stack="blue"
    fi
    
    log "Current stack: $current_stack"
    log "Target stack: $target_stack"
    
    # Check if target stack exists
    local target_compose="docker-compose.production-${target_stack}.yml"
    if [[ ! -f "$target_compose" ]]; then
        log_error "Target stack compose file not found: $target_compose"
        return 1
    fi
    
    # Check if target stack is running
    if ! docker-compose -f "$target_compose" ps -q > /dev/null 2>&1; then
        log_error "Target stack is not running: $target_stack"
        return 1
    fi
    
    # Switch load balancer to target stack
    log "Switching load balancer to $target_stack stack..."
    switch_load_balancer "$target_stack"
    
    # Update current stack reference
    echo "$target_stack" > "${PROJECT_ROOT}/.current-stack"
    
    # Cleanup old stack
    log "Cleaning up old $current_stack stack..."
    cleanup_old_stack "$current_stack"
    
    log_success "Production rollback completed successfully"
}

# Switch load balancer
switch_load_balancer() {
    local target_stack="$1"
    local target_port="800${target_stack: -1}"
    local load_balancer_config="${PROJECT_ROOT}/nginx/production.conf"
    
    log "Switching load balancer to $target_stack stack (port $target_port)..."
    
    if [[ -f "$load_balancer_config" ]]; then
        # Update upstream configuration
        sed -i "s/server localhost:[0-9]*;/server localhost:$target_port;/" "$load_balancer_config"
        
        # Reload nginx
        if docker-compose ps nginx | grep -q "Up"; then
            docker-compose exec nginx nginx -s reload
            log_success "Load balancer switched to $target_stack stack"
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

# Check staging health
check_staging_health() {
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

# Check production health
check_production_health() {
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
        fi
    done
}

# Run post-rollback tests
run_post_rollback_tests() {
    local env="$1"
    
    log "Running post-rollback tests for $env environment..."
    
    local api_url=""
    if [[ "$env" == "production" ]]; then
        local current_stack=$(get_current_stack "production")
        api_url="http://localhost:800${current_stack: -1}"
    else
        api_url="http://localhost:8000"
    fi
    
    # Wait for API to be ready
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f "$api_url/health" > /dev/null 2>&1; then
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
    
    # Run basic health checks
    if curl -f "$api_url/health" > /dev/null 2>&1; then
        log_success "API health check passed"
    else
        log_error "API health check failed"
        return 1
    fi
    
    if curl -f "$api_url/metrics" > /dev/null 2>&1; then
        log_success "API metrics check passed"
    else
        log_error "API metrics check failed"
        return 1
    fi
    
    log_success "Post-rollback tests completed successfully"
}

# Send rollback notifications
send_rollback_notifications() {
    local env="$1"
    local status="$2"
    local message="$3"
    
    log "Sending rollback notifications..."
    
    # Send to Slack (if configured)
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🔄 AMAS $env Rollback $status: $message\"}" \
            "$SLACK_WEBHOOK_URL" > /dev/null 2>&1 || true
    fi
    
    # Send email notification (if configured)
    if [[ -n "${NOTIFICATION_EMAIL:-}" ]]; then
        echo "AMAS $env Rollback $status: $message" | \
            mail -s "AMAS $env Rollback $status" "$NOTIFICATION_EMAIL" || true
    fi
    
    log_success "Rollback notifications sent"
}

# Confirmation prompt
confirm_rollback() {
    local env="$1"
    local target="$2"
    
    if [[ "$FORCE" == "true" ]]; then
        return 0
    fi
    
    echo ""
    log_warning "⚠️  ROLLBACK CONFIRMATION REQUIRED ⚠️"
    echo ""
    echo "Environment: $env"
    echo "Target: $target"
    echo ""
    echo "This will rollback the $env environment to $target"
    echo "This action may cause service interruption."
    echo ""
    read -p "Are you sure you want to proceed? (yes/no): " -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        return 0
    else
        log "Rollback cancelled by user"
        exit 0
    fi
}

# Main rollback function
main() {
    log "🔄 Starting AMAS Rollback"
    log "Environment: $ENVIRONMENT"
    log "Target Version: ${TARGET_VERSION:-latest available}"
    log "Force: $FORCE"
    
    # Get target information
    local target_info=""
    if [[ -n "$TARGET_VERSION" ]]; then
        target_info="$TARGET_VERSION"
    else
        target_info="latest available"
    fi
    
    # Confirm rollback
    confirm_rollback "$ENVIRONMENT" "$target_info"
    
    # Set up error handling
    trap 'send_rollback_notifications "$ENVIRONMENT" "FAILED" "Rollback failed"; exit 1' ERR
    
    # Perform rollback based on environment
    if [[ "$ENVIRONMENT" == "staging" ]]; then
        rollback_staging "$TARGET_VERSION"
        check_staging_health
        run_post_rollback_tests "staging"
    else
        rollback_production "$TARGET_VERSION"
        local current_stack=$(get_current_stack "production")
        check_production_health "$current_stack"
        run_post_rollback_tests "production"
    fi
    
    send_rollback_notifications "$ENVIRONMENT" "SUCCESS" "Rollback completed successfully"
    
    log_success "🎉 Rollback completed successfully!"
    
    echo ""
    echo "📊 $ENVIRONMENT Environment Status:"
    if [[ "$ENVIRONMENT" == "production" ]]; then
        local current_stack=$(get_current_stack "production")
        echo "  • Active Stack: $current_stack"
        echo "  • AMAS API: http://localhost:8000"
        echo "  • AMAS Dashboard: http://localhost:3000"
    else
        echo "  • AMAS API: http://localhost:8000"
        echo "  • AMAS Dashboard: http://localhost:3000"
    fi
    echo ""
    echo "🔧 Management Commands:"
    echo "  • View logs: docker-compose -f docker-compose.${ENVIRONMENT}.yml logs -f"
    echo "  • Check status: docker-compose -f docker-compose.${ENVIRONMENT}.yml ps"
    echo ""
}

# Handle script interruption
trap 'log_error "Rollback interrupted by user"; send_rollback_notifications "$ENVIRONMENT" "INTERRUPTED" "Rollback was interrupted"; exit 1' INT TERM

# Run main function
main "$@"