#!/bin/bash

# AMAS Restore Script
# Automated restore system for production and staging environments

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
BACKUP_DIR="${PROJECT_ROOT}/backups"
LOG_FILE="${PROJECT_ROOT}/logs/restore.log"

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
    echo "  -e, --environment ENV    Environment to restore (staging|production)"
    echo "  -b, --backup BACKUP      Backup to restore (timestamp or path)"
    echo "  -t, --type TYPE          Restore type (full|database|config|volumes)"
    echo "  -f, --force             Force restore without confirmation"
    echo "  -v, --verify            Verify backup before restore"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --environment production --backup 20240101-120000"
    echo "  $0 --environment staging --backup /path/to/backup --type database"
    echo "  $0 --environment production --backup 20240101-120000 --type full --force"
    echo ""
}

# Parse command line arguments
ENVIRONMENT=""
BACKUP=""
RESTORE_TYPE="full"
FORCE=false
VERIFY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -b|--backup)
            BACKUP="$2"
            shift 2
            ;;
        -t|--type)
            RESTORE_TYPE="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -v|--verify)
            VERIFY=true
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

# Validate arguments
if [[ -z "$ENVIRONMENT" ]]; then
    log_error "Environment is required. Use -e or --environment"
    usage
    exit 1
fi

if [[ -z "$BACKUP" ]]; then
    log_error "Backup is required. Use -b or --backup"
    usage
    exit 1
fi

if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    log_error "Invalid environment: $ENVIRONMENT. Must be 'staging' or 'production'"
    exit 1
fi

if [[ "$RESTORE_TYPE" != "full" && "$RESTORE_TYPE" != "database" && "$RESTORE_TYPE" != "config" && "$RESTORE_TYPE" != "volumes" ]]; then
    log_error "Invalid restore type: $RESTORE_TYPE. Must be 'full', 'database', 'config', or 'volumes'"
    exit 1
fi

