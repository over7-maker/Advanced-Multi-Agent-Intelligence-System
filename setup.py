#!/usr/bin/env python3
"""
AMAS Setup Script
Complete installation and configuration for AMAS
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "data",
        "data/collective_knowledge",
        "data/personalities", 
        "data/models",
        "data/predictions",
        "data/auth",
        "data/audit",
        "data/sessions",
        "config",
        "config/security",
        "web",
        "web/src",
        "web/src/components",
        "web/public",
        "tests",
        "tests/unit",
        "tests/integration",
        "tests/load"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies"""
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")

def setup_environment():
    """Setup environment configuration"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("📝 Created .env file from .env.example")
        print("⚠️  Please edit .env and add your API keys")
    else:
        print("📝 .env file already exists")

def setup_web_dashboard():
    """Setup React dashboard"""
    web_dir = Path("web")
    if not web_dir.exists():
        print("📁 Creating web dashboard...")
        web_dir.mkdir(exist_ok=True)
    
    # Create package.json if it doesn't exist
    package_json = web_dir / "package.json"
    if not package_json.exists():
        package_content = """{
  "name": "amas-dashboard",
  "version": "1.0.0",
  "description": "AMAS Control Dashboard",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0",
    "lucide-react": "^0.290.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}"""
        package_json.write_text(package_content)
        print("📝 Created package.json for React dashboard")

def run_security_scan():
    """Run security scan"""
    return run_command("python scripts/security-scan.sh", "Running security scan")

def validate_environment():
    """Validate environment setup"""
    return run_command("python scripts/validate_env.py", "Validating environment")

def main():
    """Main setup function"""
    print("🚀 AMAS Setup - Advanced Multi-Agent Intelligence System")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    # Setup environment
    print("\n⚙️ Setting up environment...")
    setup_environment()
    
    # Setup web dashboard
    print("\n🎨 Setting up web dashboard...")
    setup_web_dashboard()
    
    # Run security scan
    print("\n🔒 Running security scan...")
    run_security_scan()
    
    # Validate environment
    print("\n🔍 Validating environment...")
    validate_environment()
    
    print("\n🎉 AMAS Setup Complete!")
    print("=" * 60)
    print("📋 Next Steps:")
    print("1. Edit .env file and add your API keys")
    print("2. Run: python scripts/validate_env.py")
    print("3. Start AMAS: python -m amas")
    print("4. Open dashboard: cd web && npm install && npm start")
    print("\n🚀 Your AMAS system is ready!")

if __name__ == "__main__":
    main()