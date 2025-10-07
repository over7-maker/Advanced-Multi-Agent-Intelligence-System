# 🚀 AMAS Complete Setup Guide - Updated & Verified

## 📋 **Prerequisites Checklist**

Before starting, ensure you have:

- [ ] **Python 3.9+** (3.11 recommended)
- [ ] **Docker Desktop** installed and running
- [ ] **Git** for version control
- [ ] **16GB+ RAM** (32GB recommended)
- [ ] **NVIDIA GPU** with CUDA support (optional but recommended)
- [ ] **50GB+ free disk space**

## 🎯 **Quick Start (5 Minutes)**

### **Option 1: Docker (Recommended)**

```bash
# 1. Clone the repository
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System

# 2. Start with Docker
docker-compose up -d

# 3. Verify installation
curl http://localhost:8000/health

# 4. Access the system
# Web Interface: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### **Option 2: Python Installation**

```bash
# 1. Clone and setup
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System

# 2. Create virtual environment
python -m venv amas-env
source amas-env/bin/activate  # Linux/Mac
# or
amas-env\Scripts\activate     # Windows

# 3. Install dependencies
pip install -e .

# 4. Start the system
python main.py
```

## 🔧 **Detailed Installation**

### **Step 1: System Preparation**

#### **Windows Users**
```powershell
# Run as Administrator
# Enable WSL 2
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart computer, then:
wsl --set-default-version 2
```

#### **Linux Users**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv python3-pip git curl wget
```

#### **macOS Users**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11 git docker
```

### **Step 2: Docker Installation**

#### **Windows**
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop/
2. Run installer as Administrator
3. Enable WSL 2 integration
4. Restart computer

#### **Linux**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### **macOS**
```bash
# Install Docker Desktop
brew install --cask docker

# Start Docker Desktop
open /Applications/Docker.app
```

### **Step 3: Python Environment Setup**

```bash
# Create project directory
mkdir -p ~/amas-project
cd ~/amas-project

# Clone repository
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System

# Create virtual environment
python3.11 -m venv amas-env

# Activate virtual environment
source amas-env/bin/activate  # Linux/Mac
# or
amas-env\Scripts\activate     # Windows

# Upgrade pip
python -m pip install --upgrade pip
```

### **Step 4: Install Dependencies**

```bash
# Install core dependencies
pip install -e .

# Install development dependencies (optional)
pip install -e .[dev]

# Install GPU support (if you have NVIDIA GPU)
pip install -e .[gpu]
```

### **Step 5: Configuration**

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env  # or vim .env
```

**Essential Configuration:**
```bash
# .env file
AMAS_ENVIRONMENT=development
AMAS_DEBUG=true
AMAS_OFFLINE_MODE=false
AMAS_GPU_ENABLED=true

# Database
AMAS_DB_HOST=localhost
AMAS_DB_PORT=5432
AMAS_DB_USER=amas
AMAS_DB_PASSWORD=amas_secure_password_123
AMAS_DB_NAME=amas

# Security
AMAS_JWT_SECRET=your_jwt_secret_key_here_32_chars_minimum
AMAS_ENCRYPTION_KEY=your_32_character_encryption_key_here

# LLM Service
AMAS_LLM_HOST=localhost
AMAS_LLM_PORT=11434
AMAS_LLM_MODEL=llama3.1:70b
```

## 🐳 **Docker Deployment**

### **Option 1: Complete Docker Stack**

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### **Option 2: Development Mode**

```bash
# Start with hot reload
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

### **Option 3: Production Mode**

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

## 🧪 **Verification & Testing**

### **Health Checks**

```bash
# Check system health
curl http://localhost:8000/health

# Check API status
curl http://localhost:8000/status

# Check agents
curl http://localhost:8000/agents
```

### **CLI Testing**

```bash
# Install CLI
pip install -e .

# Check system status
amas status

# Run health check
amas health --check-all

# Submit test task
amas submit-task research "Test AI capabilities" --wait
```

### **Web Interface Testing**

1. Open browser to `http://localhost:3000`
2. Check dashboard loads correctly
3. Submit a test task through the UI
4. Monitor task progress
5. Verify results display

## 🔧 **Troubleshooting**

### **Common Issues & Solutions**

#### **Docker Issues**

**Problem**: Docker not found
```bash
# Check Docker installation
docker --version

# If not found, reinstall Docker Desktop
# Restart terminal after installation
```

**Problem**: Docker daemon not running
```bash
# Start Docker Desktop
# Or start Docker service
sudo systemctl start docker  # Linux
net start com.docker.service  # Windows
```

