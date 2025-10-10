#!/bin/bash
# AMAS Kubernetes Deployment Script
# Implements RD-080: Create scaling documentation and procedures

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="amas"
IMAGE_NAME="amas"
IMAGE_TAG="latest"
REPLICAS=2
MIN_REPLICAS=2
MAX_REPLICAS=10

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

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    # Check if cluster is accessible
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    fi
    
    # Check if namespace exists
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        log_info "Creating namespace $NAMESPACE..."
        kubectl create namespace $NAMESPACE
    fi
    
    log_success "Prerequisites check passed"
}

build_image() {
    log_info "Building Docker image..."
    
    if [ -f "Dockerfile" ]; then
        docker build -t $IMAGE_NAME:$IMAGE_TAG .
        log_success "Docker image built successfully"
    else
        log_warning "Dockerfile not found. Skipping image build."
    fi
}

deploy_database() {
    log_info "Deploying database services..."
    
    # Deploy PostgreSQL
    kubectl apply -f postgres.yaml
    log_info "Waiting for PostgreSQL to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/postgres -n $NAMESPACE
    
    # Deploy Redis
    kubectl apply -f redis.yaml
    log_info "Waiting for Redis to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/redis -n $NAMESPACE
    
    # Deploy Neo4j
    kubectl apply -f neo4j.yaml
    log_info "Waiting for Neo4j to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/neo4j -n $NAMESPACE
    
    log_success "Database services deployed"
}

deploy_application() {
    log_info "Deploying AMAS application..."
    
    # Update image tag in deployment
    sed -i "s|image: amas:latest|image: $IMAGE_NAME:$IMAGE_TAG|g" amas-deployment.yaml
    
    # Deploy application
    kubectl apply -f amas-deployment.yaml
    log_info "Waiting for AMAS application to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/amas -n $NAMESPACE
    
    log_success "AMAS application deployed"
}

deploy_monitoring() {
    log_info "Deploying monitoring services..."
    
    # Deploy Prometheus
    kubectl apply -f monitoring.yaml
    log_info "Waiting for Prometheus to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/prometheus -n $NAMESPACE
    
    # Deploy Grafana
    log_info "Waiting for Grafana to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/grafana -n $NAMESPACE
    
    log_success "Monitoring services deployed"
}

deploy_autoscaling() {
    log_info "Deploying autoscaling configuration..."
    
    # Deploy HPA
    kubectl apply -f hpa.yaml
    
    log_success "Autoscaling configuration deployed"
}

deploy_ingress() {
    log_info "Deploying ingress configuration..."
    
    # Deploy ingress
    kubectl apply -f ingress.yaml
    
    log_success "Ingress configuration deployed"
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check all deployments
    kubectl get deployments -n $NAMESPACE
    
    # Check all services
    kubectl get services -n $NAMESPACE
    
    # Check HPA
    kubectl get hpa -n $NAMESPACE
    
    # Check pods
    kubectl get pods -n $NAMESPACE
    
    log_success "Deployment verification completed"
}

show_access_info() {
    log_info "Deployment completed! Access information:"
    echo ""
    echo "Services:"
    kubectl get services -n $NAMESPACE
    echo ""
    echo "To access the application:"
    echo "1. Port forward: kubectl port-forward service/amas 8000:8000 -n $NAMESPACE"
    echo "2. Open browser: http://localhost:8000"
    echo ""
    echo "To access monitoring:"
    echo "1. Prometheus: kubectl port-forward service/prometheus 9090:9090 -n $NAMESPACE"
    echo "2. Grafana: kubectl port-forward service/grafana 3000:3000 -n $NAMESPACE"
    echo ""
    echo "To check logs:"
    echo "kubectl logs -f deployment/amas -n $NAMESPACE"
    echo ""
    echo "To scale the application:"
    echo "kubectl scale deployment amas --replicas=$REPLICAS -n $NAMESPACE"
}

cleanup() {
    log_info "Cleaning up deployment..."
    
    kubectl delete namespace $NAMESPACE --ignore-not-found=true
    
    log_success "Cleanup completed"
}

# Main script
case "${1:-deploy}" in
    "deploy")
        check_prerequisites
        build_image
        deploy_database
        deploy_application
        deploy_monitoring
        deploy_autoscaling
        deploy_ingress
        verify_deployment
        show_access_info
        ;;
    "cleanup")
        cleanup
        ;;
    "status")
        verify_deployment
        ;;
    "scale")
        if [ -z "$2" ]; then
            log_error "Please specify number of replicas: $0 scale 5"
            exit 1
        fi
        kubectl scale deployment amas --replicas=$2 -n $NAMESPACE
        log_success "Scaled to $2 replicas"
        ;;
    "logs")
        kubectl logs -f deployment/amas -n $NAMESPACE
        ;;
    *)
        echo "Usage: $0 {deploy|cleanup|status|scale|logs}"
        echo "  deploy  - Deploy AMAS to Kubernetes (default)"
        echo "  cleanup - Remove AMAS from Kubernetes"
        echo "  status  - Show deployment status"
        echo "  scale   - Scale application (e.g., $0 scale 5)"
        echo "  logs    - Show application logs"
        exit 1
        ;;
esac