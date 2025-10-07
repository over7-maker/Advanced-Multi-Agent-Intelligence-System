# ⚙️ AMAS Configuration Guide

## Overview

This guide covers all configuration options for the AMAS system, including the new minimal configuration modes and environment setup.

## 🎯 Configuration Modes

### **Basic Mode (3 API Keys)**
Minimal setup with core functionality:
- **DEEPSEEK_API_KEY**: Primary AI provider
- **GLM_API_KEY**: Secondary AI provider  
- **GROK_API_KEY**: Tertiary AI provider

### **Standard Mode (4 API Keys)**
Enhanced setup with additional capabilities:
- Basic mode + **KIMI_API_KEY**

### **Full Mode (6 API Keys)**
Complete setup with all providers:
- Standard mode + **QWEN_API_KEY** + **GPTOSS_API_KEY**

## 🔧 Environment Variables

### **Required Variables (Basic Mode)**
```bash
# AI Provider Keys
export DEEPSEEK_API_KEY="your_deepseek_api_key"
export GLM_API_KEY="your_glm_api_key"
export GROK_API_KEY="your_grok_api_key"

# Configuration Mode
export AMAS_CONFIG_MODE="basic"
```

### **Optional Variables (Standard/Full Modes)**
```bash
# Additional AI Providers
export KIMI_API_KEY="your_kimi_api_key"      # Standard mode
export QWEN_API_KEY="your_qwen_api_key"      # Full mode
export GPTOSS_API_KEY="your_gptoss_api_key"  # Full mode
```

### **Application Settings**
```bash
# Environment
export AMAS_ENVIRONMENT="development"  # development, staging, production
export AMAS_DEBUG="true"               # true, false
export AMAS_OFFLINE_MODE="false"       # true, false
export AMAS_GPU_ENABLED="false"        # true, false
```

### **Database Configuration**
```bash
# PostgreSQL
export AMAS_DB_HOST="localhost"
export AMAS_DB_PORT="5432"
export AMAS_DB_USER="amas"
export AMAS_DB_PASSWORD="your_secure_password"
export AMAS_DB_NAME="amas"

# Redis
export AMAS_REDIS_HOST="localhost"
export AMAS_REDIS_PORT="6379"
export AMAS_REDIS_PASSWORD="your_redis_password"
export AMAS_REDIS_DB="0"

# Neo4j
export AMAS_NEO4J_URI="bolt://localhost:7687"
export AMAS_NEO4J_USER="neo4j"
export AMAS_NEO4J_PASSWORD="your_neo4j_password"
```

### **Security Settings**
```bash
# JWT and Encryption
export AMAS_JWT_SECRET="your_jwt_secret_key_minimum_32_characters"
export AMAS_ENCRYPTION_KEY="your_32_character_encryption_key"
export AMAS_AUDIT_ENABLED="true"
```

### **Development Settings**
```bash
# PgAdmin (for development)
export PGADMIN_PASSWORD="your_pgadmin_password"
```

### **Performance Settings**
```bash
# System Performance
export AMAS_MAX_WORKERS="4"
export AMAS_TASK_TIMEOUT="300"
export AMAS_RATE_LIMIT="100"
```

### **Logging Settings**
```bash
# Logging Configuration
export AMAS_LOG_LEVEL="INFO"           # DEBUG, INFO, WARNING, ERROR
export AMAS_LOG_FORMAT="json"          # json, text
export AMAS_LOG_FILE="logs/amas.log"
```

### **Monitoring Settings**
```bash
# Monitoring and Metrics
export AMAS_METRICS_ENABLED="true"
export AMAS_HEALTH_CHECK_INTERVAL="30"
export AMAS_PROMETHEUS_PORT="9090"
```

## 📁 Configuration Files

### **Environment Template (.env.example)**
```bash
# Copy and customize
cp .env.example .env
vim .env
```

### **Minimal Configuration (src/amas/config/minimal_config.py)**
```python
from amas.config.minimal_config import get_minimal_config_manager, MinimalMode

# Get configuration manager
config_manager = get_minimal_config_manager(MinimalMode.BASIC)

# Validate environment
is_valid = config_manager.validate_environment()
```

### **Docker Compose (docker-compose.dev.yml)**
```yaml
# Development environment with all services
version: '3.8'
services:
  amas-dev:
    build: .
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - GLM_API_KEY=${GLM_API_KEY}
      - GROK_API_KEY=${GROK_API_KEY}
    ports:
      - "8000:8000"
```

## 🚀 Quick Setup

### **1. Basic Setup (3 API Keys)**
```bash
# Set minimal required keys
export DEEPSEEK_API_KEY="your_key"
export GLM_API_KEY="your_key"
export GROK_API_KEY="your_key"

# Validate setup
python scripts/validate_env.py --mode basic --verbose
```

### **2. Standard Setup (4 API Keys)**
```bash
# Add KIMI key to basic setup
export KIMI_API_KEY="your_key"

# Validate setup
python scripts/validate_env.py --mode standard --verbose
```

