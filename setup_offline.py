#!/usr/bin/env python3
"""
AMAS Intelligence System - Offline Setup Script
Complete offline installation and configuration
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class OfflineSetup:
    """Complete offline setup for AMAS system"""
    
    def __init__(self):
        self.workspace_path = Path("/workspace")
        self.data_path = self.workspace_path / "data"
        self.models_path = self.workspace_path / "models"
        self.logs_path = self.workspace_path / "logs"
        
    def create_offline_directories(self):
        """Create all necessary offline directories"""
        try:
            logger.info("📁 Creating offline directory structure...")
            
            directories = [
                self.data_path,
                self.models_path,
                self.logs_path,
                self.data_path / "agents",
                self.data_path / "vectors",
                self.data_path / "neo4j",
                self.data_path / "postgres",
                self.data_path / "redis",
                self.data_path / "backups",
                self.data_path / "datasets",
                self.data_path / "evidence",
                self.models_path / "llm",
                self.models_path / "embedding",
                self.models_path / "classification"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"   ✅ Created: {directory}")
            
            logger.info("✅ Offline directory structure created")
            return True
            
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            return False
    
    def create_offline_config_files(self):
        """Create offline configuration files"""
        try:
            logger.info("⚙️ Creating offline configuration files...")
            
            # Create offline environment file
            env_content = """# AMAS Offline Environment Configuration
AMAS_MODE=offline
AMAS_OFFLINE_MODE=true
AMAS_LOCAL_ONLY=true
AMAS_NO_INTERNET=true
AMAS_ISOLATION_LEVEL=complete

# Local Service URLs
AMAS_LLM_HOST=localhost:11434
AMAS_VECTOR_HOST=localhost:8001
AMAS_GRAPH_HOST=localhost:7474
AMAS_REDIS_HOST=localhost:6379
AMAS_POSTGRES_HOST=localhost:5432

# Database Configuration
AMAS_POSTGRES_USER=amas
AMAS_POSTGRES_PASSWORD=amas_offline_secure
AMAS_POSTGRES_DB=amas_offline

# Neo4j Configuration
AMAS_NEO4J_AUTH=neo4j/amas_offline_secure

# Security Configuration
AMAS_JWT_SECRET=amas_offline_jwt_secret_2024_secure
AMAS_ENCRYPTION_KEY=offline_encryption_key_2024_secure

# Data Paths
AMAS_DATA_PATH=/workspace/data
AMAS_MODELS_PATH=/workspace/models
AMAS_LOGS_PATH=/workspace/logs
"""
            
            env_file = self.workspace_path / ".env.offline"
            with open(env_file, 'w') as f:
                f.write(env_content)
            logger.info(f"   ✅ Created: {env_file}")
            
            # Create offline requirements file
            requirements_content = """# AMAS Offline Requirements
# Core dependencies for offline operation

# Web Framework
fastapi==0.117.1
uvicorn==0.37.0
pydantic==2.11.9

# HTTP and Networking
requests==2.32.5
aiohttp==3.12.15
httpx==0.28.1

# Data Processing
numpy==2.3.3
pandas==2.3.2

# Security
PyJWT==2.10.1
cryptography==46.0.1
bcrypt==5.0.0

# Local Database (optional)
# psycopg2-binary==2.9.9
# redis==5.0.1
# neo4j==5.15.0

# Local ML (optional)
# scikit-learn==1.3.0
# sentence-transformers==2.2.2

# Utilities
python-dotenv==1.0.0
pyyaml==6.0.1
click==8.1.7
rich==13.7.0
"""
            
            req_file = self.workspace_path / "requirements-offline.txt"
            with open(req_file, 'w') as f:
                f.write(requirements_content)
            logger.info(f"   ✅ Created: {req_file}")
            
            # Create offline startup script
            startup_script = """#!/bin/bash
# AMAS Offline Startup Script

echo "🔒 Starting AMAS Offline System..."
echo "=================================="

# Set offline environment
export AMAS_MODE=offline
export AMAS_OFFLINE_MODE=true
export AMAS_LOCAL_ONLY=true
export AMAS_NO_INTERNET=true

# Start offline system
echo "🚀 Starting offline agents..."
python3 offline_example.py

