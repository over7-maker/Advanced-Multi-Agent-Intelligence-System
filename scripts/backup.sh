#!/bin/bash

# AMAS Backup Script
# Automated backup system for production and staging environments

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
LOG_FILE="${PROJECT_ROOT}/logs/backup.log"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Create directories if they don't exist
mkdir -p "${BACKUP_DIR}"
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
    echo "  -e, --environment ENV    Environment to backup (staging|production)"
    echo "  -t, --type TYPE          Backup type (full|incremental|database|config)"
    echo "  -r, --retention DAYS     Retention period in days (default: 30)"
    echo "  -c, --compress           Compress backup files"
    echo "  -v, --verify             Verify backup integrity"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --environment production --type full"
    echo "  $0 --environment staging --type database --compress"
    echo "  $0 --environment production --type full --retention 7 --verify"
    echo ""
}

# Parse command line arguments
ENVIRONMENT=""
BACKUP_TYPE="full"
RETENTION_DAYS=30
COMPRESS=false
VERIFY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -t|--type)
            BACKUP_TYPE="$2"
            shift 2
            ;;
        -r|--retention)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        -c|--compress)
            COMPRESS=true
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

if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    log_error "Invalid environment: $ENVIRONMENT. Must be 'staging' or 'production'"
    exit 1
fi

if [[ "$BACKUP_TYPE" != "full" && "$BACKUP_TYPE" != "incremental" && "$BACKUP_TYPE" != "database" && "$BACKUP_TYPE" != "config" ]]; then
    log_error "Invalid backup type: $BACKUP_TYPE. Must be 'full', 'incremental', 'database', or 'config'"
    exit 1
fi

# Set backup directory
BACKUP_PATH="${BACKUP_DIR}/${ENVIRONMENT}-${BACKUP_TYPE}-${TIMESTAMP}"

# Create backup directory
mkdir -p "$BACKUP_PATH"

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

# Backup database
backup_database() {
    local env="$1"
    local backup_path="$2"
    local compose_file=$(get_compose_file "$env")
    
    log "Backing up database for $env environment..."
    
    # Get database service name
    local db_service=""
    if [[ "$env" == "production" ]]; then
        local current_stack=$(cat "${PROJECT_ROOT}/.current-stack" 2>/dev/null || echo "blue")
        db_service="postgres-${current_stack}"
    else
        db_service="postgres"
    fi
    
    # Check if database service is running
    if ! docker-compose -f "$compose_file" ps "$db_service" | grep -q "Up"; then
        log_error "Database service is not running: $db_service"
        return 1
    fi
    
    # Create database backup
    local db_backup_file="${backup_path}/database-backup.sql"
    if docker-compose -f "$compose_file" exec -T "$db_service" pg_dump -U postgres -d amas > "$db_backup_file"; then
        log_success "Database backup created: $db_backup_file"
        
        # Get backup size
        local backup_size=$(du -h "$db_backup_file" | cut -f1)
        log "Database backup size: $backup_size"
        
        return 0
    else
        log_error "Database backup failed"
        return 1
    fi
}

# Backup Redis data
backup_redis() {
    local env="$1"
    local backup_path="$2"
    local compose_file=$(get_compose_file "$env")
    
    log "Backing up Redis data for $env environment..."
    
    # Get Redis service name
    local redis_service=""
    if [[ "$env" == "production" ]]; then
        local current_stack=$(cat "${PROJECT_ROOT}/.current-stack" 2>/dev/null || echo "blue")
        redis_service="redis-${current_stack}"
    else
        redis_service="redis"
    fi
    
    # Check if Redis service is running
    if ! docker-compose -f "$compose_file" ps "$redis_service" | grep -q "Up"; then
        log_error "Redis service is not running: $redis_service"
        return 1
    fi
    
    # Create Redis backup
    local redis_backup_file="${backup_path}/redis-backup.rdb"
    if docker-compose -f "$compose_file" exec -T "$redis_service" redis-cli BGSAVE; then
        # Wait for background save to complete
        sleep 5
        
        # Copy the RDB file
        if docker-compose -f "$compose_file" cp "$redis_service:/data/dump.rdb" "$redis_backup_file"; then
            log_success "Redis backup created: $redis_backup_file"
            
            # Get backup size
            local backup_size=$(du -h "$redis_backup_file" | cut -f1)
            log "Redis backup size: $backup_size"
            
            return 0
        else
            log_error "Redis backup copy failed"
            return 1
        fi
    else
        log_error "Redis backup failed"
        return 1
    fi
}

