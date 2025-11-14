#!/bin/bash
# Blue-Green Deployment Script for AMAS Emergency Deployments
# Provides instant traffic switching for emergency scenarios

set -euo pipefail

# Configuration
NAMESPACE="${NAMESPACE:-amas-prod}"
SERVICE_NAME="${SERVICE_NAME:-amas-orchestrator}"
BLUE_DEPLOYMENT="${BLUE_DEPLOYMENT:-${SERVICE_NAME}-blue}"
GREEN_DEPLOYMENT="${GREEN_DEPLOYMENT:-${SERVICE_NAME}-green}"
CURRENT_COLOR="${CURRENT_COLOR:-blue}"  # Current active color
IMAGE_TAG="${IMAGE_TAG:-latest}"
HEALTH_CHECK_TIMEOUT="${HEALTH_CHECK_TIMEOUT:-300}"  # 5 minutes

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

# Determine target color (opposite of current)
get_target_color() {
    if [ "$CURRENT_COLOR" = "blue" ]; then
        echo "green"
    else
        echo "blue"
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_warning "Namespace $NAMESPACE does not exist. Creating it..."
        kubectl create namespace "$NAMESPACE"
    fi
    
    log_success "Prerequisites check passed"
}

# Deploy to inactive environment
deploy_inactive() {
    local target_color=$(get_target_color)
    local deployment_name="${SERVICE_NAME}-${target_color}"
    local image="${DOCKER_REGISTRY:-ghcr.io/over7-maker}/${IMAGE_NAME:-amas-orchestrator}:${IMAGE_TAG}"
    
    log_info "Deploying to ${target_color} environment: $deployment_name"
    
    # Check if deployment exists
    if kubectl get deployment "$deployment_name" -n "$NAMESPACE" &> /dev/null; then
        log_info "Updating existing deployment $deployment_name"
        kubectl set image deployment/"$deployment_name" \
            orchestrator="$image" \
            -n "$NAMESPACE"
    else
        log_info "Creating new deployment $deployment_name"
        
        # Create deployment from template (assuming blue deployment exists as template)
        if kubectl get deployment "$BLUE_DEPLOYMENT" -n "$NAMESPACE" -o yaml 2>/dev/null | \
           sed "s/${BLUE_DEPLOYMENT}/${deployment_name}/g" | \
           sed "s/app: ${SERVICE_NAME}-blue/app: ${SERVICE_NAME}-${target_color}/g" | \
           kubectl apply -f -; then
            log_success "Deployment $deployment_name created"
        else
            log_error "Failed to create deployment $deployment_name"
            log_info "Please ensure $BLUE_DEPLOYMENT exists as a template"
            exit 1
        fi
        
        # Update image
        kubectl set image deployment/"$deployment_name" \
            orchestrator="$image" \
            -n "$NAMESPACE"
    fi
    
    # Scale to desired replicas
    local replicas=$(kubectl get deployment "$BLUE_DEPLOYMENT" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "3")
    kubectl scale deployment "$deployment_name" --replicas="$replicas" -n "$NAMESPACE"
    
    log_success "Deployment $deployment_name updated with image $image"
}

# Wait for deployment to be ready
wait_for_deployment() {
    local deployment_name="$1"
    local timeout="${2:-$HEALTH_CHECK_TIMEOUT}"
    
    log_info "Waiting for deployment $deployment_name to be ready (timeout: ${timeout}s)..."
    
    if kubectl rollout status deployment/"$deployment_name" -n "$NAMESPACE" --timeout="${timeout}s"; then
        log_success "Deployment $deployment_name is ready"
        return 0
    else
        log_error "Deployment $deployment_name failed to become ready"
        return 1
    fi
}

