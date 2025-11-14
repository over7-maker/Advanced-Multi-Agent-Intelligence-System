#!/bin/bash
# Deploy Orchestration System
# This script deploys the Hierarchical Agent Orchestration System to Kubernetes

set -e

NAMESPACE="${NAMESPACE:-amas}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "🚀 Deploying Hierarchical Agent Orchestration System"
echo "Namespace: $NAMESPACE"
echo "Image Tag: $IMAGE_TAG"
echo ""

# Check if namespace exists
if ! kubectl get namespace "$NAMESPACE" &>/dev/null; then
    echo "📦 Creating namespace $NAMESPACE..."
    kubectl create namespace "$NAMESPACE"
fi

# Check if secrets exist
if ! kubectl get secret amas-secrets -n "$NAMESPACE" &>/dev/null; then
    echo "⚠️  Warning: amas-secrets not found. Please create secrets first:"
    echo "   kubectl create secret generic amas-secrets \\"
    echo "     --from-literal=POSTGRES_PASSWORD='your-password' \\"
    echo "     --from-literal=REDIS_PASSWORD='your-password' \\"
    echo "     --from-literal=NEO4J_PASSWORD='your-password' \\"
    echo "     --from-literal=SECRET_KEY='your-secret-key' \\"
    echo "     -n $NAMESPACE"
    exit 1
fi

# Wait for foundation services
echo "⏳ Waiting for foundation services..."
if ! kubectl wait --for=condition=ready pod -l app=postgres -n "$NAMESPACE" --timeout=300s 2>/dev/null; then
    echo "⚠️  Warning: PostgreSQL not ready. Continuing anyway..."
fi

if ! kubectl wait --for=condition=ready pod -l app=redis -n "$NAMESPACE" --timeout=300s 2>/dev/null; then
    echo "⚠️  Warning: Redis not ready. Continuing anyway..."
fi

if ! kubectl wait --for=condition=ready pod -l app=neo4j -n "$NAMESPACE" --timeout=300s 2>/dev/null; then
    echo "⚠️  Warning: Neo4j not ready. Continuing anyway..."
fi

# Deploy configuration
echo "📝 Deploying orchestration configuration..."
kubectl apply -f k8s/orchestration-configmap.yaml

# Replace IMAGE_TAG in deployment
echo "🐳 Deploying orchestration service (image tag: $IMAGE_TAG)..."
sed "s/\${IMAGE_TAG}/$IMAGE_TAG/g" k8s/orchestration-deployment.yaml | kubectl apply -f -

# Deploy HPA
echo "📈 Deploying autoscaling configuration..."
kubectl apply -f k8s/orchestration-hpa.yaml

# Wait for deployment
echo "⏳ Waiting for orchestration pods to be ready..."
kubectl wait --for=condition=available deployment/amas-orchestration -n "$NAMESPACE" --timeout=600s || {
    echo "❌ Deployment failed. Checking pod status..."
    kubectl get pods -l component=orchestration -n "$NAMESPACE"
    kubectl logs -l component=orchestration -n "$NAMESPACE" --tail=50
    exit 1
}

# Verify deployment
echo "✅ Deployment complete!"
echo ""
echo "📊 Deployment Status:"
kubectl get pods -l component=orchestration -n "$NAMESPACE"
echo ""
echo "🔍 Service Endpoints:"
kubectl get svc amas-orchestration -n "$NAMESPACE"
echo ""
echo "📈 Autoscaling Status:"
kubectl get hpa amas-orchestration-hpa -n "$NAMESPACE"
echo ""
echo "🏥 Health Check:"
kubectl exec -n "$NAMESPACE" deployment/amas-orchestration -- \
    curl -s http://localhost:8000/health/orchestration || echo "⚠️  Health check endpoint not yet available"
echo ""
echo "✨ Orchestration system deployed successfully!"
echo ""
echo "📚 Next steps:"
echo "   1. Monitor metrics: kubectl port-forward svc/amas-orchestration 9090:9090 -n $NAMESPACE"
echo "   2. View logs: kubectl logs -l component=orchestration -n $NAMESPACE -f"
echo "   3. Check documentation: docs/deployment/ORCHESTRATION_DEPLOYMENT.md"