# Backup Neo4j data
backup_neo4j() {
    local env="$1"
    local backup_path="$2"
    local compose_file=$(get_compose_file "$env")
    
    log "Backing up Neo4j data for $env environment..."
    
    # Get Neo4j service name
    local neo4j_service=""
    if [[ "$env" == "production" ]]; then
        local current_stack=$(cat "${PROJECT_ROOT}/.current-stack" 2>/dev/null || echo "blue")
        neo4j_service="neo4j-${current_stack}"
    else
        neo4j_service="neo4j"
    fi
    
    # Check if Neo4j service is running
    if ! docker-compose -f "$compose_file" ps "$neo4j_service" | grep -q "Up"; then
        log_error "Neo4j service is not running: $neo4j_service"
        return 1
    fi
    
    # Create Neo4j backup directory
    local neo4j_backup_dir="${backup_path}/neo4j"
    mkdir -p "$neo4j_backup_dir"
    
    # Export Neo4j data
    local neo4j_export_file="${neo4j_backup_dir}/neo4j-export.cypher"
    if docker-compose -f "$compose_file" exec -T "$neo4j_service" cypher-shell -u neo4j -p "amas_password" "CALL apoc.export.cypher.all('neo4j-export.cypher', {format: 'cypher-shell'});" > /dev/null 2>&1; then
        # Copy the export file
        if docker-compose -f "$compose_file" cp "$neo4j_service:/var/lib/neo4j/import/neo4j-export.cypher" "$neo4j_export_file"; then
            log_success "Neo4j backup created: $neo4j_export_file"
            
            # Get backup size
            local backup_size=$(du -h "$neo4j_export_file" | cut -f1)
            log "Neo4j backup size: $backup_size"
            
            return 0
        else
            log_error "Neo4j backup copy failed"
            return 1
        fi
    else
        log_error "Neo4j backup failed"
        return 1
    fi
}

# Backup application data
backup_application_data() {
    local env="$1"
    local backup_path="$2"
    
    log "Backing up application data for $env environment..."
    
    # Create application data directory
    local app_data_dir="${backup_path}/application-data"
    mkdir -p "$app_data_dir"
    
    # Backup data directory
    if [[ -d "${PROJECT_ROOT}/data" ]]; then
        cp -r "${PROJECT_ROOT}/data" "${app_data_dir}/"
        log_success "Application data backed up"
    else
        log_warning "Application data directory not found"
    fi
    
    # Backup logs directory
    if [[ -d "${PROJECT_ROOT}/logs" ]]; then
        cp -r "${PROJECT_ROOT}/logs" "${app_data_dir}/"
        log_success "Application logs backed up"
    else
        log_warning "Application logs directory not found"
    fi
    
    # Backup configuration files
    local config_files=(
        ".env.${env}"
        "docker-compose.${env}.yml"
        "nginx/nginx.conf"
        "monitoring/prometheus.yml"
    )
    
    for config_file in "${config_files[@]}"; do
        if [[ -f "${PROJECT_ROOT}/${config_file}" ]]; then
            cp "${PROJECT_ROOT}/${config_file}" "${app_data_dir}/"
            log "Configuration file backed up: $config_file"
        fi
    done
}

# Backup Docker volumes
backup_docker_volumes() {
    local env="$1"
    local backup_path="$2"
    local compose_file=$(get_compose_file "$env")
    
    log "Backing up Docker volumes for $env environment..."
    
    # Create volumes backup directory
    local volumes_backup_dir="${backup_path}/volumes"
    mkdir -p "$volumes_backup_dir"
    
    # Get volume names
    local volume_names=$(docker-compose -f "$compose_file" config --volumes)
    
    for volume_name in $volume_names; do
        log "Backing up volume: $volume_name"
        
        # Create volume backup
        local volume_backup_file="${volumes_backup_dir}/${volume_name}.tar"
        if docker run --rm -v "$volume_name":/source -v "${volumes_backup_dir}":/backup alpine tar czf "/backup/${volume_name}.tar" -C /source .; then
            log_success "Volume backed up: $volume_name"
        else
            log_error "Volume backup failed: $volume_name"
        fi
    done
}