# Health check for deployment
health_check() {
    local deployment_name="$1"
    local service_name="${SERVICE_NAME}-${2}"  # color
    
    log_info "Performing health check for $deployment_name..."
    
    # Check if pods are ready
    local ready_pods=$(kubectl get deployment "$deployment_name" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
    local desired_pods=$(kubectl get deployment "$deployment_name" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
    
    if [ "$ready_pods" != "$desired_pods" ] || [ "$ready_pods" = "0" ]; then
        log_error "Not all pods are ready ($ready_pods/$desired_pods)"
        return 1
    fi
    
    # Check service endpoint if available
    if kubectl get service "$service_name" -n "$NAMESPACE" &> /dev/null; then
        local service_url=$(kubectl get service "$service_name" -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")
        
        if [ -n "$service_url" ]; then
            log_info "Checking health endpoint at $service_url"
            if curl -f -s -m 10 "http://${service_url}/health/ready" > /dev/null 2>&1; then
                log_success "Health check passed"
                return 0
            else
                log_warning "Health endpoint check failed, but pods are ready"
            fi
        fi
    fi
    
    log_success "Health check passed (pods ready)"
    return 0
}

# Switch traffic to target color
switch_traffic() {
    local target_color=$(get_target_color)
    local target_service="${SERVICE_NAME}-${target_color}"
    local main_service="${SERVICE_NAME}"
    
    log_info "Switching traffic to ${target_color} environment..."
    
    # Update main service selector to point to target color
    if kubectl get service "$main_service" -n "$NAMESPACE" &> /dev/null; then
        # Patch service selector
        kubectl patch service "$main_service" -n "$NAMESPACE" -p "{\"spec\":{\"selector\":{\"app\":\"${SERVICE_NAME}-${target_color}\"}}}"
        log_success "Traffic switched to ${target_color} environment"
        
        # Update current color
        CURRENT_COLOR="$target_color"
        return 0
    else
        log_error "Main service $main_service not found"
        return 1
    fi
}

# Scale down inactive environment
scale_down_inactive() {
    local inactive_color=$(get_target_color)  # This will be the old active color
    local inactive_deployment="${SERVICE_NAME}-${inactive_color}"
    
    log_info "Scaling down inactive ${inactive_color} environment..."
    
    if kubectl scale deployment "$inactive_deployment" --replicas=0 -n "$NAMESPACE"; then
        log_success "Inactive environment scaled down"
        return 0
    else
        log_warning "Failed to scale down inactive environment (may not exist)"
        return 0  # Don't fail if it doesn't exist
    fi
}

# Rollback to previous color
rollback() {
    local previous_color=$(get_target_color)  # Opposite of current
    log_warning "Rolling back to ${previous_color} environment..."
    
    if switch_traffic; then
        log_success "Rollback completed"
        return 0
    else
        log_error "Rollback failed"
        return 1
    fi
}

# Main blue-green deployment flow
main() {
    local action="${1:-deploy}"  # deploy, switch, rollback
    
    log_info "Starting blue-green deployment operation: $action"
    log_info "Current active color: $CURRENT_COLOR"
    log_info "Image tag: $IMAGE_TAG"
    
    check_prerequisites
    
    case "$action" in
        deploy)
            local target_color=$(get_target_color)
            local target_deployment="${SERVICE_NAME}-${target_color}"
            
            # Deploy to inactive environment
            deploy_inactive
            
            # Wait for deployment to be ready
            if ! wait_for_deployment "$target_deployment"; then
                log_error "Deployment failed, aborting switch"
                exit 1
            fi
            
            # Health check
            if ! health_check "$target_deployment" "$target_color"; then
                log_error "Health check failed, aborting switch"
                exit 1
            fi
            
            # Switch traffic
            if switch_traffic; then
                log_success "Blue-green deployment completed successfully!"
                
                # Optionally scale down old environment after a grace period
                log_info "Waiting 60s before scaling down old environment..."
                sleep 60
                scale_down_inactive
            else
                log_error "Failed to switch traffic"
                exit 1
            fi
            ;;
        switch)
            # Just switch traffic (assumes both environments are ready)
            if switch_traffic; then
                log_success "Traffic switch completed"
            else
                log_error "Traffic switch failed"
                exit 1
            fi
            ;;
        rollback)
            rollback
            ;;
        *)
            log_error "Unknown action: $action"
            log_info "Usage: $0 [deploy|switch|rollback]"
            exit 1
            ;;
    esac
    
    log_info "Deployment summary:"
    kubectl get deployments -n "$NAMESPACE" -l "app=${SERVICE_NAME}" -o wide
    kubectl get services -n "$NAMESPACE" -l "app=${SERVICE_NAME}" -o wide
}

# Handle script interruption
trap 'log_error "Operation interrupted. Current state may be inconsistent."; exit 1' INT TERM

# Run main function
main "$@"
