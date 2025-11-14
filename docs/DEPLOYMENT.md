# 🚀 AMAS Production Deployment Guide

## 📋 **Prerequisites**

- **Docker & Docker Compose** (recommended)
- **Python 3.11+** (if running directly)
- **Node.js 18+** (for React dashboard)
- **PostgreSQL 15+** (or use Docker)
- **Redis 7+** (or use Docker)
- **Neo4j 5+** (or use Docker)

## 🐳 **Docker Deployment (Recommended)**

### **1. Quick Start with Docker Compose**

```bash
# Clone the repository
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
nano .env

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### **2. Access Services**

- **AMAS API**: http://localhost:8000
- **React Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/api/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Neo4j Browser**: http://localhost:7474

### **3. Monitor Logs**

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f amas
docker-compose logs -f postgres
docker-compose logs -f redis
```

## 🐍 **Direct Python Deployment**

### **1. System Setup**

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-pip postgresql redis-server

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### **2. Database Setup**

```bash
# PostgreSQL
sudo -u postgres createdb amas
sudo -u postgres createuser amas_user
sudo -u postgres psql -c "ALTER USER amas_user PASSWORD 'amas_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE amas TO amas_user;"

# Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Neo4j
wget https://dist.neo4j.org/neo4j-community-5.15.0-unix.tar.gz
tar -xzf neo4j-community-5.15.0-unix.tar.gz
cd neo4j-community-5.15.0
./bin/neo4j start
```

### **3. AMAS Installation**

```bash
# Clone and setup
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System

# Run setup script
python3 setup.py

# Configure environment
cp .env.example .env
nano .env  # Add your API keys

# Validate setup
python3 scripts/validate_env.py

# Start AMAS
python3 -m amas
```

### **4. React Dashboard Setup**

```bash
# Install dependencies
cd web
npm install

# Build for production
npm run build

# Start development server
npm start
```

## ☁️ **Cloud Deployment**

### **AWS Deployment**

```bash
# Using AWS CLI
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --instance-type t3.large \
  --key-name your-key-pair \
  --security-groups amas-sg \
  --user-data file://user-data.sh
```

### **Google Cloud Platform**

```bash
# Using gcloud CLI
gcloud compute instances create amas-server \
  --image-family ubuntu-2004-lts \
  --image-project ubuntu-os-cloud \
  --machine-type e2-standard-2 \
  --tags amas-server
```

### **Azure Deployment**

```bash
# Using Azure CLI
az vm create \
  --resource-group amas-rg \
  --name amas-server \
  --image UbuntuLTS \
  --size Standard_B2s \
  --admin-username azureuser
```

## 🔧 **Configuration**

### **Environment Variables**

```bash
# Required API Keys (at least 2-3)
OPENAI_API_KEY=your_openai_key
GEMINIAI_API_KEY=your_gemini_key
GROQAI_API_KEY=your_groq_key

# Optional for redundancy
COHERE_API_KEY=your_cohere_key
ANTHROPIC_API_KEY=your_anthropic_key
HUGGINGFACE_API_KEY=your_huggingface_key

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/amas
REDIS_URL=redis://localhost:6379/0
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Security
JWT_SECRET=your_jwt_secret
ENCRYPTION_KEY=your_encryption_key

# Performance
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30
CACHE_TTL=3600
```

### **Nginx Configuration**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /dashboard {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 **Monitoring & Maintenance**

### **Health Checks**

```bash
# API Health
curl http://localhost:8000/health

# System Status
curl http://localhost:8000/api/status

# Provider Status
curl http://localhost:8000/api/providers
```

### **Log Monitoring**

```bash
# View logs
tail -f logs/amas.log

# Monitor with journalctl (systemd)
journalctl -u amas -f

# Docker logs
docker-compose logs -f amas
```

### **Performance Monitoring**

```bash
# Run performance tests
python3 tests/load/amas_load_test.py

# Monitor system resources
python3 monitor-intelligence.py

# Check database performance
psql -d amas -c "SELECT * FROM pg_stat_activity;"
```

## 🔒 **Security Considerations**

### **1. API Key Security**

- Store API keys in environment variables
- Use secrets management (AWS Secrets Manager, Azure Key Vault)
- Never commit keys to version control
- Rotate keys regularly

### **2. Network Security**

- Use HTTPS in production
- Configure firewall rules
- Use VPN for internal access
- Enable rate limiting

### **3. Data Security**

- Encrypt sensitive data at rest
- Use secure database connections
- Implement audit logging
- Regular security scans

## 🚀 **Scaling**

### **Horizontal Scaling**

```yaml
# docker-compose.yml
services:
  amas:
    deploy:
      replicas: 3
    environment:
      - AMAS_INSTANCE_ID=${HOSTNAME}
```

### **Load Balancing**

```nginx
upstream amas_backend {
    server amas1:8000;
    server amas2:8000;
    server amas3:8000;
}

server {
    location / {
        proxy_pass http://amas_backend;
    }
}
```

### **Database Scaling**

- Use read replicas for PostgreSQL
- Implement Redis clustering
- Configure Neo4j clustering
- Use connection pooling