### **3. Full Setup (6 API Keys)**
```bash
# Add remaining keys
export QWEN_API_KEY="your_key"
export GPTOSS_API_KEY="your_key"

# Validate setup
python scripts/validate_env.py --mode full --verbose
```

## 🔍 Validation

### **Environment Validation**
```bash
# Basic validation
python scripts/validate_env.py --mode basic

# Verbose validation
python scripts/validate_env.py --mode basic --verbose

# Skip database checks
python scripts/validate_env.py --mode basic --skip-db

# Generate environment template
python scripts/validate_env.py --generate-template
```

### **Implementation Verification**
```bash
# Verify all implementations
python scripts/verify_implementation.py

# Check specific components
python scripts/verify_implementation.py --component orchestrator
python scripts/verify_implementation.py --component agents
```

## 🐳 Docker Configuration

### **Development Environment**
```bash
# Start complete development environment
docker-compose -f docker-compose.dev.yml up -d

# Check services
docker-compose -f docker-compose.dev.yml ps

# View logs
docker-compose -f docker-compose.dev.yml logs -f amas-dev
```

### **Environment Variables in Docker**
```yaml
# docker-compose.dev.yml
environment:
  - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
  - GLM_API_KEY=${GLM_API_KEY}
  - GROK_API_KEY=${GROK_API_KEY}
  - AMAS_CONFIG_MODE=${AMAS_CONFIG_MODE:-basic}
  - AMAS_DEBUG=${AMAS_DEBUG:-true}
```

## 🧪 Testing Configuration

### **Test Environment**
```bash
# Set test environment variables
export AMAS_ENVIRONMENT="test"
export AMAS_DEBUG="true"
export AMAS_CONFIG_MODE="basic"

# Run tests
python scripts/run_tests.py --unit --verbose
```

### **Test Configuration Files**
- `pytest.ini`: Pytest configuration
- `tests/conftest.py`: Test fixtures and configuration
- `scripts/run_tests.py`: Test runner script

## 📊 Performance Configuration

### **Benchmarking**
```bash
# Run performance benchmarks
python scripts/benchmark_system.py --mode basic --output results.json

# Run specific benchmarks
python scripts/benchmark_system.py --mode basic --benchmark latency
python scripts/benchmark_system.py --mode basic --benchmark throughput
```

### **Performance Tuning**
```bash
# Adjust worker count
export AMAS_MAX_WORKERS="8"

# Adjust task timeout
export AMAS_TASK_TIMEOUT="600"

# Adjust rate limits
export AMAS_RATE_LIMIT="200"
```

## 🔒 Security Configuration

### **API Key Security**
```bash
# Use environment variables (recommended)
export DEEPSEEK_API_KEY="your_key"

# Or use a secrets file (not recommended for production)
echo "DEEPSEEK_API_KEY=your_key" >> .env
```

### **Database Security**
```bash
# Use strong passwords
export AMAS_DB_PASSWORD="$(openssl rand -base64 32)"
export AMAS_REDIS_PASSWORD="$(openssl rand -base64 32)"
export AMAS_NEO4J_PASSWORD="$(openssl rand -base64 32)"
```

### **JWT and Encryption**
```bash
# Generate secure keys
export AMAS_JWT_SECRET="$(openssl rand -base64 32)"
export AMAS_ENCRYPTION_KEY="$(openssl rand -base64 32 | head -c 32)"
```

## 🚨 Troubleshooting

### **Common Issues**

#### **1. Missing API Keys**
```bash
# Error: Missing required API keys
# Solution: Set minimal required keys
export DEEPSEEK_API_KEY="your_key"
export GLM_API_KEY="your_key"
export GROK_API_KEY="your_key"
```

#### **2. Configuration Mode Mismatch**
```bash
# Error: Configuration mode not supported
# Solution: Use supported modes
export AMAS_CONFIG_MODE="basic"    # or "standard" or "full"
```

#### **3. Database Connection Issues**
```bash
# Error: Database connection failed
# Solution: Check database settings and skip DB checks for testing
python scripts/validate_env.py --mode basic --skip-db
```

#### **4. Import Errors**
```bash
# Error: ModuleNotFoundError
# Solution: Install dependencies
pip install -r requirements.txt
```

### **Debug Mode**
```bash
# Enable debug mode for detailed logging
export AMAS_DEBUG="true"
export AMAS_LOG_LEVEL="DEBUG"

# Run with verbose output
python scripts/validate_env.py --mode basic --verbose
```

## 📚 Additional Resources

- **Implementation Status**: `IMPLEMENTATION_STATUS.md`
- **Migration Guide**: `MIGRATION_GUIDE.md`
- **Project Status**: `PROJECT_STATUS.md`
- **API Documentation**: `http://localhost:8000/docs` (when running)

---

**🎯 Your AMAS system is now properly configured and ready for use!**