# Create backup manifest
create_backup_manifest() {
    local backup_path="$1"
    local env="$2"
    local backup_type="$3"
    
    log "Creating backup manifest..."
    
    local manifest_file="${backup_path}/backup-manifest.json"
    
    cat > "$manifest_file" << EOF
{
  "backup_info": {
    "environment": "$env",
    "backup_type": "$backup_type",
    "timestamp": "$TIMESTAMP",
    "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "created_by": "$(whoami)",
    "hostname": "$(hostname)"
  },
  "backup_contents": {
    "database": $(if [[ -f "${backup_path}/database-backup.sql" ]]; then echo "true"; else echo "false"; fi),
    "redis": $(if [[ -f "${backup_path}/redis-backup.rdb" ]]; then echo "true"; else echo "false"; fi),
    "neo4j": $(if [[ -f "${backup_path}/neo4j/neo4j-export.cypher" ]]; then echo "true"; else echo "false"; fi),
    "application_data": $(if [[ -d "${backup_path}/application-data" ]]; then echo "true"; else echo "false"; fi),
    "volumes": $(if [[ -d "${backup_path}/volumes" ]]; then echo "true"; else echo "false"; fi)
  },
  "file_sizes": {
    "database": "$(if [[ -f "${backup_path}/database-backup.sql" ]]; then du -h "${backup_path}/database-backup.sql" | cut -f1; else echo "N/A"; fi)",
    "redis": "$(if [[ -f "${backup_path}/redis-backup.rdb" ]]; then du -h "${backup_path}/redis-backup.rdb" | cut -f1; else echo "N/A"; fi)",
    "neo4j": "$(if [[ -f "${backup_path}/neo4j/neo4j-export.cypher" ]]; then du -h "${backup_path}/neo4j/neo4j-export.cypher" | cut -f1; else echo "N/A"; fi)"
  },
  "total_size": "$(du -sh "$backup_path" | cut -f1)"
}
EOF

    log_success "Backup manifest created: $manifest_file"
}

# Verify backup integrity
verify_backup() {
    local backup_path="$1"
    
    log "Verifying backup integrity..."
    
    local verification_passed=true
    
    # Check if manifest exists
    if [[ ! -f "${backup_path}/backup-manifest.json" ]]; then
        log_error "Backup manifest not found"
        verification_passed=false
    fi
    
    # Check database backup
    if [[ -f "${backup_path}/database-backup.sql" ]]; then
        if ! head -1 "${backup_path}/database-backup.sql" | grep -q "PostgreSQL database dump"; then
            log_error "Database backup appears to be corrupted"
            verification_passed=false
        else
            log_success "Database backup verification passed"
        fi
    fi
    
    # Check Redis backup
    if [[ -f "${backup_path}/redis-backup.rdb" ]]; then
        if ! file "${backup_path}/redis-backup.rdb" | grep -q "data"; then
            log_error "Redis backup appears to be corrupted"
            verification_passed=false
        else
            log_success "Redis backup verification passed"
        fi
    fi
    
    if [[ "$verification_passed" == "true" ]]; then
        log_success "Backup verification completed successfully"
        return 0
    else
        log_error "Backup verification failed"
        return 1
    fi
}

# Compress backup
compress_backup() {
    local backup_path="$1"
    
    log "Compressing backup..."
    
    local compressed_file="${backup_path}.tar.gz"
    
    if tar -czf "$compressed_file" -C "$(dirname "$backup_path")" "$(basename "$backup_path")"; then
        log_success "Backup compressed: $compressed_file"
        
        # Get compressed size
        local compressed_size=$(du -h "$compressed_file" | cut -f1)
        log "Compressed backup size: $compressed_size"
        
        # Remove original directory
        rm -rf "$backup_path"
        
        return 0
    else
        log_error "Backup compression failed"
        return 1
    fi
}

