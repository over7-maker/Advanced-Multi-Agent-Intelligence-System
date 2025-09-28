#!/usr/bin/env python3
"""
Start Local GitHub Actions Runner
Quick start script for the local GitHub Actions environment
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("❌ Not in a git repository! Please run from your project root.")
        return False
    
    # Check if .github/workflows exists
    if not os.path.exists('.github/workflows'):
        print("❌ No .github/workflows directory found!")
        return False
    
    # Check if Python is available
    try:
        subprocess.run([sys.executable, '--version'], check=True, capture_output=True)
        print("✅ Python is available")
    except:
        print("❌ Python is not available!")
        return False
    
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements_local.txt'
        ], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_runner():
    """Start the local GitHub Actions runner"""
    print("🚀 Starting Local GitHub Actions Runner...")
    
    try:
        subprocess.run([sys.executable, 'local_github_actions.py'])
    except KeyboardInterrupt:
        print("\n👋 Shutting down Local GitHub Actions Runner...")
    except Exception as e:
        print(f"❌ Error starting runner: {e}")

def main():
    """Main entry point"""
    print("🤖 Local GitHub Actions Runner Setup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Start the runner
    start_runner()

if __name__ == "__main__":
    main()