echo "✅ AMAS Offline System started"
"""
            
            startup_file = self.workspace_path / "start_offline.sh"
            with open(startup_file, 'w') as f:
                f.write(startup_script)
            os.chmod(startup_file, 0o755)
            logger.info(f"   ✅ Created: {startup_file}")
            
            logger.info("✅ Offline configuration files created")
            return True
            
        except Exception as e:
            logger.error(f"Error creating config files: {e}")
            return False
    
    def create_offline_datasets(self):
        """Create offline datasets for local operation"""
        try:
            logger.info("📊 Creating offline datasets...")
            
            # Create sample threat intelligence dataset
            threat_intel = {
                "malware_signatures": [
                    {
                        "name": "Trojan.Generic.Offline",
                        "hash": "abc123def456",
                        "severity": "high",
                        "source": "local_db",
                        "timestamp": "2024-09-26T18:00:00Z"
                    },
                    {
                        "name": "Ransomware.Crypto.Offline",
                        "hash": "def456ghi789",
                        "severity": "critical",
                        "source": "local_db",
                        "timestamp": "2024-09-26T18:00:00Z"
                    }
                ],
                "ip_reputation": [
                    {
                        "ip": "192.168.1.100",
                        "reputation": "malicious",
                        "source": "local_db",
                        "confidence": 0.9
                    },
                    {
                        "ip": "10.0.0.1",
                        "reputation": "clean",
                        "source": "local_db",
                        "confidence": 0.95
                    }
                ],
                "domain_reputation": [
                    {
                        "domain": "malicious-offline.example.com",
                        "reputation": "malicious",
                        "source": "local_db",
                        "confidence": 0.85
                    }
                ]
            }
            
            threat_file = self.data_path / "datasets" / "threat_intelligence.json"
            with open(threat_file, 'w') as f:
                import json
                json.dump(threat_intel, f, indent=2)
            logger.info(f"   ✅ Created: {threat_file}")
            
            # Create sample OSINT dataset
            osint_data = {
                "news_sources": [
                    {
                        "name": "Local Security News",
                        "url": "local://news/security",
                        "type": "offline",
                        "last_updated": "2024-09-26T18:00:00Z"
                    }
                ],
                "social_media": [
                    {
                        "platform": "local_forum",
                        "url": "local://forum/security",
                        "type": "offline",
                        "last_updated": "2024-09-26T18:00:00Z"
                    }
                ],
                "web_sources": [
                    {
                        "name": "Local Web Archive",
                        "url": "local://archive/web",
                        "type": "offline",
                        "last_updated": "2024-09-26T18:00:00Z"
                    }
                ]
            }
            
            osint_file = self.data_path / "datasets" / "osint_sources.json"
            with open(osint_file, 'w') as f:
                import json
                json.dump(osint_data, f, indent=2)
            logger.info(f"   ✅ Created: {osint_file}")
            
            logger.info("✅ Offline datasets created")
            return True
            
        except Exception as e:
            logger.error(f"Error creating datasets: {e}")
            return False
    
    def create_docker_offline_setup(self):
        """Create Docker offline setup"""
        try:
            logger.info("🐳 Creating Docker offline setup...")
            
            # Create offline Dockerfile
            dockerfile_content = """FROM python:3.13-slim

# Set offline environment
ENV AMAS_MODE=offline
ENV AMAS_OFFLINE_MODE=true
ENV AMAS_LOCAL_ONLY=true
ENV AMAS_NO_INTERNET=true

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements-offline.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-offline.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /app/data /app/models /app/logs

# Expose port
EXPOSE 8000

# Start command
CMD ["python3", "offline_example.py"]
"""
            
            dockerfile = self.workspace_path / "Dockerfile.offline"
            with open(dockerfile, 'w') as f:
                f.write(dockerfile_content)
            logger.info(f"   ✅ Created: {dockerfile}")
            
            # Create offline startup script
            start_offline_script = """#!/bin/bash
# AMAS Offline Docker Startup

echo "🔒 Starting AMAS Offline System with Docker..."
echo "=============================================="

# Start offline services
docker-compose -f docker-compose-offline.yml up -d

echo "✅ AMAS Offline System started with Docker"
echo "🌐 Access: http://localhost:8000"
echo "📊 Health: http://localhost:8000/health"
"""
            
            start_script = self.workspace_path / "start_offline_docker.sh"
            with open(start_script, 'w') as f:
                f.write(start_offline_script)
            os.chmod(start_script, 0o755)
            logger.info(f"   ✅ Created: {start_script}")
            
            logger.info("✅ Docker offline setup created")
            return True
            
        except Exception as e:
            logger.error(f"Error creating Docker setup: {e}")
            return False
    
    def run_offline_setup(self):
        """Run complete offline setup"""
        try:
            logger.info("🚀 AMAS Offline Setup")
            logger.info("=" * 50)
            logger.info("🔒 Complete Local Isolation Setup")
            logger.info("=" * 50)
            
            # Create directories
            if not self.create_offline_directories():
                return False
            
            # Create configuration files
            if not self.create_offline_config_files():
                return False
            
            # Create datasets
            if not self.create_offline_datasets():
                return False
            
            # Create Docker setup
            if not self.create_docker_offline_setup():
                return False
            
            # Final summary
            logger.info("=" * 50)
            logger.info("🎉 OFFLINE SETUP COMPLETED SUCCESSFULLY!")
            logger.info("=" * 50)
            logger.info("✅ Directory structure created")
            logger.info("✅ Configuration files created")
            logger.info("✅ Offline datasets created")
            logger.info("✅ Docker setup created")
            logger.info("=" * 50)
            logger.info("🚀 To start offline system:")
            logger.info("   python3 offline_example.py")
            logger.info("   ./start_offline.sh")
            logger.info("   ./start_offline_docker.sh")
            logger.info("=" * 50)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in offline setup: {e}")
            return False

def main():
    """Main setup function"""
    try:
        setup = OfflineSetup()
        success = setup.run_offline_setup()
        
        if success:
            logger.info("🏆 AMAS Offline setup completed successfully!")
            return 0
        else:
            logger.error("❌ AMAS Offline setup failed!")
            return 1
            
    except Exception as e:
        logger.error(f"Setup error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)