"""
Setup script for AMAS Intelligence System
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    try:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "data",
        "evidence",
        "sandbox",
        "backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Created directory: {directory}")

def main():
    """Main setup function"""
    print("Setting up AMAS Intelligence System...")
    
    # Create directories
    create_directories()
    
    # Install requirements
    install_requirements()
    
    print("Setup completed successfully!")
    print("You can now run: python test_system.py")

if __name__ == "__main__":
    main()