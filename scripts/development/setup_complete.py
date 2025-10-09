"""
Complete Setup Script for AMAS Intelligence System
Handles all dependencies, environment setup, and system initialization
"""

import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def install_requirements():
    """Install required packages"""
    try:
        logger.info("Installing required packages...")

        # Install base requirements
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        logger.info("Base requirements installed successfully")

        # Install phase 2 requirements if available
        if Path("requirements-phase2.txt").exists():
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    "requirements-phase2.txt",
                ]
            )
            logger.info("Phase 2 requirements installed successfully")

        # Install additional packages for enhanced functionality
        additional_packages = [
            "python-dotenv",
            "httpx",
            "aiofiles",
            "pydantic-settings",
            "structlog",
            "rich",
            "typer",
        ]

        for package in additional_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                logger.info(f"Installed {package}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to install {package}: {e}")

        logger.info("All requirements installed successfully")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing requirements: {e}")
        sys.exit(1)


def create_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "data",
        "evidence",
        "sandbox",
        "backups",
        "models",
        "cache",
        "temp",
        "reports",
        "intelligence",
        "threat_intel",
        "osint_data",
        "forensics_data",
        "analysis_results",
    ]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory}")


def setup_environment():
    """Setup environment variables and configuration"""
    try:
        # Load environment variables from .env file
        if Path(".env").exists():
            from dotenv import load_dotenv

            load_dotenv()
            logger.info("Environment variables loaded from .env file")
        else:
            logger.warning(".env file not found. Using default configuration.")

        # Set environment variables
        os.environ.setdefault("AMAS_MODE", "development")
        os.environ.setdefault("AMAS_OFFLINE_MODE", "true")
        os.environ.setdefault("AMAS_GPU_ENABLED", "true")
        os.environ.setdefault("AMAS_LOG_LEVEL", "INFO")

        logger.info("Environment setup completed")

    except Exception as e:
        logger.error(f"Error setting up environment: {e}")
        raise


def check_docker_services():
    """Check if Docker services are running"""
    try:
        # Check if docker-compose is available
        result = subprocess.run(
            ["docker-compose", "--version"], capture_output=True, text=True
        )
        if result.returncode == 0:
            logger.info(f"Docker Compose available: {result.stdout.strip()}")
        else:
            logger.warning(
                "Docker Compose not found. Please install Docker and Docker Compose."
            )
            return False

        # Check if services are running
        result = subprocess.run(
            ["docker-compose", "ps"], capture_output=True, text=True
        )
        if result.returncode == 0:
            logger.info("Docker services status:")
            logger.info(result.stdout)
        else:
            logger.warning("Could not check Docker services status")

        return True

    except Exception as e:
        logger.error(f"Error checking Docker services: {e}")
        return False


def start_docker_services():
    """Start Docker services"""
    try:
        logger.info("Starting Docker services...")
        result = subprocess.run(
            ["docker-compose", "up", "-d"], capture_output=True, text=True
        )
        if result.returncode == 0:
            logger.info("Docker services started successfully")
            return True
        else:
            logger.error(f"Failed to start Docker services: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Error starting Docker services: {e}")
        return False


def create_docker_compose_override():
    """Create docker-compose.override.yml for development"""
    override_content = """version: '3.8'

services:
  amas-core:
    environment:
      - AMAS_MODE=development
      - AMAS_OFFLINE_MODE=true
      - AMAS_GPU_ENABLED=true
      - AMAS_LOG_LEVEL=DEBUG
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
      - ./evidence:/app/evidence
      - ./sandbox:/app/sandbox
      - ./backups:/app/backups
      - ./models:/app/models
      - ./cache:/app/cache
      - ./temp:/app/temp
      - ./reports:/app/reports
      - ./intelligence:/app/intelligence
      - ./threat_intel:/app/threat_intel
      - ./osint_data:/app/osint_data
      - ./forensics_data:/app/forensics_data
      - ./analysis_results:/app/analysis_results
    ports:
      - "8000:8000"
      - "8001:8001"
    restart: unless-stopped

  postgres:
    environment:
      - POSTGRES_DB=amas
      - POSTGRES_USER=amas
      - POSTGRES_PASSWORD=amas123
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init_db.sql
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

  neo4j:
    environment:
      - NEO4J_AUTH=neo4j/amas123
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    ports:
      - "7474:7474"
      - "7687:7687"
    restart: unless-stopped

  ollama:
    environment:
      - OLLAMA_HOST=0.0.0.0
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  neo4j_data:
  neo4j_logs:
  ollama_data:
"""

    with open("docker-compose.override.yml", "w") as f:
        f.write(override_content)

    logger.info("Created docker-compose.override.yml for development")


