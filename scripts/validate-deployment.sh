#!/bin/bash

# AMAS Deployment Validation Script
# Comprehensive validation checks for production and staging deployments

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
LOG_FILE="${PROJECT_ROOT}/logs/validation.log"
VALIDATION_RESULTS="${PROJECT_ROOT}/logs/validation-results.json"

# Create logs directory if it doesn't exist
mkdir -p "${PROJECT_ROOT}/logs"

# Validation results
declare -A VALIDATION_RESULTS
VALIDATION_PASSED=0
VALIDATION_FAILED=0
VALIDATION_WARNINGS=0

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$LOG_FILE"
    ((VALIDATION_PASSED++))
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}" | tee -a "$LOG_FILE"
    ((VALIDATION_WARNINGS++))
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
    ((VALIDATION_FAILED++))
}

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Environment to validate (staging|production)"
    echo "  -t, --type TYPE          Validation type (basic|comprehensive|security|performance)"
    echo "  -u, --url URL           Base URL for validation (optional)"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --environment staging --type basic"
    echo "  $0 --environment production --type comprehensive --url https://api.example.com"
    echo ""
}

# Parse command line arguments
ENVIRONMENT=""
VALIDATION_TYPE="comprehensive"
BASE_URL=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -t|--type)
            VALIDATION_TYPE="$2"
            shift 2
            ;;
        -u|--url)
            BASE_URL="$2"
            shift 2
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

if [[ "$VALIDATION_TYPE" != "basic" && "$VALIDATION_TYPE" != "comprehensive" && "$VALIDATION_TYPE" != "security" && "$VALIDATION_TYPE" != "performance" ]]; then
    log_error "Invalid validation type: $VALIDATION_TYPE. Must be 'basic', 'comprehensive', 'security', or 'performance'"
    exit 1
fi

# Set default URL if not provided
if [[ -z "$BASE_URL" ]]; then
    if [[ "$ENVIRONMENT" == "production" ]]; then
        BASE_URL="http://localhost:8000"
    else
        BASE_URL="http://localhost:8000"
    fi
fi

# Record validation result
record_result() {
    local check_name="$1"
    local status="$2"
    local message="$3"
    local details="$4"
    
    VALIDATION_RESULTS["$check_name"]="{\"status\":\"$status\",\"message\":\"$message\",\"details\":\"$details\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
}

# Basic connectivity validation
validate_connectivity() {
    log "Validating basic connectivity..."
    
    # Test API health endpoint
    if curl -f -s "$BASE_URL/health" > /dev/null 2>&1; then
        log_success "API health endpoint is accessible"
        record_result "api_health" "PASS" "API health endpoint is accessible" "GET $BASE_URL/health"
    else
        log_error "API health endpoint is not accessible"
        record_result "api_health" "FAIL" "API health endpoint is not accessible" "GET $BASE_URL/health"
        return 1
    fi
    
    # Test API metrics endpoint
    if curl -f -s "$BASE_URL/metrics" > /dev/null 2>&1; then
        log_success "API metrics endpoint is accessible"
        record_result "api_metrics" "PASS" "API metrics endpoint is accessible" "GET $BASE_URL/metrics"
    else
        log_warning "API metrics endpoint is not accessible"
        record_result "api_metrics" "WARN" "API metrics endpoint is not accessible" "GET $BASE_URL/metrics"
    fi
    
    # Test response time
    local response_time=$(curl -o /dev/null -s -w "%{time_total}" "$BASE_URL/health")
    if (( $(echo "$response_time < 2.0" | bc -l) )); then
        log_success "API response time is acceptable: ${response_time}s"
        record_result "api_response_time" "PASS" "API response time is acceptable" "${response_time}s"
    else
        log_warning "API response time is slow: ${response_time}s"
        record_result "api_response_time" "WARN" "API response time is slow" "${response_time}s"
    fi
}

