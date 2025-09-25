#!/usr/bin/env python3
"""
AMAS Intelligence System Setup Script

This script sets up the AMAS Intelligence System environment,
installs dependencies, and configures services.
"""

import os
import sys
import subprocess
import shutil
import json
import secrets
import string
from pathlib import Path
from typing import Dict, Any, Optional
import argparse


class AMASSetup:
    """AMAS Intelligence System setup manager."""
    
    def __init__(self, base_path: str = None):
        """
        Initialize setup manager.
        
        Args:
            base_path: Base path for the AMAS installation
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.config_path = self.base_path / "config"
        self.data_path = self.base_path / "data"
        self.logs_path = self.base_path / "logs"
        self.models_path = self.base_path / "models"
        
        # Configuration
        self.config = {
            "amas_mode": "production",
            "offline_mode": True,
            "gpu_enabled": True,
            "log_level": "INFO",
            "jwt_secret": self._generate_secret(32),
            "encryption_key": self._generate_secret(32),
            "audit_enabled": True,
            "llm_host": "localhost:11434",
            "vector_host": "localhost:8001",
            "graph_host": "localhost:7474",
            "redis_host": "localhost:6379",
            "postgres_host": "localhost:5432",
            "neo4j_password": self._generate_secret(16),
            "postgres_password": self._generate_secret(16),
            "n8n_password": self._generate_secret(16),
            "grafana_password": self._generate_secret(16)
        }
    
    def _generate_secret(self, length: int = 32) -> str:
        """Generate a random secret string."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def create_directories(self):
        """Create necessary directories."""
        print("Creating directories...")
        
        directories = [
            self.config_path,
            self.data_path,
            self.logs_path,
            self.models_path,
            self.data_path / "vector",
            self.data_path / "graph",
            self.data_path / "files",
            self.logs_path / "audit",
            self.logs_path / "performance",
            self.models_path / "llm",
            self.models_path / "embeddings"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  Created: {directory}")
    
    def create_config_files(self):
        """Create configuration files."""
        print("Creating configuration files...")
        
        # Main configuration
        main_config = {
            "system": {
                "mode": self.config["amas_mode"],
                "offline_mode": self.config["offline_mode"],
                "gpu_enabled": self.config["gpu_enabled"],
                "log_level": self.config["log_level"]
            },
            "security": {
                "jwt_secret": self.config["jwt_secret"],
                "encryption_key": self.config["encryption_key"],
                "audit_enabled": self.config["audit_enabled"]
            },
            "services": {
                "llm": {
                    "host": self.config["llm_host"],
                    "api_key": None
                },
                "vector": {
                    "host": self.config["vector_host"],
                    "api_key": None
                },
                "graph": {
                    "host": self.config["graph_host"],
                    "username": "neo4j",
                    "password": self.config["neo4j_password"]
                },
                "redis": {
                    "host": self.config["redis_host"],
                    "password": None
                },
                "postgres": {
                    "host": self.config["postgres_host"],
                    "username": "amas",
                    "password": self.config["postgres_password"],
                    "database": "amas"
                }
            },
            "n8n": {
                "url": "http://localhost:5678",
                "username": "admin",
                "password": self.config["n8n_password"]
            },
            "monitoring": {
                "prometheus": {
                    "host": "localhost:9090"
                },
                "grafana": {
                    "host": "localhost:3001",
                    "password": self.config["grafana_password"]
                }
            }
        }
        
        config_file = self.config_path / "amas_config.json"
        with open(config_file, 'w') as f:
            json.dump(main_config, f, indent=2)
        print(f"  Created: {config_file}")
        
        # Environment file
        env_content = f"""# AMAS Intelligence System Environment Variables

# System Configuration
AMAS_MODE={self.config['amas_mode']}
AMAS_OFFLINE_MODE={self.config['offline_mode']}
AMAS_GPU_ENABLED={self.config['gpu_enabled']}
AMAS_LOG_LEVEL={self.config['log_level']}

# Security
AMAS_JWT_SECRET={self.config['jwt_secret']}
AMAS_ENCRYPTION_KEY={self.config['encryption_key']}
AMAS_AUDIT_ENABLED={self.config['audit_enabled']}

# Service URLs
AMAS_LLM_HOST={self.config['llm_host']}
AMAS_VECTOR_HOST={self.config['vector_host']}
AMAS_GRAPH_HOST={self.config['graph_host']}
AMAS_REDIS_HOST={self.config['redis_host']}
AMAS_POSTGRES_HOST={self.config['postgres_host']}

# Database Passwords
NEO4J_PASSWORD={self.config['neo4j_password']}
POSTGRES_PASSWORD={self.config['postgres_password']}

# n8n Configuration
N8N_URL=http://localhost:5678
N8N_USERNAME=admin
N8N_PASSWORD={self.config['n8n_password']}

# Monitoring
GRAFANA_PASSWORD={self.config['grafana_password']}
"""
        
        env_file = self.base_path / ".env"
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"  Created: {env_file}")
    
    def install_dependencies(self):
        """Install Python dependencies."""
        print("Installing Python dependencies...")
        
        try:
            # Install core dependencies
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], check=True)
            
            # Install requirements
            requirements_file = self.base_path / "requirements.txt"
            if requirements_file.exists():
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], check=True)
                print("  Installed core dependencies")
            
            # Install intelligence-specific dependencies
            intelligence_requirements = self.base_path / "requirements-intelligence.txt"
            if intelligence_requirements.exists():
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(intelligence_requirements)
                ], check=True)
                print("  Installed intelligence dependencies")
            
        except subprocess.CalledProcessError as e:
            print(f"  Error installing dependencies: {e}")
            sys.exit(1)
    
    def setup_docker(self):
        """Setup Docker environment."""
        print("Setting up Docker environment...")
        
        # Check if Docker is available
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            print("  Docker is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("  Docker is not available. Please install Docker first.")
            return False
        
        # Check if Docker Compose is available
        try:
            subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
            print("  Docker Compose is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("  Docker Compose is not available. Please install Docker Compose first.")
            return False
        
        return True
    
    def create_docker_compose(self):
        """Create Docker Compose configuration."""
        print("Creating Docker Compose configuration...")
        
        # Copy docker-compose.yml if it doesn't exist
        docker_compose_src = self.base_path / "docker" / "docker-compose.yml"
        docker_compose_dst = self.base_path / "docker-compose.yml"
        
        if docker_compose_src.exists() and not docker_compose_dst.exists():
            shutil.copy2(docker_compose_src, docker_compose_dst)
            print(f"  Created: {docker_compose_dst}")
    
    def create_startup_scripts(self):
        """Create startup scripts."""
        print("Creating startup scripts...")
        
        # Linux/Mac startup script
        startup_script = self.base_path / "start.sh"
        startup_content = """#!/bin/bash
# AMAS Intelligence System Startup Script

echo "Starting AMAS Intelligence System..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start Docker services
echo "Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Check service health
echo "Checking service health..."
python scripts/health_check.py

echo "AMAS Intelligence System started successfully!"
echo "Web Interface: http://localhost:3000"
echo "API: http://localhost:8000"
echo "n8n: http://localhost:5678"
echo "Grafana: http://localhost:3001"
"""
        
        with open(startup_script, 'w') as f:
            f.write(startup_content)
        startup_script.chmod(0o755)
        print(f"  Created: {startup_script}")
        
        # Windows startup script
        startup_script_win = self.base_path / "start.bat"
        startup_content_win = """@echo off
REM AMAS Intelligence System Startup Script

echo Starting AMAS Intelligence System...

REM Load environment variables
if exist .env (
    for /f "tokens=1,2 delims==" %%a in (.env) do set %%a=%%b
)

REM Start Docker services
echo Starting Docker services...
docker-compose up -d

REM Wait for services to be ready
echo Waiting for services to be ready...
timeout /t 30 /nobreak > nul

REM Check service health
echo Checking service health...
python scripts/health_check.py

echo AMAS Intelligence System started successfully!
echo Web Interface: http://localhost:3000
echo API: http://localhost:8000
echo n8n: http://localhost:5678
echo Grafana: http://localhost:3001
"""
        
        with open(startup_script_win, 'w') as f:
            f.write(startup_content_win)
        print(f"  Created: {startup_script_win}")
    
    def create_health_check(self):
        """Create health check script."""
        print("Creating health check script...")
        
        health_check_script = self.base_path / "scripts" / "health_check.py"
        health_check_content = '''#!/usr/bin/env python3
"""
AMAS Intelligence System Health Check Script
"""

import requests
import sys
import time
from typing import Dict, Any


def check_service(url: str, name: str) -> bool:
    """Check if a service is healthy."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✓ {name} is healthy")
            return True
        else:
            print(f"✗ {name} returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ {name} is not accessible: {e}")
        return False


def main():
    """Main health check function."""
    print("AMAS Intelligence System Health Check")
    print("=" * 40)
    
    services = {
        "API": "http://localhost:8000/health",
        "Web Interface": "http://localhost:3000",
        "n8n": "http://localhost:5678",
        "Grafana": "http://localhost:3001",
        "Prometheus": "http://localhost:9090"
    }
    
    healthy_services = 0
    total_services = len(services)
    
    for name, url in services.items():
        if check_service(url, name):
            healthy_services += 1
        time.sleep(1)
    
    print("=" * 40)
    print(f"Health Check Complete: {healthy_services}/{total_services} services healthy")
    
    if healthy_services == total_services:
        print("All services are healthy!")
        sys.exit(0)
    else:
        print("Some services are not healthy!")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
        
        with open(health_check_script, 'w') as f:
            f.write(health_check_content)
        health_check_script.chmod(0o755)
        print(f"  Created: {health_check_script}")
    
    def run_setup(self):
        """Run the complete setup process."""
        print("AMAS Intelligence System Setup")
        print("=" * 40)
        
        # Create directories
        self.create_directories()
        
        # Create configuration files
        self.create_config_files()
        
        # Install dependencies
        self.install_dependencies()
        
        # Setup Docker
        if self.setup_docker():
            self.create_docker_compose()
        
        # Create startup scripts
        self.create_startup_scripts()
        
        # Create health check
        self.create_health_check()
        
        print("=" * 40)
        print("Setup completed successfully!")
        print("\nNext steps:")
        print("1. Review configuration in config/amas_config.json")
        print("2. Start the system with: ./start.sh (Linux/Mac) or start.bat (Windows)")
        print("3. Access the web interface at: http://localhost:3000")
        print("4. Check system health with: python scripts/health_check.py")


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="AMAS Intelligence System Setup")
    parser.add_argument("--base-path", help="Base path for installation", default=".")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument("--skip-docker", action="store_true", help="Skip Docker setup")
    
    args = parser.parse_args()
    
    setup = AMASSetup(args.base_path)
    setup.run_setup()


if __name__ == "__main__":
    main()