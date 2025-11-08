#!/bin/bash
# Canary Deployment Script for AMAS Progressive Delivery Pipeline
# Implements automated canary deployment with monitoring and automatic rollback

set -euo pipefail

# Configuration
NAMESPACE="${NAMESPACE:-amas-prod}"
ROLLOUT_NAME="${ROLLOUT_NAME:-amas-orchestrator}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
PROMOTION_WAIT_TIME="${PROMOTION_WAIT_TIME:-120}"  # 2 minutes between steps
MAX_ROLLBACK_TIME="${MAX_ROLLBACK_TIME:-120}"  # 2 minutes for rollback
HEALTH_CHECK_INTERVAL="${HEALTH_CHECK_INTERVAL:-10}"  # 10 seconds

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Check if Argo Rollouts is installed
    if ! kubectl get crd rollouts.argoproj.io &> /dev/null; then
        log_error "Argo Rollouts CRD not found. Please install Argo Rollouts first."
        log_info "Install with: kubectl create namespace argo-rollouts && kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml"
        exit 1
    fi
    
    # Check if namespace exists
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_warning "Namespace $NAMESPACE does not exist. Creating it..."
        kubectl create namespace "$NAMESPACE"
    fi
    
    log_success "Prerequisites check passed"
}

# Update rollout image
update_rollout_image() {
    local image="${1:-}"
    if [ -z "$image" ]; then
        log_error "Image name is required"
        exit 1
    fi
    
    log_info "Updating rollout image to $image..."
    
    if ! kubectl set image rollout/"$ROLLOUT_NAME" \
        orchestrator="$image" \
        -n "$NAMESPACE" 2>/dev/null; then
        log_error "Failed to update rollout image"
        exit 1
    fi
    
    log_success "Rollout image updated"
}

# Wait for rollout to be ready
wait_for_rollout() {
    local timeout="${1:-300}"  # 5 minutes default
    log_info "Waiting for rollout to be ready (timeout: ${timeout}s)..."
    
    if kubectl rollout status rollout/"$ROLLOUT_NAME" -n "$NAMESPACE" --timeout="${timeout}s"; then
        log_success "Rollout is ready"
        return 0
    else
        log_error "Rollout failed to become ready within ${timeout}s"
        return 1
    fi
}

# Check health endpoint
check_health() {
    local endpoint="${1:-/health/ready}"
    local service_url="${2:-}"
    
    if [ -z "$service_url" ]; then
        # Try to get service URL from ingress
        service_url=$(kubectl get ingress -n "$NAMESPACE" -o jsonpath='{.items[0].spec.rules[0].host}' 2>/dev/null || echo "")
        if [ -z "$service_url" ]; then
            log_warning "Could not determine service URL, skipping health check"
            return 0
        fi
        service_url="https://${service_url}"
    fi
    
    log_info "Checking health endpoint: ${service_url}${endpoint}"
    
    if curl -f -s -m 10 "${service_url}${endpoint}" > /dev/null 2>&1; then
        log_success "Health check passed"
        return 0
    else
        log_warning "Health check failed or endpoint not accessible"
        return 1
    fi
}

# Monitor canary deployment
monitor_canary() {
    log_info "Monitoring canary deployment..."
    
    local start_time=$(date +%s)
    local check_count=0
    local max_checks=12  # 2 minutes at 10 second intervals
    local unhealthy_count=0
    local max_unhealthy=3  # Allow 3 consecutive failures
    
    while [ $check_count -lt $max_checks ]; do
        check_count=$((check_count + 1))
        
        # Check rollout status
        local rollout_status=$(kubectl get rollout "$ROLLOUT_NAME" -n "$NAMESPACE" -o jsonpath='{.status.phase}' 2>/dev/null || echo "Unknown")
        
        if [ "$rollout_status" = "Degraded" ] || [ "$rollout_status" = "Failed" ]; then
            log_error "Rollout is in $rollout_status state"
            unhealthy_count=$((unhealthy_count + 1))
            
            if [ $unhealthy_count -ge $max_unhealthy ]; then
                log_error "Rollout has been unhealthy for too long, triggering rollback"
                return 1
            fi
        else
            unhealthy_count=0
        fi
        
        # Check analysis runs
        local analysis_status=$(kubectl get analysisrun -n "$NAMESPACE" -l app="$ROLLOUT_NAME" -o jsonpath='{.items[-1].status.phase}' 2>/dev/null || echo "Unknown")
        
        if [ "$analysis_status" = "Failed" ]; then
            log_error "Analysis run failed, triggering rollback"
            return 1
        fi
        
        log_info "Check $check_count/$max_checks - Rollout: $rollout_status, Analysis: $analysis_status"
        sleep $HEALTH_CHECK_INTERVAL
    done
    
    log_success "Canary monitoring completed successfully"
    return 0
}