**Problem**: Permission denied
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Restart terminal
```

#### **Python Issues**

**Problem**: Virtual environment not activating
```bash
# Check Python version
python --version

# Recreate virtual environment
rm -rf amas-env
python3.11 -m venv amas-env
source amas-env/bin/activate
```

**Problem**: Package installation fails
```bash
# Update pip
python -m pip install --upgrade pip

# Clear pip cache
pip cache purge

# Install with verbose output
pip install -e . -v
```

#### **Service Issues**

**Problem**: Services not starting
```bash
# Check Docker logs
docker-compose logs

# Check port conflicts
netstat -tulpn | grep :8000

# Restart services
docker-compose restart
```

**Problem**: Database connection failed
```bash
# Check database status
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d
```

### **Performance Issues**

**Problem**: Slow performance
```bash
# Check resource usage
docker stats

# Increase Docker resources
# Docker Desktop > Settings > Resources > Advanced
# Memory: 8GB+, CPUs: 4+

# Check GPU usage
nvidia-smi  # If using GPU
```

**Problem**: Memory issues
```bash
# Check memory usage
free -h  # Linux
# or
docker stats

# Increase swap space if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📊 **System Monitoring**

### **Health Monitoring**

```bash
# Real-time monitoring
watch -n 5 'curl -s http://localhost:8000/health | jq'

# Check all services
curl -s http://localhost:8000/status | jq

# Monitor Docker containers
watch -n 5 'docker-compose ps'
```

### **Log Monitoring**

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f amas-api
docker-compose logs -f postgres
docker-compose logs -f redis

# View application logs
tail -f logs/amas.log
```

### **Performance Monitoring**

```bash
# System resources
htop  # or top

# Docker resources
docker stats

# GPU usage (if applicable)
nvidia-smi -l 1
```

## 🚀 **Production Deployment**

### **Environment Setup**

```bash
# Set production environment
export AMAS_ENVIRONMENT=production
export AMAS_DEBUG=false
export AMAS_OFFLINE_MODE=true

# Update configuration
cp .env.production .env
```

### **Security Hardening**

```bash
# Generate secure keys
openssl rand -hex 32  # For JWT secret
openssl rand -hex 32  # For encryption key

# Update .env with secure values
nano .env
```

### **Backup Strategy**

```bash
# Backup database
docker-compose exec postgres pg_dump -U amas amas > backup_$(date +%Y%m%d).sql

# Backup configuration
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env docker-compose.yml

# Backup data
tar -czf data_backup_$(date +%Y%m%d).tar.gz data/ logs/
```

### **Monitoring Setup**

```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Access monitoring
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001
```

## 🎯 **Next Steps**

### **After Successful Installation**

1. **Explore the Web Interface**
   - Visit `http://localhost:3000`
   - Familiarize yourself with the dashboard
   - Try submitting different types of tasks

2. **Test Agent Capabilities**
   - Submit OSINT tasks
   - Try data analysis tasks
   - Test reporting functionality

3. **Configure Monitoring**
   - Set up Grafana dashboards
   - Configure alerting
   - Monitor system performance

4. **Customize Configuration**
   - Adjust agent parameters
   - Configure security settings
   - Set up backup schedules

5. **Explore Advanced Features**
   - Create custom workflows
   - Integrate with external systems
   - Develop custom agents

## 🆘 **Getting Help**

### **Documentation**
- **User Guide**: [docs/user/README.md](docs/user/README.md)
- **Developer Guide**: [docs/developer/README.md](docs/developer/README.md)
- **API Reference**: [docs/api/README.md](docs/api/README.md)

### **Community Support**
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Community Q&A
- **Discord**: Real-time community chat

### **Professional Support**
- **Enterprise Support**: Available for production deployments
- **Custom Development**: Tailored solutions for specific needs
- **Training & Consulting**: Expert guidance and training

---

## ✅ **Installation Checklist**

- [ ] Prerequisites installed (Python, Docker, Git)
- [ ] Repository cloned successfully
- [ ] Virtual environment created and activated
- [ ] Dependencies installed without errors
- [ ] Configuration file created and customized
- [ ] Docker services started successfully
- [ ] Health checks passing
- [ ] Web interface accessible
- [ ] CLI commands working
- [ ] Test task submitted and completed
- [ ] Monitoring configured (optional)
- [ ] Backup strategy implemented (optional)

**🎉 Congratulations! Your AMAS system is now ready for production use!**

*For additional support, please refer to the documentation or contact the development team.*