# Service health validation
validate_service_health() {
    log "Validating service health..."
    
    local compose_file=""
    if [[ "$ENVIRONMENT" == "production" ]]; then
        # Get current stack
        local current_stack_file="${PROJECT_ROOT}/.current-stack"
        local current_stack="blue"
        if [[ -f "$current_stack_file" ]]; then
            current_stack=$(cat "$current_stack_file")
        fi
        compose_file="docker-compose.production-${current_stack}.yml"
    else
        compose_file="docker-compose.staging.yml"
    fi
    
    if [[ ! -f "$compose_file" ]]; then
        log_error "Compose file not found: $compose_file"
        record_result "compose_file" "FAIL" "Compose file not found" "$compose_file"
        return 1
    fi
    
    # Check if services are running
    if ! docker-compose -f "$compose_file" ps -q > /dev/null 2>&1; then
        log_error "No services are running"
        record_result "services_running" "FAIL" "No services are running" "$compose_file"
        return 1
    fi
    
    # Check individual services
    local services=()
    if [[ "$ENVIRONMENT" == "production" ]]; then
        local current_stack=$(cat "${PROJECT_ROOT}/.current-stack" 2>/dev/null || echo "blue")
        services=("postgres-${current_stack}" "redis-${current_stack}" "neo4j-${current_stack}" "amas-${current_stack}")
    else
        services=("postgres" "redis" "neo4j" "amas" "nginx")
    fi
    
    for service in "${services[@]}"; do
        if docker-compose -f "$compose_file" ps "$service" | grep -q "healthy\|Up"; then
            log_success "$service is healthy"
            record_result "service_$service" "PASS" "$service is healthy" "docker-compose ps $service"
        else
            log_error "$service is not healthy"
            record_result "service_$service" "FAIL" "$service is not healthy" "docker-compose ps $service"
        fi
    done
}

# Database validation
validate_database() {
    log "Validating database connectivity..."
    
    local compose_file=""
    local db_service=""
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        local current_stack=$(cat "${PROJECT_ROOT}/.current-stack" 2>/dev/null || echo "blue")
        compose_file="docker-compose.production-${current_stack}.yml"
        db_service="postgres-${current_stack}"
    else
        compose_file="docker-compose.staging.yml"
        db_service="postgres"
    fi
    
    # Test database connectivity
    if docker-compose -f "$compose_file" exec -T "$db_service" pg_isready -U postgres > /dev/null 2>&1; then
        log_success "Database is accessible"
        record_result "database_connectivity" "PASS" "Database is accessible" "pg_isready"
    else
        log_error "Database is not accessible"
        record_result "database_connectivity" "FAIL" "Database is not accessible" "pg_isready"
        return 1
    fi
    
    # Test database queries
    local query_result=$(docker-compose -f "$compose_file" exec -T "$db_service" psql -U postgres -d amas -c "SELECT 1;" 2>/dev/null | grep -c "1 row" || echo "0")
    if [[ "$query_result" -gt 0 ]]; then
        log_success "Database queries are working"
        record_result "database_queries" "PASS" "Database queries are working" "SELECT 1"
    else
        log_error "Database queries are not working"
        record_result "database_queries" "FAIL" "Database queries are not working" "SELECT 1"
    fi
}

# Redis validation
validate_redis() {
    log "Validating Redis connectivity..."
    
    local compose_file=""
    local redis_service=""
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        local current_stack=$(cat "${PROJECT_ROOT}/.current-stack" 2>/dev/null || echo "blue")
        compose_file="docker-compose.production-${current_stack}.yml"
        redis_service="redis-${current_stack}"
    else
        compose_file="docker-compose.staging.yml"
        redis_service="redis"
    fi
    
    # Test Redis connectivity
    if docker-compose -f "$compose_file" exec -T "$redis_service" redis-cli ping > /dev/null 2>&1; then
        log_success "Redis is accessible"
        record_result "redis_connectivity" "PASS" "Redis is accessible" "redis-cli ping"
    else
        log_error "Redis is not accessible"
        record_result "redis_connectivity" "FAIL" "Redis is not accessible" "redis-cli ping"
        return 1
    fi
    
    # Test Redis operations
    if docker-compose -f "$compose_file" exec -T "$redis_service" redis-cli set test_key "test_value" > /dev/null 2>&1; then
        local get_result=$(docker-compose -f "$compose_file" exec -T "$redis_service" redis-cli get test_key 2>/dev/null | tr -d '\r\n')
        if [[ "$get_result" == "test_value" ]]; then
            log_success "Redis operations are working"
            record_result "redis_operations" "PASS" "Redis operations are working" "SET/GET test"
        else
            log_error "Redis operations are not working"
            record_result "redis_operations" "FAIL" "Redis operations are not working" "SET/GET test"
        fi
        # Clean up test key
        docker-compose -f "$compose_file" exec -T "$redis_service" redis-cli del test_key > /dev/null 2>&1
    fi
}