async def test_system_components():
    """Test system components"""
    try:
        logger.info("Testing system components...")

        # Test imports
        try:
            from main import AMASIntelligenceSystem

            logger.info("✅ Main system import successful")
        except Exception as e:
            logger.error(f"❌ Main system import failed: {e}")
            return False

        # Test services
        try:
            from services.database_service import DatabaseService
            from services.knowledge_graph_service import KnowledgeGraphService
            from services.llm_service import LLMService
            from services.security_service import SecurityService
            from services.vector_service import VectorService

            logger.info("✅ Agent imports successful")
        except Exception as e:
            logger.error(f"❌ Agent imports failed: {e}")
            return False

        # Test API
        try:
            from api.main import app

            logger.info("✅ API import successful")
        except Exception as e:
            logger.error(f"❌ API import failed: {e}")
            return False

        logger.info("✅ All system components imported successfully")
        return True

    except Exception as e:
        logger.error(f"System component test failed: {e}")
        return False


def create_startup_scripts():
    """Create startup scripts for different environments"""

    # Development startup script
    dev_script = """#!/bin/bash
# AMAS Intelligence System - Development Startup Script

echo "Starting AMAS Intelligence System in Development Mode..."

# Load environment variables
export AMAS_MODE=development
export AMAS_OFFLINE_MODE=true
export AMAS_GPU_ENABLED=true
export AMAS_LOG_LEVEL=DEBUG

# Start Docker services
echo "Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Start the main application
echo "Starting AMAS Intelligence System..."
python main.py

echo "AMAS Intelligence System started successfully!"
"""

    with open("start_dev.sh", "w") as f:
        f.write(dev_script)
    os.chmod("start_dev.sh", 0o755)

    # Production startup script
    prod_script = """#!/bin/bash
# AMAS Intelligence System - Production Startup Script

echo "Starting AMAS Intelligence System in Production Mode..."

# Load environment variables
export AMAS_MODE=production
export AMAS_OFFLINE_MODE=false
export AMAS_GPU_ENABLED=true
export AMAS_LOG_LEVEL=INFO

# Start Docker services
echo "Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Start the API server
echo "Starting AMAS API Server..."
python api/main.py

echo "AMAS Intelligence System started successfully!"
"""

    with open("start_prod.sh", "w") as f:
        f.write(prod_script)
    os.chmod("start_prod.sh", 0o755)

    # Test script
    test_script = """#!/bin/bash
# AMAS Intelligence System - Test Script

echo "Running AMAS Intelligence System Tests..."

# Run complete system test
python test_complete_system.py

echo "Tests completed!"
"""

    with open("run_tests.sh", "w") as f:
        f.write(test_script)
    os.chmod("run_tests.sh", 0o755)

    logger.info("Created startup scripts: start_dev.sh, start_prod.sh, run_tests.sh")


def main():
    """Main setup function"""
    logger.info("Setting up AMAS Intelligence System...")
    logger.info("=" * 60)

    try:
        # Step 1: Create directories
        logger.info("Step 1: Creating directories...")
        create_directories()

        # Step 2: Install requirements
        logger.info("Step 2: Installing requirements...")
        install_requirements()

        # Step 3: Setup environment
        logger.info("Step 3: Setting up environment...")
        setup_environment()

        # Step 4: Create Docker override
        logger.info("Step 4: Creating Docker override...")
        create_docker_compose_override()

        # Step 5: Create startup scripts
        logger.info("Step 5: Creating startup scripts...")
        create_startup_scripts()

        # Step 6: Test system components
        logger.info("Step 6: Testing system components...")
        component_test_passed = asyncio.run(test_system_components())

        # Step 7: Check Docker services
        logger.info("Step 7: Checking Docker services...")
        docker_available = check_docker_services()

        if docker_available:
            logger.info("Step 8: Starting Docker services...")
            docker_started = start_docker_services()
            if docker_started:
                logger.info("✅ Docker services started successfully")
            else:
                logger.warning("⚠️ Docker services failed to start")
        else:
            logger.warning(
                "⚠️ Docker not available. Please install Docker and Docker Compose."
            )

        # Summary
        logger.info("=" * 60)
        logger.info("SETUP COMPLETED")
        logger.info("=" * 60)
        logger.info(f"✅ Directories created")
        logger.info(f"✅ Requirements installed")
        logger.info(f"✅ Environment configured")
        logger.info(f"✅ Docker override created")
        logger.info(f"✅ Startup scripts created")
        logger.info(
            f"✅ System components: {'PASSED' if component_test_passed else 'FAILED'}"
        )
        logger.info(
            f"✅ Docker services: {'AVAILABLE' if docker_available else 'NOT AVAILABLE'}"
        )

        if component_test_passed:
            logger.info("🎉 AMAS Intelligence System setup completed successfully!")
            logger.info("")
            logger.info("Next steps:")
            logger.info("1. Start the system: ./start_dev.sh")
            logger.info("2. Run tests: ./run_tests.sh")
            logger.info("3. Access API: http://localhost:8000")
            logger.info("4. View logs: tail -f logs/amas.log")
        else:
            logger.error("❌ Setup completed with errors. Please check the logs.")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Setup failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
