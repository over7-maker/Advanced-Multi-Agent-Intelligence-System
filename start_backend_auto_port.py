#!/usr/bin/env python3
"""
Start backend server on an available port
Automatically finds a free port if 8000 is in use
"""

import socket
import subprocess
import sys
from pathlib import Path

def find_free_port(start_port=8000, max_attempts=10):
    """Find a free port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    return None

def main():
    """Start backend server"""
    # Try port 8000 first
    port = find_free_port(8000)
    
    if port is None:
        print("❌ Could not find an available port (tried 8000-8009)")
        sys.exit(1)
    
    if port != 8000:
        print(f"⚠️  Port 8000 is in use, using port {port} instead")
    else:
        print(f"✅ Port {port} is available")
    
    print(f"\n🚀 Starting AMAS Backend Server on port {port}...")
    print(f"   Access: http://localhost:{port}")
    print(f"   Docs: http://localhost:{port}/docs")
    print(f"   Health: http://localhost:{port}/health")
    print("\nPress Ctrl+C to stop\n")
    
    # Start uvicorn
    project_root = Path(__file__).parent
    cmd = [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", str(port)
    ]
    
    try:
        subprocess.run(cmd, cwd=project_root)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()

