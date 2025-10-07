# 📦 AMAS Installation Guide

> Step-by-step installation instructions for the Advanced Multi-Agent Intelligence System

## 🚀 Quick Start (Docker)

The fastest way to get AMAS running is with Docker:

```bash
# Clone the repository
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System

# Copy environment template
cp .env.example .env

# Edit .env with your API keys (optional)
nano .env

# Start AMAS
docker-compose up -d

# Verify installation
docker-compose ps
```

Access AMAS at:
- 🌐 Web Dashboard: http://localhost:3000
- 📡 API: http://localhost:8000
- 📊 Monitoring: http://localhost:3001

## 🐍 Python Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+
- Redis 7+
- Node.js 18+ (for web dashboard)
- Git

### Step 1: System Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip \
    postgresql postgresql-contrib redis-server \
    nodejs npm git build-essential
```

#### macOS
```bash
brew install python@3.11 postgresql@15 redis node git
brew services start postgresql@15
brew services start redis
```

#### Windows
```powershell
# Install Python from python.org
# Install PostgreSQL from postgresql.org
# Install Redis from github.com/microsoftarchive/redis/releases
# Install Node.js from nodejs.org
```

### Step 2: Clone Repository

```bash
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System
```

### Step 3: Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-monitoring.txt
```

### Step 4: Database Setup

```bash
# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE amas;
CREATE USER amas_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE amas TO amas_user;
\q
```

```bash
# Run migrations
python scripts/setup_database.py
```

### Step 5: Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

Required configurations:
```env
# Database
DATABASE_URL=postgresql://amas_user:secure_password@localhost:5432/amas

# Redis
REDIS_URL=redis://localhost:6379

# API Keys (at least one recommended)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
# Add more as needed

# Security
JWT_SECRET=$(openssl rand -base64 32)
ENCRYPTION_KEY=$(openssl rand -base64 32)
```

### Step 6: Web Dashboard Setup

```bash
cd web
npm install
npm run build
cd ..
```

### Step 7: Start Services

```bash
# Start API server
python -m amas.api.server &

# Start monitoring
python monitor-intelligence.py &

# Start web dashboard
cd web && npm start &
```

## 🐳 Docker Compose Options

### Development Mode
```bash
docker-compose -f docker-compose.dev.yml up
```

### Production Mode
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### With Monitoring
```bash
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

## ☸️ Kubernetes Installation

### Prerequisites
- Kubernetes cluster (1.24+)
- kubectl configured
- Helm 3+

### Installation Steps

```bash
# Add AMAS Helm repository
helm repo add amas https://charts.amas.ai
helm repo update

# Install AMAS
helm install amas amas/amas \
  --namespace amas \
  --create-namespace \
  --values values.yaml
```

Example `values.yaml`:
```yaml
replicaCount: 3

image:
  repository: amas/platform
  tag: latest
  pullPolicy: IfNotPresent

ingress:
  enabled: true
  hostname: amas.example.com
  tls: true

postgresql:
  enabled: true
  auth:
    database: amas
    username: amas_user

redis:
  enabled: true
  auth:
    enabled: true

monitoring:
  enabled: true
  prometheus:
    enabled: true
  grafana:
    enabled: true
```

## ☁️ Cloud Deployments

### AWS
```bash
# Using CloudFormation
aws cloudformation create-stack \
  --stack-name amas \
  --template-body file://aws/template.yaml \
  --parameters file://aws/parameters.json \
  --capabilities CAPABILITY_IAM
```

### Azure
```bash
# Using ARM template
az group create --name amas-rg --location eastus
az deployment group create \
  --resource-group amas-rg \
  --template-file azure/template.json \
  --parameters @azure/parameters.json
```

### Google Cloud
```bash
# Using Terraform
cd terraform/gcp
terraform init
terraform plan -var-file="prod.tfvars"
terraform apply -var-file="prod.tfvars"
```

## ✅ Post-Installation

### 1. Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Check agent status
curl http://localhost:8000/api/agents/status

# Run test task
python examples/basic_usage.py
```

### 2. Initial Configuration

```bash
# Configure agents
python scripts/configure_agents.py

# Set up monitoring alerts
python scripts/setup_alerts.py

# Initialize collective intelligence
python scripts/setup_collective_intelligence.py
```

### 3. Security Hardening

```bash
# Generate secure keys
python scripts/generate_keys.py

# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Set up SSL
certbot certonly --standalone -d your-domain.com
```

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U amas_user -d amas
```

#### Redis Connection Error
```bash
# Check Redis status
sudo systemctl status redis

# Test connection
redis-cli ping
```

#### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

#### Module Import Errors
```bash
# Ensure virtual environment is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Getting Help

- 📚 Documentation: [docs.amas.ai](https://docs.amas.ai)
- 💬 Discord: [discord.gg/amas](https://discord.gg/amas)
- 🐛 Issues: [GitHub Issues](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues)
- 📧 Email: support@amas.ai

## 🎉 Next Steps

1. **Explore the Dashboard**: Visit http://localhost:3000
2. **Try Examples**: Run scripts in the `examples/` directory
3. **Read Documentation**: Check out the comprehensive guides
4. **Join Community**: Connect with other AMAS users
5. **Customize**: Add your own agents and workflows

---

*Welcome to the AMAS community! 🚀*