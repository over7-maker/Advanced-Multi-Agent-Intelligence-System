"""
Virtual Environment Setup Script for AMAS Intelligence System
"""

import subprocess
import sys
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def create_virtual_environment():
    """Create virtual environment"""
    try:
        logger.info("Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        logger.info("Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating virtual environment: {e}")
        return False


def install_requirements():
    """Install requirements in virtual environment"""
    try:
        logger.info("Installing requirements in virtual environment...")

        # Determine pip path
        if os.name == "nt":  # Windows
            pip_path = "venv/Scripts/pip"
            python_path = "venv/Scripts/python"
        else:  # Unix/Linux
            pip_path = "venv/bin/pip"
            python_path = "venv/bin/python"

        # Upgrade pip first
        subprocess.check_call([python_path, "-m", "pip", "install", "--upgrade", "pip"])

        # Install requirements
        if Path("requirements.txt").exists():
            subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])
            logger.info("Base requirements installed")

        if Path("requirements-phase2.txt").exists():
            subprocess.check_call(
                [pip_path, "install", "-r", "requirements-phase2.txt"]
            )
            logger.info("Phase 2 requirements installed")

        # Install additional packages
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
                subprocess.check_call([pip_path, "install", package])
                logger.info(f"Installed {package}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to install {package}: {e}")

        logger.info("All requirements installed successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing requirements: {e}")
        return False


def create_activation_scripts():
    """Create activation scripts for different platforms"""

    # Windows activation script
    windows_script = """@echo off
echo Activating AMAS Intelligence System Virtual Environment...
call venv\\Scripts\\activate.bat
echo Virtual environment activated!
echo.
echo To start the system:
echo   python main.py
echo.
echo To run tests:
echo   python test_complete_system.py
echo.
echo To start API server:
echo   python api/main.py
"""

    with open("activate_venv.bat", "w") as f:
        f.write(windows_script)

    # Unix/Linux activation script
    unix_script = """#!/bin/bash
echo "Activating AMAS Intelligence System Virtual Environment..."
source venv/bin/activate
echo "Virtual environment activated!"
echo ""
echo "To start the system:"
echo "  python main.py"
echo ""
echo "To run tests:"
echo "  python test_complete_system.py"
echo ""
echo "To start API server:"
echo "  python api/main.py"
"""

    with open("activate_venv.sh", "w") as f:
        f.write(unix_script)
    os.chmod("activate_venv.sh", 0o755)

    logger.info("Created activation scripts: activate_venv.bat, activate_venv.sh")


def create_startup_scripts():
    """Create startup scripts that use virtual environment"""

    # Development startup script
    dev_script = """#!/bin/bash
# AMAS Intelligence System - Development Startup Script

echo "Starting AMAS Intelligence System in Development Mode..."

# Activate virtual environment
source venv/bin/activate

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

    # Test script
    test_script = """#!/bin/bash
# AMAS Intelligence System - Test Script

echo "Running AMAS Intelligence System Tests..."

# Activate virtual environment
source venv/bin/activate

# Run complete system test
python test_complete_system.py

echo "Tests completed!"
"""

    with open("run_tests.sh", "w") as f:
        f.write(test_script)
    os.chmod("run_tests.sh", 0o755)

    logger.info("Created startup scripts: start_dev.sh, run_tests.sh")


def main():
    """Main setup function"""
    logger.info("Setting up AMAS Intelligence System with Virtual Environment...")
    logger.info("=" * 70)

    try:
        # Step 1: Create virtual environment
        logger.info("Step 1: Creating virtual environment...")
        if not create_virtual_environment():
            logger.error("Failed to create virtual environment")
            sys.exit(1)

        # Step 2: Install requirements
        logger.info("Step 2: Installing requirements...")
        if not install_requirements():
            logger.error("Failed to install requirements")
            sys.exit(1)

        # Step 3: Create activation scripts
        logger.info("Step 3: Creating activation scripts...")
        create_activation_scripts()

        # Step 4: Create startup scripts
        logger.info("Step 4: Creating startup scripts...")
        create_startup_scripts()

        # Summary
        logger.info("=" * 70)
        logger.info("SETUP COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)
        logger.info("✅ Virtual environment created")
        logger.info("✅ Requirements installed")
        logger.info("✅ Activation scripts created")
        logger.info("✅ Startup scripts created")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Activate virtual environment:")
        if os.name == "nt":
            logger.info("   Windows: activate_venv.bat")
        else:
            logger.info("   Unix/Linux: source activate_venv.sh")
        logger.info("2. Start Docker services: docker-compose up -d")
        logger.info("3. Run tests: ./run_tests.sh")
        logger.info("4. Start system: ./start_dev.sh")
        logger.info("")
        logger.info("🎉 AMAS Intelligence System is ready!")

    except Exception as e:
        logger.error(f"Setup failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