# Promote canary to next step
promote_canary() {
    log_info "Promoting canary to next step..."
    
    if kubectl argo rollouts promote "$ROLLOUT_NAME" -n "$NAMESPACE"; then
        log_success "Canary promoted successfully"
        return 0
    else
        log_error "Failed to promote canary"
        return 1
    fi
}

# Rollback deployment
rollback_deployment() {
    log_warning "Initiating rollback..."
    
    if kubectl rollout undo rollout/"$ROLLOUT_NAME" -n "$NAMESPACE"; then
        log_info "Rollback command issued, waiting for completion..."
        
        if wait_for_rollout "$MAX_ROLLBACK_TIME"; then
            log_success "Rollback completed successfully"
            return 0
        else
            log_error "Rollback did not complete within ${MAX_ROLLBACK_TIME}s"
            return 1
        fi
    else
        log_error "Failed to initiate rollback"
        return 1
    fi
}

# Main canary deployment flow
main() {
    log_info "Starting canary deployment for $ROLLOUT_NAME in namespace $NAMESPACE"
    log_info "Image tag: $IMAGE_TAG"
    
    # Check prerequisites
    check_prerequisites
    
    # Get current image
    local current_image=$(kubectl get rollout "$ROLLOUT_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null || echo "")
    local new_image="${DOCKER_REGISTRY:-ghcr.io/over7-maker}/${IMAGE_NAME:-amas-orchestrator}:${IMAGE_TAG}"
    
    if [ -z "$current_image" ]; then
        log_error "Rollout $ROLLOUT_NAME not found in namespace $NAMESPACE"
        exit 1
    fi
    
    log_info "Current image: $current_image"
    log_info "New image: $new_image"
    
    # Update rollout image (triggers canary)
    update_rollout_image "$new_image"
    
    # Wait for initial canary pod
    log_info "Waiting for canary pod to be ready..."
    sleep 30
    
    # Monitor canary at each step
    local canary_steps=(10 25 50 75 100)
    local step_index=0
    
    for traffic_percent in "${canary_steps[@]}"; do
        step_index=$((step_index + 1))
        log_info "=== Canary Step $step_index: ${traffic_percent}% traffic ==="
        
        # Wait for current step to stabilize
        log_info "Waiting ${PROMOTION_WAIT_TIME}s for step to stabilize..."
        sleep $PROMOTION_WAIT_TIME
        
        # Monitor canary health
        if ! monitor_canary; then
            log_error "Canary health check failed at ${traffic_percent}% traffic"
            rollback_deployment
            exit 1
        fi
        
        # If not at 100%, promote to next step
        if [ $traffic_percent -lt 100 ]; then
            if ! promote_canary; then
                log_error "Failed to promote canary to next step"
                rollback_deployment
                exit 1
            fi
        else
            log_success "Canary deployment completed successfully at 100% traffic"
        fi
    done
    
    # Final health check
    log_info "Performing final health check..."
    if check_health; then
        log_success "Final health check passed"
    else
        log_warning "Final health check had issues, but deployment is complete"
    fi
    
    log_success "Canary deployment completed successfully!"
    log_info "Deployment summary:"
    kubectl get rollout "$ROLLOUT_NAME" -n "$NAMESPACE" -o wide
}

# Handle script interruption
trap 'log_error "Deployment interrupted. Initiating rollback..."; rollback_deployment; exit 1' INT TERM

# Run main function
main "$@"
