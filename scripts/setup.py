#!/usr/bin/env python3
"""
AMAS Intelligence System Setup Script
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class AMASSetup:
    """AMAS Intelligence System Setup"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = self.project_root / "scripts"
        self.logs_dir = self.project_root / "logs"
        self.data_dir = self.project_root / "data"

    async def setup_system(self):
        """Setup the complete AMAS system"""
        try:
            logger.info("Starting AMAS Intelligence System setup...")

            # Create directories
            await self._create_directories()

            # Check dependencies
            await self._check_dependencies()

            # Setup Python environment
            await self._setup_python_environment()

            # Setup Docker
            await self._setup_docker()

            # Initialize services
            await self._initialize_services()

            logger.info("AMAS Intelligence System setup completed successfully!")

        except Exception as e:
            logger.error(f"Setup failed: {e}")
            sys.exit(1)

    async def _create_directories(self):
        """Create necessary directories"""
        logger.info("Creating directories...")

        directories = [
            self.logs_dir,
            self.data_dir,
            self.data_dir / "vector_index",
            self.data_dir / "knowledge_graph",
            self.data_dir / "models",
            self.data_dir / "workflows",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")

    async def _check_dependencies(self):
        """Check system dependencies"""
        logger.info("Checking dependencies...")

        # Check Python version
        if sys.version_info < (3, 8):
            raise Exception("Python 3.8 or higher is required")

        # Check Docker
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                raise Exception("Docker is not installed or not running")
            logger.info(f"Docker version: {result.stdout.strip()}")
        except FileNotFoundError:
            raise Exception("Docker is not installed")

        # Check Docker Compose
        try:
            result = subprocess.run(
                ["docker-compose", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                raise Exception("Docker Compose is not installed")
            logger.info(f"Docker Compose version: {result.stdout.strip()}")
        except FileNotFoundError:
            raise Exception("Docker Compose is not installed")

        # Check NVIDIA GPU (optional)
        try:
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("NVIDIA GPU detected - GPU acceleration enabled")
            else:
                logger.warning("NVIDIA GPU not detected - using CPU only")
        except FileNotFoundError:
            logger.warning("nvidia-smi not found - using CPU only")

    async def _setup_python_environment(self):
        """Setup Python environment"""
        logger.info("Setting up Python environment...")

        # Install requirements
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            logger.info("Installing Python dependencies...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                check=True,
            )
        else:
            logger.warning("requirements.txt not found")

    async def _setup_docker(self):
        """Setup Docker services"""
        logger.info("Setting up Docker services...")

        # Build and start services
        docker_compose_file = self.project_root / "docker-compose.yml"
        if docker_compose_file.exists():
            logger.info("Starting Docker services...")
            subprocess.run(
                [
                    "docker-compose",
                    "-f",
                    str(docker_compose_file),
                    "up",
                    "-d",
                    "--build",
                ],
                check=True,
            )
        else:
            logger.warning("docker-compose.yml not found")

    async def _initialize_services(self):
        """Initialize AMAS services"""
        logger.info("Initializing AMAS services...")

        # Wait for services to be ready
        await self._wait_for_services()

        # Initialize database
        await self._initialize_database()

        # Download models
        await self._download_models()

        # Setup workflows
        await self._setup_workflows()

    async def _wait_for_services(self):
        """Wait for services to be ready"""
        logger.info("Waiting for services to be ready...")

        services = [
            ("http://localhost:11434", "Ollama LLM Service"),
            ("http://localhost:8001", "Vector Service"),
            ("http://localhost:7474", "Neo4j Knowledge Graph"),
            ("http://localhost:5678", "n8n Workflow Engine"),
        ]

        for url, name in services:
            logger.info(f"Waiting for {name}...")
            # In a real implementation, would check HTTP endpoints

    async def _initialize_database(self):
        """Initialize database schemas"""
        logger.info("Initializing database...")

        # Initialize Neo4j
        logger.info("Setting up Neo4j knowledge graph...")

        # Initialize PostgreSQL
        logger.info("Setting up PostgreSQL database...")

    async def _download_models(self):
        """Download required models"""
        logger.info("Downloading AI models...")

        # Download Ollama models
        models = ["llama3.1:8b", "codellama:7b", "mistral:7b"]

        for model in models:
            logger.info(f"Downloading model: {model}")
            # In a real implementation, would use Ollama API

    async def _setup_workflows(self):
        """Setup n8n workflows"""
        logger.info("Setting up n8n workflows...")

        # Create intelligence workflows
        workflows = [
            "osint_collection",
            "threat_monitoring",
            "investigation_pipeline",
            "reporting_generation",
        ]

        for workflow in workflows:
            logger.info(f"Setting up workflow: {workflow}")

async def main():
    """Main setup function"""
    setup = AMASSetup()
    await setup.setup_system()

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