# Clean up old backups
cleanup_old_backups() {
    local env="$1"
    local retention_days="$2"
    
    log "Cleaning up old backups (retention: $retention_days days)..."
    
    # Find old backups
    local old_backups=$(find "$BACKUP_DIR" -name "${env}-*" -type d -mtime +$retention_days)
    
    if [[ -n "$old_backups" ]]; then
        for backup in $old_backups; do
            log "Removing old backup: $backup"
            rm -rf "$backup"
        done
        log_success "Old backups cleaned up"
    else
        log "No old backups to clean up"
    fi
}

# Send backup notifications
send_backup_notifications() {
    local env="$1"
    local backup_type="$2"
    local status="$3"
    local backup_path="$4"
    
    log "Sending backup notifications..."
    
    local message=""
    if [[ "$status" == "success" ]]; then
        message="✅ AMAS $env $backup_type backup completed successfully: $backup_path"
    else
        message="❌ AMAS $env $backup_type backup failed: $backup_path"
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
            mail -s "AMAS Backup $status" "$NOTIFICATION_EMAIL" || true
    fi
    
    log_success "Backup notifications sent"
}

# Main backup function
main() {
    log "💾 Starting AMAS Backup"
    log "Environment: $ENVIRONMENT"
    log "Backup Type: $BACKUP_TYPE"
    log "Retention: $RETENTION_DAYS days"
    log "Compress: $COMPRESS"
    log "Verify: $VERIFY"
    
    # Set up error handling
    trap 'log_error "Backup interrupted by user"; send_backup_notifications "$ENVIRONMENT" "$BACKUP_TYPE" "failed" "$BACKUP_PATH"; exit 1' INT TERM
    
    # Perform backup based on type
    case "$BACKUP_TYPE" in
        "full")
            backup_database "$ENVIRONMENT" "$BACKUP_PATH"
            backup_redis "$ENVIRONMENT" "$BACKUP_PATH"
            backup_neo4j "$ENVIRONMENT" "$BACKUP_PATH"
            backup_application_data "$ENVIRONMENT" "$BACKUP_PATH"
            backup_docker_volumes "$ENVIRONMENT" "$BACKUP_PATH"
            ;;
        "incremental")
            backup_database "$ENVIRONMENT" "$BACKUP_PATH"
            backup_redis "$ENVIRONMENT" "$BACKUP_PATH"
            backup_application_data "$ENVIRONMENT" "$BACKUP_PATH"
            ;;
        "database")
            backup_database "$ENVIRONMENT" "$BACKUP_PATH"
            ;;
        "config")
            backup_application_data "$ENVIRONMENT" "$BACKUP_PATH"
            ;;
    esac
    
    # Create backup manifest
    create_backup_manifest "$BACKUP_PATH" "$ENVIRONMENT" "$BACKUP_TYPE"
    
    # Verify backup if requested
    if [[ "$VERIFY" == "true" ]]; then
        if ! verify_backup "$BACKUP_PATH"; then
            log_error "Backup verification failed"
            send_backup_notifications "$ENVIRONMENT" "$BACKUP_TYPE" "failed" "$BACKUP_PATH"
            exit 1
        fi
    fi
    
    # Compress backup if requested
    if [[ "$COMPRESS" == "true" ]]; then
        if ! compress_backup "$BACKUP_PATH"; then
            log_error "Backup compression failed"
            send_backup_notifications "$ENVIRONMENT" "$BACKUP_TYPE" "failed" "$BACKUP_PATH"
            exit 1
        fi
    fi
    
    # Clean up old backups
    cleanup_old_backups "$ENVIRONMENT" "$RETENTION_DAYS"
    
    # Send notifications
    send_backup_notifications "$ENVIRONMENT" "$BACKUP_TYPE" "success" "$BACKUP_PATH"
    
    log_success "🎉 Backup completed successfully!"
    
    echo ""
    echo "📊 Backup Summary:"
    echo "  • Environment: $ENVIRONMENT"
    echo "  • Type: $BACKUP_TYPE"
    echo "  • Location: $BACKUP_PATH"
    echo "  • Size: $(du -sh "$BACKUP_PATH" | cut -f1)"
    echo "  • Timestamp: $TIMESTAMP"
    echo ""
}

# Handle script interruption
trap 'log_error "Backup interrupted by user"; send_backup_notifications "$ENVIRONMENT" "$BACKUP_TYPE" "failed" "$BACKUP_PATH"; exit 1' INT TERM

# Run main function
main "$@"