# Neo4j validation
validate_neo4j() {
    log "Validating Neo4j connectivity..."
    
    local compose_file=""
    local neo4j_service=""
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        local current_stack=$(cat "${PROJECT_ROOT}/.current-stack" 2>/dev/null || echo "blue")
        compose_file="docker-compose.production-${current_stack}.yml"
        neo4j_service="neo4j-${current_stack}"
    else
        compose_file="docker-compose.staging.yml"
        neo4j_service="neo4j"
    fi
    
    # Test Neo4j connectivity
    if docker-compose -f "$compose_file" exec -T "$neo4j_service" cypher-shell -u neo4j -p "amas_password" "RETURN 1;" > /dev/null 2>&1; then
        log_success "Neo4j is accessible"
        record_result "neo4j_connectivity" "PASS" "Neo4j is accessible" "cypher-shell RETURN 1"
    else
        log_error "Neo4j is not accessible"
        record_result "neo4j_connectivity" "FAIL" "Neo4j is not accessible" "cypher-shell RETURN 1"
        return 1
    fi
}

# API endpoint validation
validate_api_endpoints() {
    log "Validating API endpoints..."
    
    local endpoints=(
        "/health"
        "/metrics"
        "/api/v1/agents"
        "/api/v1/tasks"
        "/api/v1/health"
    )
    
    for endpoint in "${endpoints[@]}"; do
        local url="$BASE_URL$endpoint"
        local status_code=$(curl -o /dev/null -s -w "%{http_code}" "$url" || echo "000")
        
        if [[ "$status_code" == "200" ]]; then
            log_success "Endpoint $endpoint is working (HTTP $status_code)"
            record_result "endpoint_$endpoint" "PASS" "Endpoint is working" "HTTP $status_code"
        elif [[ "$status_code" == "404" ]]; then
            log_warning "Endpoint $endpoint not found (HTTP $status_code)"
            record_result "endpoint_$endpoint" "WARN" "Endpoint not found" "HTTP $status_code"
        else
            log_error "Endpoint $endpoint failed (HTTP $status_code)"
            record_result "endpoint_$endpoint" "FAIL" "Endpoint failed" "HTTP $status_code"
        fi
    done
}