# Find backup path
find_backup_path() {
    local backup="$1"
    local env="$2"
    
    # If backup is a full path, use it directly
    if [[ "$backup" == /* ]]; then
        if [[ -d "$backup" ]]; then
            echo "$backup"
            return 0
        else
            log_error "Backup path not found: $backup"
            return 1
        fi
    fi
    
    # If backup is a timestamp, find the matching backup
    local backup_pattern="${BACKUP_DIR}/${env}-*-${backup}"
    local matching_backups=($(find "$BACKUP_DIR" -name "${env}-*-${backup}" -type d 2>/dev/null))
    
    if [[ ${#matching_backups[@]} -eq 0 ]]; then
        # Try compressed backup
        local compressed_pattern="${BACKUP_DIR}/${env}-*-${backup}.tar.gz"
        local compressed_backups=($(find "$BACKUP_DIR" -name "${env}-*-${backup}.tar.gz" 2>/dev/null))
        
        if [[ ${#compressed_backups[@]} -eq 1 ]]; then
            echo "${compressed_backups[0]}"
            return 0
        elif [[ ${#compressed_backups[@]} -gt 1 ]]; then
            log_error "Multiple compressed backups found for timestamp: $backup"
            return 1
        else
            log_error "No backup found for timestamp: $backup"
            return 1
        fi
    elif [[ ${#matching_backups[@]} -eq 1 ]]; then
        echo "${matching_backups[0]}"
        return 0
    else
        log_error "Multiple backups found for timestamp: $backup"
        return 1
    fi
}

# Extract compressed backup
extract_backup() {
    local backup_path="$1"
    local extract_dir="$2"
    
    if [[ "$backup_path" == *.tar.gz ]]; then
        log "Extracting compressed backup..."
        
        if tar -xzf "$backup_path" -C "$extract_dir"; then
            log_success "Backup extracted successfully"
            
            # Find the extracted directory
            local extracted_dir=$(find "$extract_dir" -name "*" -type d -maxdepth 1 | head -1)
            echo "$extracted_dir"
            return 0
        else
            log_error "Failed to extract backup"
            return 1
        fi
    else
        echo "$backup_path"
        return 0
    fi
}

# Get compose file based on environment
get_compose_file() {
    local env="$1"
    if [[ "$env" == "production" ]]; then
        # Get current stack
        local current_stack_file="${PROJECT_ROOT}/.current-stack"
        local current_stack="blue"
        if [[ -f "$current_stack_file" ]]; then
            current_stack=$(cat "$current_stack_file")
        fi
        echo "docker-compose.production-${current_stack}.yml"
    else
        echo "docker-compose.staging.yml"
    fi
}

# Get service names based on environment
get_service_names() {
    local env="$1"
    if [[ "$env" == "production" ]]; then
        local current_stack=$(cat "${PROJECT_ROOT}/.current-stack" 2>/dev/null || echo "blue")
        echo "postgres-${current_stack}" "redis-${current_stack}" "neo4j-${current_stack}" "amas-${current_stack}"
    else
        echo "postgres" "redis" "neo4j" "amas" "nginx"
    fi
}

# Verify backup integrity
verify_backup() {
    local backup_path="$1"
    
    log "Verifying backup integrity..."
    
    # Check if manifest exists
    if [[ ! -f "${backup_path}/backup-manifest.json" ]]; then
        log_error "Backup manifest not found"
        return 1
    fi
    
    # Parse manifest
    local env=$(jq -r '.backup_info.environment' "${backup_path}/backup-manifest.json")
    local backup_type=$(jq -r '.backup_info.backup_type' "${backup_path}/backup-manifest.json")
    local timestamp=$(jq -r '.backup_info.timestamp' "${backup_path}/backup-manifest.json")
    
    log "Backup info: Environment=$env, Type=$backup_type, Timestamp=$timestamp"
    
    # Check database backup
    if [[ -f "${backup_path}/database-backup.sql" ]]; then
        if ! head -1 "${backup_path}/database-backup.sql" | grep -q "PostgreSQL database dump"; then
            log_error "Database backup appears to be corrupted"
            return 1
        else
            log_success "Database backup verification passed"
        fi
    fi
    
    # Check Redis backup
    if [[ -f "${backup_path}/redis-backup.rdb" ]]; then
        if ! file "${backup_path}/redis-backup.rdb" | grep -q "data"; then
            log_error "Redis backup appears to be corrupted"
            return 1
        else
            log_success "Redis backup verification passed"
        fi
    fi
    
    log_success "Backup verification completed successfully"
    return 0
}

# Stop services before restore
stop_services() {
    local env="$1"
    local compose_file=$(get_compose_file "$env")
    
    log "Stopping services for $env environment..."
    
    if [[ -f "$compose_file" ]]; then
        docker-compose -f "$compose_file" down --remove-orphans
        log_success "Services stopped"
    else
        log_warning "Compose file not found: $compose_file"
    fi
}

# Restore database
restore_database() {
    local env="$1"
    local backup_path="$2"
    local compose_file=$(get_compose_file "$env")
    
    log "Restoring database for $env environment..."
    
    # Get database service name
    local db_service=""
    if [[ "$env" == "production" ]]; then
        local current_stack=$(cat "${PROJECT_ROOT}/.current-stack" 2>/dev/null || echo "blue")
        db_service="postgres-${current_stack}"
    else
        db_service="postgres"
    fi
    
    # Check if database backup exists
    if [[ ! -f "${backup_path}/database-backup.sql" ]]; then
        log_error "Database backup not found: ${backup_path}/database-backup.sql"
        return 1
    fi
    
    # Start database service
    log "Starting database service..."
    docker-compose -f "$compose_file" up -d "$db_service"
    
    # Wait for database to be ready
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose -f "$compose_file" exec -T "$db_service" pg_isready -U postgres > /dev/null 2>&1; then
            log_success "Database is ready"
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
    
    # Restore database
    if docker-compose -f "$compose_file" exec -T "$db_service" psql -U postgres -d amas < "${backup_path}/database-backup.sql"; then
        log_success "Database restored successfully"
        return 0
    else
        log_error "Database restore failed"
        return 1
    fi
}

# Restore Redis data
restore_redis() {
    local env="$1"
    local backup_path="$2"
    local compose_file=$(get_compose_file "$env")
    
    log "Restoring Redis data for $env environment..."
    
    # Get Redis service name
    local redis_service=""
    if [[ "$env" == "production" ]]; then
        local current_stack=$(cat "${PROJECT_ROOT}/.current-stack" 2>/dev/null || echo "blue")
        redis_service="redis-${current_stack}"
    else
        redis_service="redis"
    fi
    
    # Check if Redis backup exists
    if [[ ! -f "${backup_path}/redis-backup.rdb" ]]; then
        log_error "Redis backup not found: ${backup_path}/redis-backup.rdb"
        return 1
    fi
    
    # Start Redis service
    log "Starting Redis service..."
    docker-compose -f "$compose_file" up -d "$redis_service"
    
    # Wait for Redis to be ready
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose -f "$compose_file" exec -T "$redis_service" redis-cli ping > /dev/null 2>&1; then
            log_success "Redis is ready"
            break
        else
            log "Waiting for Redis to be ready (attempt $attempt/$max_attempts)..."
            sleep 5
            ((attempt++))
        fi
    done
    
    if [[ $attempt -gt $max_attempts ]]; then
        log_error "Redis failed to become ready within expected time"
        return 1
    fi
    
    # Stop Redis
    docker-compose -f "$compose_file" stop "$redis_service"
    
    # Copy backup file
    if docker-compose -f "$compose_file" cp "${backup_path}/redis-backup.rdb" "$redis_service:/data/dump.rdb"; then
        log_success "Redis backup copied successfully"
    else
        log_error "Redis backup copy failed"
        return 1
    fi
    
    # Start Redis
    docker-compose -f "$compose_file" start "$redis_service"
    
    log_success "Redis data restored successfully"
    return 0
}

# Restore Neo4j data
restore_neo4j() {
    local env="$1"
    local backup_path="$2"
    local compose_file=$(get_compose_file "$env")
    
    log "Restoring Neo4j data for $env environment..."
    
    # Get Neo4j service name
    local neo4j_service=""
    if [[ "$env" == "production" ]]; then
        local current_stack=$(cat "${PROJECT_ROOT}/.current-stack" 2>/dev/null || echo "blue")
        neo4j_service="neo4j-${current_stack}"
    else
        neo4j_service="neo4j"
    fi
    
    # Check if Neo4j backup exists
    if [[ ! -f "${backup_path}/neo4j/neo4j-export.cypher" ]]; then
        log_error "Neo4j backup not found: ${backup_path}/neo4j/neo4j-export.cypher"
        return 1
    fi
    
    # Start Neo4j service
    log "Starting Neo4j service..."
    docker-compose -f "$compose_file" up -d "$neo4j_service"
    
    # Wait for Neo4j to be ready
    local max_attempts=60
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose -f "$compose_file" exec -T "$neo4j_service" cypher-shell -u neo4j -p "amas_password" "RETURN 1;" > /dev/null 2>&1; then
            log_success "Neo4j is ready"
            break
        else
            log "Waiting for Neo4j to be ready (attempt $attempt/$max_attempts)..."
            sleep 10
            ((attempt++))
        fi
    done
    
    if [[ $attempt -gt $max_attempts ]]; then
        log_error "Neo4j failed to become ready within expected time"
        return 1
    fi
    
    # Copy backup file
    if docker-compose -f "$compose_file" cp "${backup_path}/neo4j/neo4j-export.cypher" "$neo4j_service:/var/lib/neo4j/import/neo4j-export.cypher"; then
        log_success "Neo4j backup copied successfully"
    else
        log_error "Neo4j backup copy failed"
        return 1
    fi
    
    # Import data
    if docker-compose -f "$compose_file" exec -T "$neo4j_service" cypher-shell -u neo4j -p "amas_password" "CALL apoc.cypher.runFile('neo4j-export.cypher');" > /dev/null 2>&1; then
        log_success "Neo4j data imported successfully"
    else
        log_error "Neo4j data import failed"
        return 1
    fi
    
    log_success "Neo4j data restored successfully"
    return 0
}

# Restore application data
restore_application_data() {
    local env="$1"
    local backup_path="$2"
    
    log "Restoring application data for $env environment..."
    
    # Check if application data backup exists
    if [[ ! -d "${backup_path}/application-data" ]]; then
        log_error "Application data backup not found: ${backup_path}/application-data"
        return 1
    fi
    
    # Restore data directory
    if [[ -d "${backup_path}/application-data/data" ]]; then
        cp -r "${backup_path}/application-data/data" "${PROJECT_ROOT}/"
        log_success "Application data restored"
    else
        log_warning "Application data directory not found in backup"
    fi
    
    # Restore logs directory
    if [[ -d "${backup_path}/application-data/logs" ]]; then
        cp -r "${backup_path}/application-data/logs" "${PROJECT_ROOT}/"
        log_success "Application logs restored"
    else
        log_warning "Application logs directory not found in backup"
    fi
    
    # Restore configuration files
    local config_files=(
        ".env.${env}"
        "docker-compose.${env}.yml"
        "nginx/nginx.conf"
        "monitoring/prometheus.yml"
    )
    
    for config_file in "${config_files[@]}"; do
        if [[ -f "${backup_path}/application-data/${config_file}" ]]; then
            cp "${backup_path}/application-data/${config_file}" "${PROJECT_ROOT}/${config_file}"
            log "Configuration file restored: $config_file"
        fi
    done
    
    log_success "Application data restored successfully"
    return 0
}

# Restore Docker volumes
restore_docker_volumes() {
    local env="$1"
    local backup_path="$2"
    local compose_file=$(get_compose_file "$env")
    
    log "Restoring Docker volumes for $env environment..."
    
    # Check if volumes backup exists
    if [[ ! -d "${backup_path}/volumes" ]]; then
        log_error "Volumes backup not found: ${backup_path}/volumes"
        return 1
    fi
    
    # Get volume names
    local volume_names=$(docker-compose -f "$compose_file" config --volumes)
    
    for volume_name in $volume_names; do
        local volume_backup_file="${backup_path}/volumes/${volume_name}.tar"
        
        if [[ -f "$volume_backup_file" ]]; then
            log "Restoring volume: $volume_name"
            
            # Create volume if it doesn't exist
            docker volume create "$volume_name" > /dev/null 2>&1 || true
            
            # Restore volume
            if docker run --rm -v "$volume_name":/target -v "${backup_path}/volumes":/backup alpine tar xzf "/backup/${volume_name}.tar" -C /target; then
                log_success "Volume restored: $volume_name"
            else
                log_error "Volume restore failed: $volume_name"
            fi
        else
            log_warning "Volume backup not found: $volume_name"
        fi
    done
    
    log_success "Docker volumes restored successfully"
    return 0
}

# Start services after restore
start_services() {
    local env="$1"
    local compose_file=$(get_compose_file "$env")
    
    log "Starting services for $env environment..."
    
    if [[ -f "$compose_file" ]]; then
        docker-compose -f "$compose_file" up -d
        log_success "Services started"
    else
        log_error "Compose file not found: $compose_file"
        return 1
    fi
}

# Verify restore
verify_restore() {
    local env="$1"
    local compose_file=$(get_compose_file "$env")
    
    log "Verifying restore for $env environment..."
    
    # Wait for services to be ready
    sleep 30
    
    # Check service health
    local services=($(get_service_names "$env"))
    
    for service in "${services[@]}"; do
        if docker-compose -f "$compose_file" ps "$service" | grep -q "healthy\|Up"; then
            log_success "$service is healthy"
        else
            log_error "$service is not healthy"
            return 1
        fi
    done
    
    log_success "Restore verification completed successfully"
    return 0
}

# Send restore notifications
send_restore_notifications() {
    local env="$1"
    local restore_type="$2"
    local status="$3"
    local backup_path="$4"
    
    log "Sending restore notifications..."
    
    local message=""
    if [[ "$status" == "success" ]]; then
        message="✅ AMAS $env $restore_type restore completed successfully: $backup_path"
    else
        message="❌ AMAS $env $restore_type restore failed: $backup_path"
    fi
    
    # Send to Slack (if configured)
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$message\"}" \
            "$SLACK_WEBHOOK_URL" > /dev/null 2>&1 || true
    fi
    
    # Send email notification (if configured)
    if [[ -n "${NOTIFICATION_EMAIL:-}" ]]; then
        echo "$message" | \
            mail -s "AMAS Restore $status" "$NOTIFICATION_EMAIL" || true
    fi
    
    log_success "Restore notifications sent"
}

# Confirmation prompt
confirm_restore() {
    local env="$1"
    local backup_path="$2"
    local restore_type="$3"
    
    if [[ "$FORCE" == "true" ]]; then
        return 0
    fi
    
    echo ""
    log_warning "⚠️  RESTORE CONFIRMATION REQUIRED ⚠️"
    echo ""
    echo "Environment: $env"
    echo "Backup: $backup_path"
    echo "Type: $restore_type"
    echo ""
    echo "This will restore the $env environment from backup."
    echo "This action may cause data loss and service interruption."
    echo ""
    read -p "Are you sure you want to proceed? (yes/no): " -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        return 0
    else
        log "Restore cancelled by user"
        exit 0
    fi
}

# Main restore function
main() {
    log "🔄 Starting AMAS Restore"
    log "Environment: $ENVIRONMENT"
    log "Backup: $BACKUP"
    log "Type: $RESTORE_TYPE"
    log "Force: $FORCE"
    log "Verify: $VERIFY"
    
    # Find backup path
    local backup_path
    if ! backup_path=$(find_backup_path "$BACKUP" "$ENVIRONMENT"); then
        log_error "Failed to find backup"
        exit 1
    fi
    
    log "Found backup: $backup_path"
    
    # Extract compressed backup if needed
    local extract_dir=""
    if [[ "$backup_path" == *.tar.gz ]]; then
        extract_dir=$(mktemp -d)
        if ! backup_path=$(extract_backup "$backup_path" "$extract_dir"); then
            log_error "Failed to extract backup"
            exit 1
        fi
    fi
    
    # Verify backup if requested
    if [[ "$VERIFY" == "true" ]]; then
        if ! verify_backup "$backup_path"; then
            log_error "Backup verification failed"
            exit 1
        fi
    fi
    
    # Confirm restore
    confirm_restore "$ENVIRONMENT" "$backup_path" "$RESTORE_TYPE"
    
    # Set up error handling
    trap 'log_error "Restore interrupted by user"; send_restore_notifications "$ENVIRONMENT" "$RESTORE_TYPE" "failed" "$backup_path"; exit 1' ERR
    
    # Stop services before restore
    stop_services "$ENVIRONMENT"
    
    # Perform restore based on type
    case "$RESTORE_TYPE" in
        "full")
            restore_database "$ENVIRONMENT" "$backup_path"
            restore_redis "$ENVIRONMENT" "$backup_path"
            restore_neo4j "$ENVIRONMENT" "$backup_path"
            restore_application_data "$ENVIRONMENT" "$backup_path"
            restore_docker_volumes "$ENVIRONMENT" "$backup_path"
            ;;
        "database")
            restore_database "$ENVIRONMENT" "$backup_path"
            ;;
        "config")
            restore_application_data "$ENVIRONMENT" "$backup_path"
            ;;
        "volumes")
            restore_docker_volumes "$ENVIRONMENT" "$backup_path"
            ;;
    esac
    
    # Start services after restore
    start_services "$ENVIRONMENT"
    
    # Verify restore
    if ! verify_restore "$ENVIRONMENT"; then
        log_error "Restore verification failed"
        send_restore_notifications "$ENVIRONMENT" "$RESTORE_TYPE" "failed" "$backup_path"
        exit 1
    fi
    
    # Clean up extracted files
    if [[ -n "$extract_dir" && -d "$extract_dir" ]]; then
        rm -rf "$extract_dir"
    fi
    
    # Send notifications
    send_restore_notifications "$ENVIRONMENT" "$RESTORE_TYPE" "success" "$backup_path"
    
    log_success "🎉 Restore completed successfully!"
    
    echo ""
    echo "📊 Restore Summary:"
    echo "  • Environment: $ENVIRONMENT"
    echo "  • Type: $RESTORE_TYPE"
    echo "  • Backup: $backup_path"
    echo "  • Status: Success"
    echo ""
}

# Handle script interruption
trap 'log_error "Restore interrupted by user"; send_restore_notifications "$ENVIRONMENT" "$RESTORE_TYPE" "failed" "$BACKUP"; exit 1' INT TERM

# Run main function
main "$@"