## 🆘 **Troubleshooting**

### **Common Issues**

1. **API Keys Not Working**
   ```bash
   python3 scripts/validate_env.py
   ```

2. **Database Connection Issues**
   ```bash
   # Check PostgreSQL
   sudo systemctl status postgresql
   
   # Check Redis
   redis-cli ping
   
   # Check Neo4j
   curl http://localhost:7474
   ```

3. **Memory Issues**
   ```bash
   # Check memory usage
   free -h
   
   # Check process memory
   ps aux --sort=-%mem | head
   ```

4. **Performance Issues**
   ```bash
   # Run load tests
   python3 tests/load/amas_load_test.py
   
   # Check system resources
   htop
   ```

### **Log Analysis**

```bash
# Search for errors
grep -i error logs/amas.log

# Search for warnings
grep -i warning logs/amas.log

# Monitor real-time
tail -f logs/amas.log | grep -i error
```

## 📈 **Performance Optimization**

### **1. Database Optimization**

- Create appropriate indexes
- Use connection pooling
- Optimize queries
- Regular maintenance

### **2. Caching**

- Enable Redis caching
- Use CDN for static assets
- Implement application-level caching
- Cache API responses

### **3. Resource Optimization**

- Tune JVM settings (if using Java components)
- Optimize Python memory usage
- Use async processing
- Implement queue management

## 🚀 **Progressive Delivery Pipeline**

AMAS includes a comprehensive Progressive Delivery Pipeline using Argo Rollouts for safe, automated deployments with canary releases and automatic rollback.

### **Overview**

The Progressive Delivery Pipeline provides:
- **Canary Deployments**: Progressive traffic shifting (10%→25%→50%→75%→100%)
- **Automatic Rollback**: SLO violations trigger immediate rollback within 2 minutes
- **Zero Downtime**: No service interruption during deployments
- **SLO-based Gates**: Health checks and metrics validation prevent bad deployments
- **Blue-Green Capability**: Instant traffic switching for emergency scenarios

### **Prerequisites**

- Kubernetes cluster with Argo Rollouts controller installed
- NGINX Ingress Controller for traffic routing
- Prometheus for metrics-based analysis
- kubectl and Argo Rollouts CLI configured

### **Quick Start**

```bash
# Install Argo Rollouts
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

# Apply analysis templates (required first)
kubectl apply -f k8s/argo-rollouts/analysis-templates.yaml

# Apply rollout configuration
kubectl apply -f k8s/argo-rollouts/rollout.yaml

# Deploy using canary script
export NAMESPACE=amas-prod
export ROLLOUT_NAME=amas-orchestrator
export IMAGE_TAG=latest
./scripts/deployment/canary_deploy.sh
```

### **Deployment Strategy**

The canary deployment follows this progressive timeline:

1. **10% Traffic** (1min) → Basic health checks
2. **25% Traffic** (1min + 1min analysis) → Success rate validation
3. **50% Traffic** (2min + 2min analysis) → Comprehensive SLO checks
4. **75% Traffic** (2min + 2min analysis) → Performance regression detection
5. **Final Validation** (1min + 1min analysis) → Final checks
6. **100% Traffic** → Full deployment

**Total Time: ~8-9 minutes** (meets <10 minute requirement)

### **Automatic Rollback Triggers**

Rollback is triggered automatically when:
- Success rate drops below 95%
- P95 latency exceeds 3.0 seconds
- Error budget remaining falls below 5%
- Health checks fail for >2 minutes

### **Monitoring Deployments**

```bash
# View rollout status
kubectl argo rollouts get rollout amas-orchestrator -n amas-prod

# Watch rollout in real-time
kubectl argo rollouts get rollout amas-orchestrator -n amas-prod --watch

# View analysis runs
kubectl get analysisruns -n amas-prod
```

### **Manual Rollback**

```bash
# Rollback to previous revision
kubectl rollout undo rollout/amas-orchestrator -n amas-prod

# Rollback to specific revision
kubectl rollout undo rollout/amas-orchestrator --to-revision=2 -n amas-prod

# Abort current rollout
kubectl argo rollouts abort amas-orchestrator -n amas-prod
```

### **Documentation**

For detailed information, see:
- [Progressive Delivery Quick Start Guide](PROGRESSIVE_DELIVERY_QUICK_START.md)
- [Progressive Delivery Implementation Guide](PROGRESSIVE_DELIVERY_IMPLEMENTATION.md)
- [Progressive Delivery Success Criteria](PROGRESSIVE_DELIVERY_SUCCESS_CRITERIA.md)

## 🎯 **Production Checklist**

- [ ] All API keys configured and validated
- [ ] Database connections working
- [ ] Security scanning passed
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Team trained on operations
- [ ] Progressive Delivery Pipeline configured (Kubernetes deployments)
- [ ] Argo Rollouts installed and tested
- [ ] Prometheus metrics integration verified

---

**🎉 Your AMAS system is now production-ready!**

For support, check the [troubleshooting guide](docs/troubleshooting.md) or open an issue on GitHub.