# Security validation
validate_security() {
    log "Validating security configuration..."
    
    # Check HTTPS (if applicable)
    if [[ "$BASE_URL" == https://* ]]; then
        local ssl_info=$(echo | openssl s_client -servername "$(echo "$BASE_URL" | sed 's|https://||' | cut -d'/' -f1)" -connect "$(echo "$BASE_URL" | sed 's|https://||' | cut -d'/' -f1):443" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null || echo "")
        if [[ -n "$ssl_info" ]]; then
            log_success "SSL certificate is valid"
            record_result "ssl_certificate" "PASS" "SSL certificate is valid" "openssl check"
        else
            log_warning "SSL certificate validation failed"
            record_result "ssl_certificate" "WARN" "SSL certificate validation failed" "openssl check"
        fi
    else
        log_warning "HTTPS not configured (using HTTP)"
        record_result "ssl_certificate" "WARN" "HTTPS not configured" "HTTP only"
    fi
    
    # Check security headers
    local security_headers=("X-Frame-Options" "X-Content-Type-Options" "X-XSS-Protection" "Strict-Transport-Security")
    for header in "${security_headers[@]}"; do
        local header_value=$(curl -s -I "$BASE_URL/health" | grep -i "$header" || echo "")
        if [[ -n "$header_value" ]]; then
            log_success "Security header $header is present"
            record_result "security_header_$header" "PASS" "Security header is present" "$header_value"
        else
            log_warning "Security header $header is missing"
            record_result "security_header_$header" "WARN" "Security header is missing" "Not found"
        fi
    done
}

# Performance validation
validate_performance() {
    log "Validating performance metrics..."
    
    # Test response times for different endpoints
    local endpoints=("/health" "/metrics" "/api/v1/agents")
    local total_time=0
    local endpoint_count=0
    
    for endpoint in "${endpoints[@]}"; do
        local url="$BASE_URL$endpoint"
        local response_time=$(curl -o /dev/null -s -w "%{time_total}" "$url" 2>/dev/null || echo "0")
        if (( $(echo "$response_time > 0" | bc -l) )); then
            total_time=$(echo "$total_time + $response_time" | bc -l)
            ((endpoint_count++))
            
            if (( $(echo "$response_time < 1.0" | bc -l) )); then
                log_success "Endpoint $endpoint response time: ${response_time}s"
                record_result "perf_$endpoint" "PASS" "Response time acceptable" "${response_time}s"
            else
                log_warning "Endpoint $endpoint response time: ${response_time}s (slow)"
                record_result "perf_$endpoint" "WARN" "Response time slow" "${response_time}s"
            fi
        fi
    done
    
    if [[ $endpoint_count -gt 0 ]]; then
        local avg_time=$(echo "scale=3; $total_time / $endpoint_count" | bc -l)
        log "Average response time: ${avg_time}s"
        record_result "avg_response_time" "INFO" "Average response time" "${avg_time}s"
    fi
    
    # Test concurrent requests
    log "Testing concurrent request handling..."
    local concurrent_requests=10
    local success_count=0
    
    for i in $(seq 1 $concurrent_requests); do
        if curl -f -s "$BASE_URL/health" > /dev/null 2>&1; then
            ((success_count++))
        fi &
    done
    wait
    
    local success_rate=$(echo "scale=2; $success_count * 100 / $concurrent_requests" | bc -l)
    if (( $(echo "$success_rate >= 90" | bc -l) )); then
        log_success "Concurrent request handling: ${success_rate}% success rate"
        record_result "concurrent_requests" "PASS" "Concurrent request handling good" "${success_rate}%"
    else
        log_warning "Concurrent request handling: ${success_rate}% success rate"
        record_result "concurrent_requests" "WARN" "Concurrent request handling poor" "${success_rate}%"
    fi
}

# Generate validation report
generate_report() {
    log "Generating validation report..."
    
    local report_file="$VALIDATION_RESULTS"
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    cat > "$report_file" << EOF
{
  "validation_summary": {
    "environment": "$ENVIRONMENT",
    "validation_type": "$VALIDATION_TYPE",
    "base_url": "$BASE_URL",
    "timestamp": "$timestamp",
    "total_checks": $((VALIDATION_PASSED + VALIDATION_FAILED + VALIDATION_WARNINGS)),
    "passed": $VALIDATION_PASSED,
    "failed": $VALIDATION_FAILED,
    "warnings": $VALIDATION_WARNINGS,
    "success_rate": "$(echo "scale=2; $VALIDATION_PASSED * 100 / ($VALIDATION_PASSED + $VALIDATION_FAILED + $VALIDATION_WARNINGS)" | bc -l)%"
  },
  "validation_results": {
EOF

    local first=true
    for check_name in "${!VALIDATION_RESULTS[@]}"; do
        if [[ "$first" == "true" ]]; then
            first=false
        else
            echo "," >> "$report_file"
        fi
        echo "    \"$check_name\": ${VALIDATION_RESULTS[$check_name]}" >> "$report_file"
    done

    cat >> "$report_file" << EOF
  }
}
EOF

    log_success "Validation report generated: $report_file"
}

# Main validation function
main() {
    log "🔍 Starting AMAS Deployment Validation"
    log "Environment: $ENVIRONMENT"
    log "Validation Type: $VALIDATION_TYPE"
    log "Base URL: $BASE_URL"
    
    # Basic validation (always run)
    validate_connectivity
    validate_service_health
    validate_database
    validate_redis
    validate_neo4j
    validate_api_endpoints
    
    # Additional validation based on type
    case "$VALIDATION_TYPE" in
        "comprehensive")
            validate_security
            validate_performance
            ;;
        "security")
            validate_security
            ;;
        "performance")
            validate_performance
            ;;
        "basic")
            # Only basic validation already completed
            ;;
    esac
    
    # Generate report
    generate_report
    
    # Summary
    echo ""
    log "📊 Validation Summary:"
    log "  ✅ Passed: $VALIDATION_PASSED"
    log "  ❌ Failed: $VALIDATION_FAILED"
    log "  ⚠️  Warnings: $VALIDATION_WARNINGS"
    log "  📈 Success Rate: $(echo "scale=2; $VALIDATION_PASSED * 100 / ($VALIDATION_PASSED + $VALIDATION_FAILED + $VALIDATION_WARNINGS)" | bc -l)%"
    echo ""
    
    if [[ $VALIDATION_FAILED -eq 0 ]]; then
        log_success "🎉 All validations passed!"
        exit 0
    else
        log_error "❌ Some validations failed!"
        exit 1
    fi
}

# Handle script interruption
trap 'log_error "Validation interrupted by user"; exit 1' INT TERM

# Run main function
main "$@"