# 🚀 AMAS Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Advanced Multi-Agent Intelligence System (AMAS) in various environments. Whether you're setting up a development instance or preparing for production deployment, this guide will walk you through each step.

**🚀 AI Agentic Workflows** - This deployment guide includes specific requirements and configuration for the revolutionary AI Agentic Workflow System with 4-layer architecture and 16 AI providers.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [AI Agentic Workflow Requirements](#ai-agentic-workflow-requirements)
3. [Deployment Options](#deployment-options)
4. [Quick Start Deployment](#quick-start-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Kubernetes Deployment](#kubernetes-deployment)
7. [Cloud Deployment](#cloud-deployment)
8. [On-Premises Deployment](#on-premises-deployment)
9. [Configuration](#configuration)
10. [Post-Deployment](#post-deployment)
11. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### System Requirements

#### Minimum Requirements
- **CPU**: 4 cores (2.4 GHz or higher)
- **RAM**: 8 GB
- **Storage**: 50 GB SSD
- **OS**: Ubuntu 20.04+, CentOS 8+, or Windows Server 2019+
- **Docker**: 20.10+ (for containerized deployment)
- **Python**: 3.11+ (for native deployment)

#### Recommended Requirements
- **CPU**: 8+ cores (3.0 GHz or higher)
- **RAM**: 16-32 GB
- **Storage**: 100+ GB SSD (NVMe preferred)
- **OS**: Ubuntu 22.04 LTS
- **Network**: 1 Gbps connection

### Software Prerequisites
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    docker.io \
    docker-compose \
    git \
    curl \
    wget \
    python3.11 \
    python3-pip \
    nodejs \
    npm \
    nginx \
    postgresql-14 \
    redis-server

# Install Docker Compose (if not included)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### API Keys Required
Ensure you have API keys for the AI providers you plan to use:
- DeepSeek API Key
- GLM API Key
- xAI Grok API Key
- Additional provider keys (see [Universal AI Manager Guide](../../UNIVERSAL_AI_MANAGER_GUIDE.md))

---

## 🚀 AI Agentic Workflow Requirements

### **Revolutionary AI Agentic Workflow System Requirements**

The AI Agentic Workflow System represents the most advanced workflow automation ever created, requiring specific infrastructure and configuration for optimal performance.

#### **Enhanced System Requirements for AI Agentic Workflows**

##### **Minimum Requirements for AI Agentic Workflows**
- **CPU**: 8 cores (3.0 GHz or higher) - Required for 4-layer AI agent processing
- **RAM**: 16 GB - Minimum for 16 AI providers and intelligent failover
- **Storage**: 100 GB SSD - For workflow data, AI model caching, and logs
- **Network**: 1 Gbps connection - For AI provider API calls and failover
- **OS**: Ubuntu 22.04 LTS or CentOS 8+ - Optimized for AI workloads

##### **Recommended Requirements for AI Agentic Workflows**
- **CPU**: 16+ cores (3.5 GHz or higher) - For maximum AI agent performance
- **RAM**: 32-64 GB - For concurrent workflow execution and AI model processing
- **Storage**: 500+ GB NVMe SSD - For high-speed AI model access and caching
- **Network**: 10 Gbps connection - For optimal AI provider communication
- **GPU**: NVIDIA RTX 4090 or A100 (optional) - For local AI model inference

#### **AI Provider API Requirements**

##### **Required API Keys for AI Agentic Workflows**
```bash
# Primary AI Providers (Required)
DEEPSEEK_API_KEY=your_deepseek_key
CLAUDE_API_KEY=your_claude_key
GPT4_API_KEY=your_gpt4_key
GLM_API_KEY=your_glm_key
GROK_API_KEY=your_grok_key

# Secondary AI Providers (Recommended)
KIMI_API_KEY=your_kimi_key
QWEN_API_KEY=your_qwen_key
GEMINI_API_KEY=your_gemini_key
GPTOSS_API_KEY=your_gptoss_key
GROQAI_API_KEY=your_groqai_key

# Additional AI Providers (Optional)
CEREBRAS_API_KEY=your_cerebras_key
GEMINIAI_API_KEY=your_geminiai_key
COHERE_API_KEY=your_cohere_key
NVIDIA_API_KEY=your_nvidia_key
CODESTRAL_API_KEY=your_codestral_key
GEMINI2_API_KEY=your_gemini2_key
GROQ2_API_KEY=your_groq2_key
CHUTES_API_KEY=your_chutes_key
```

##### **API Provider Configuration**
```yaml
# AI Provider Configuration
ai_providers:
  deepseek:
    priority: 1
    timeout: 30
    max_retries: 3
    rate_limit: 1000  # requests per hour
  claude:
    priority: 2
    timeout: 30
    max_retries: 3
    rate_limit: 500
  gpt4:
    priority: 3
    timeout: 30
    max_retries: 3
    rate_limit: 200
  # ... additional providers
```

#### **Workflow Infrastructure Requirements**

##### **GitHub Actions Requirements**
- **GitHub Repository**: With Actions enabled
- **GitHub Secrets**: All 16 AI provider API keys configured
- **Repository Permissions**: Write access for workflow execution
- **Actions Minutes**: Sufficient minutes for workflow execution
- **Concurrent Jobs**: At least 4 concurrent jobs for 4-layer architecture

##### **Workflow Storage Requirements**
```yaml
# Workflow Storage Configuration
workflow_storage:
  artifacts:
    retention_days: 30
    max_size: "1GB"
  logs:
    retention_days: 90
    max_size: "500MB"
  cache:
    enabled: true
    ttl: 3600  # 1 hour
    max_size: "2GB"
```

#### **Network Requirements for AI Agentic Workflows**

##### **Outbound Network Access**
```bash
# Required outbound connections for AI providers
# DeepSeek API
curl -I https://api.deepseek.com

# Claude API
curl -I https://api.anthropic.com

# OpenAI API
curl -I https://api.openai.com

# Google AI API
curl -I https://generativelanguage.googleapis.com

# Additional AI provider endpoints
# ... (all 16 AI providers)
```

##### **Firewall Configuration**
```bash
# Allow outbound HTTPS connections
sudo ufw allow out 443/tcp

# Allow outbound HTTP connections (if needed)
sudo ufw allow out 80/tcp

# Allow GitHub API access
sudo ufw allow out to api.github.com port 443

# Allow webhook endpoints (if using)
sudo ufw allow in 8080/tcp
```

#### **Security Requirements for AI Agentic Workflows**

##### **API Key Security**
```bash
# Secure API key storage
chmod 600 /etc/amas/api-keys.env
chown amas:amas /etc/amas/api-keys.env

# Encrypt API keys at rest
gpg --symmetric --cipher-algo AES256 api-keys.env

# Use environment variables
export $(cat /etc/amas/api-keys.env | xargs)
```

##### **Workflow Security Configuration**
```yaml
# Workflow Security Settings
workflow_security:
  api_key_rotation:
    enabled: true
    rotation_interval: "30d"
  audit_logging:
    enabled: true
    log_level: "info"
  access_control:
    enabled: true
    allowed_ips: ["10.0.0.0/8", "192.168.0.0/16"]
  encryption:
    enabled: true
    algorithm: "AES-256-GCM"
```

#### **Performance Requirements for AI Agentic Workflows**

##### **Resource Limits**
```yaml
# Resource Limits for AI Workflows
resource_limits:
  orchestrator:
    cpu: "2000m"
    memory: "4Gi"
    timeout: "30m"
  self_improver:
    cpu: "1000m"
    memory: "2Gi"
    timeout: "45m"
  issue_responder:
    cpu: "500m"
    memory: "1Gi"
    timeout: "15m"
```

##### **Scaling Configuration**
```yaml
# Auto-scaling Configuration
autoscaling:
  enabled: true
  min_replicas: 2
  max_replicas: 10
  target_cpu_utilization: 70
  target_memory_utilization: 80
  scale_up_stabilization: "2m"
  scale_down_stabilization: "5m"
```

---

## 🎯 Deployment Options

### Deployment Comparison

| Feature | Docker | Kubernetes | Cloud | On-Premises |
|---------|---------|------------|-------|-------------|
| **Ease of Setup** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Scalability** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **High Availability** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Cost** | Low | Medium | Variable | High |
| **Maintenance** | Low | Medium | Low | High |
| **Best For** | Dev/Small | Enterprise | SaaS | Security-Critical |

---

## 🚀 Quick Start Deployment

The fastest way to get AMAS running:

```bash
# Clone the repository
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System

# Copy and configure environment
cp .env.example .env
nano .env  # Add your API keys

# Start with Docker Compose
docker-compose up -d

# Verify deployment
docker-compose ps
curl http://localhost:8000/api/v1/health
```

---

## 🐳 Docker Deployment

### Standard Docker Deployment

#### 1. Prepare Environment
```bash
# Create deployment directory
mkdir -p /opt/amas
cd /opt/amas

# Clone repository
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git .

# Create environment file
cp .env.example .env
```

#### 2. Configure Environment
Edit `.env` file with your settings:
```bash
# Core Configuration
AMAS_ENV=production
AMAS_DEBUG=false
AMAS_LOG_LEVEL=info

# API Keys (add all that you have)
DEEPSEEK_API_KEY=your_key_here
GLM_API_KEY=your_key_here
GROK_API_KEY=your_key_here
# ... add other provider keys

# Database Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=amas
POSTGRES_USER=amas
POSTGRES_PASSWORD=secure_password_here

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=secure_redis_password

# Security
SECRET_KEY=generate_secure_secret_key_here
API_KEY=generate_secure_api_key_here
```

#### 3. Build and Start Services
```bash
# Build custom images
docker-compose build

# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

#### 4. Verify Deployment
```bash
# Check health endpoint
curl http://localhost:8000/api/v1/health

# Test API access
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/system/info

# Access web interface
open http://localhost:3000
```

### Docker Swarm Deployment

For high availability with Docker:

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml amas

# Scale services
docker service scale amas_api=3
docker service scale amas_worker=5

# Monitor services
docker service ls
docker stack ps amas
```

---

## ☸️ Kubernetes Deployment

### Kubernetes Setup

#### 1. Prepare Kubernetes Manifests
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: amas
---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: amas-config
  namespace: amas
data:
  AMAS_ENV: "production"
  AMAS_LOG_LEVEL: "info"
  POSTGRES_HOST: "postgres-service"
  REDIS_HOST: "redis-service"
---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: amas-secrets
  namespace: amas
type: Opaque
stringData:
  DEEPSEEK_API_KEY: "your_key_here"
  GLM_API_KEY: "your_key_here"
  POSTGRES_PASSWORD: "secure_password"
  REDIS_PASSWORD: "secure_password"
  SECRET_KEY: "secure_secret_key"
```

#### 2. Deploy Core Services
```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy configs and secrets
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Deploy database
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml

# Deploy AMAS services
kubectl apply -f k8s/amas-deployment.yaml
kubectl apply -f k8s/amas-service.yaml

# Deploy ingress
kubectl apply -f k8s/ingress.yaml
```

#### 3. Helm Chart Deployment
```bash
# Add AMAS helm repository
helm repo add amas https://charts.amas.ai
helm repo update

# Install with custom values
helm install amas amas/amas \
  --namespace amas \
  --create-namespace \
  --values values.yaml
```

#### 4. Monitor Deployment
```bash
# Check pod status
kubectl get pods -n amas

# View logs
kubectl logs -n amas -l app=amas-api -f

# Check services
kubectl get svc -n amas

# Get ingress
kubectl get ingress -n amas
```

---

## ☁️ Cloud Deployment

### AWS Deployment

#### 1. Using AWS ECS
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name amas-cluster

# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service
aws ecs create-service \
  --cluster amas-cluster \
  --service-name amas-service \
  --task-definition amas:1 \
  --desired-count 3 \
  --launch-type FARGATE
```

#### 2. Using AWS EKS
```bash
# Create EKS cluster
eksctl create cluster \
  --name amas-cluster \
  --version 1.28 \
  --region us-east-1 \
  --nodegroup-name amas-nodes \
  --node-type t3.large \
  --nodes 3

# Deploy AMAS
kubectl apply -f k8s/
```

### Google Cloud Platform

#### Using GKE
```bash
# Create GKE cluster
gcloud container clusters create amas-cluster \
  --num-nodes=3 \
  --machine-type=n1-standard-2 \
  --region=us-central1

# Get credentials
gcloud container clusters get-credentials amas-cluster

# Deploy AMAS
kubectl apply -f k8s/
```

### Azure Deployment

#### Using AKS
```bash
# Create resource group
az group create --name amas-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group amas-rg \
  --name amas-cluster \
  --node-count 3 \
  --enable-addons monitoring

# Get credentials
az aks get-credentials --resource-group amas-rg --name amas-cluster

# Deploy AMAS
kubectl apply -f k8s/
```

---

## 🏢 On-Premises Deployment

### Bare Metal Installation

#### 1. System Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
  python3.11 \
  python3.11-venv \
  postgresql-14 \
  redis-server \
  nginx \
  supervisor

# Create application user
sudo useradd -m -s /bin/bash amas
sudo usermod -aG sudo amas
```

#### 2. Database Setup
```bash
# PostgreSQL setup
sudo -u postgres psql <<EOF
CREATE USER amas WITH PASSWORD 'secure_password';
CREATE DATABASE amas OWNER amas;
GRANT ALL PRIVILEGES ON DATABASE amas TO amas;
EOF

# Redis setup
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

#### 3. Application Installation
```bash
# Switch to amas user
sudo su - amas

# Clone repository
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git ~/amas
cd ~/amas

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

#### 4. Service Configuration
```bash
# Create systemd service
sudo tee /etc/systemd/system/amas.service <<EOF
[Unit]
Description=AMAS Service
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=amas
WorkingDirectory=/home/amas/amas
Environment="PATH=/home/amas/amas/venv/bin"
ExecStart=/home/amas/amas/venv/bin/python -m src.amas.main
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable amas
sudo systemctl start amas
```

#### 5. Nginx Configuration
```nginx
# /etc/nginx/sites-available/amas
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## ⚙️ Configuration

### Environment Variables

#### Core Settings
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AMAS_ENV` | Environment (development/production) | development | Yes |
| `AMAS_DEBUG` | Debug mode | false | No |
| `AMAS_LOG_LEVEL` | Logging level | info | No |
| `SECRET_KEY` | Application secret key | - | Yes |
| `API_KEY` | Default API key | - | Yes |

#### Database Settings
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `POSTGRES_HOST` | PostgreSQL host | localhost | Yes |
| `POSTGRES_PORT` | PostgreSQL port | 5432 | No |
| `POSTGRES_DB` | Database name | amas | Yes |
| `POSTGRES_USER` | Database user | amas | Yes |
| `POSTGRES_PASSWORD` | Database password | - | Yes |

#### Redis Settings
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REDIS_HOST` | Redis host | localhost | Yes |
| `REDIS_PORT` | Redis port | 6379 | No |
| `REDIS_PASSWORD` | Redis password | - | No |
| `REDIS_DB` | Redis database | 0 | No |

#### AI Provider Settings
Configure API keys for each provider you want to use:
```bash
DEEPSEEK_API_KEY=your_key
GLM_API_KEY=your_key
GROK_API_KEY=your_key
KIMI_API_KEY=your_key
QWEN_API_KEY=your_key
# ... additional providers
```

### Configuration Files

#### 1. Main Configuration (`config/config.yaml`)
```yaml
amas:
  version: "1.1.0"
  environment: production
  
server:
  host: 0.0.0.0
  port: 8000
  workers: 4
  
database:
  pool_size: 20
  max_overflow: 40
  pool_timeout: 30
  
redis:
  pool_size: 10
  decode_responses: true
  
monitoring:
  enabled: true
  prometheus_port: 9090
  grafana_port: 3000
```

#### 2. Agent Configuration (`config/agents.yaml`)
```yaml
agents:
  osint:
    enabled: true
    max_concurrent: 5
    timeout: 300
    
  security:
    enabled: true
    max_concurrent: 3
    timeout: 600
    
  analysis:
    enabled: true
    max_concurrent: 10
    timeout: 300
```

---

## 🔍 Post-Deployment

### 1. Health Checks
```bash
# API health check
curl http://your-domain.com/api/v1/health

# Database connectivity
docker exec amas_postgres psql -U amas -c "SELECT 1"

# Redis connectivity
docker exec amas_redis redis-cli ping

# Agent status
curl -H "X-API-Key: your-key" http://your-domain.com/api/v1/agents
```

### 2. Initial Configuration
```bash
# Create admin user
docker exec amas_api python -m src.amas.cli create-admin \
  --username admin \
  --email admin@example.com

# Generate API keys
docker exec amas_api python -m src.amas.cli generate-api-key \
  --name "Production App"

# Initialize database
docker exec amas_api python -m src.amas.cli db upgrade
```

### 3. Security Hardening
```bash
# Set up firewall rules
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Configure SSL/TLS
sudo certbot --nginx -d your-domain.com

# Set up fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

### 4. Monitoring Setup
```bash
# Access Grafana
open http://your-domain.com:3000
# Default credentials: admin/admin

# Import AMAS dashboards
# Navigate to Dashboards > Import
# Upload JSON files from monitoring/dashboards/

# Configure alerts
# Navigate to Alerting > Alert rules
# Configure based on your requirements
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check logs
docker-compose logs api
journalctl -u amas -f

# Common causes:
# - Missing environment variables
# - Database connection issues
# - Port conflicts
```

#### 2. Database Connection Failed
```bash
# Test connection
psql -h localhost -U amas -d amas

# Check PostgreSQL status
sudo systemctl status postgresql

# Verify credentials in .env
```

#### 3. API Key Issues
```bash
# Regenerate API key
docker exec amas_api python -m src.amas.cli generate-api-key

# Check key in headers
curl -H "X-API-Key: your-key" http://localhost:8000/api/v1/health
```

#### 4. Performance Issues
```bash
# Check resource usage
docker stats
htop

# Scale services
docker-compose scale worker=5

# Optimize database
docker exec amas_postgres vacuumdb -U amas -d amas -z
```

### Debug Mode
Enable debug mode for troubleshooting:
```bash
# Set in .env
AMAS_DEBUG=true
AMAS_LOG_LEVEL=debug

# Restart services
docker-compose restart
```

### Support Resources
- [GitHub Issues](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues)
- [Documentation](../README.md)
- [Community Discord](https://discord.gg/amas)

---

## 📚 Next Steps

1. Review [Production Deployment Guide](PRODUCTION_DEPLOYMENT.md) for production-specific configurations
2. Set up [Monitoring and Alerting](../monitoring/README.md)
3. Configure [Backup and Recovery](../operations/BACKUP_RECOVERY.md)
4. Implement [Security Best Practices](../security/SECURITY.md)
5. Explore [API Documentation](../api/README.md)

---

**Last Updated**: January 2025  
**Version**: 1.1.0  
**Status**: Production Ready